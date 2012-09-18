"""
a tool to help understand how thermal mass affects the heat transfer through a wall
"""

"""
### these were helpful in getting started and for reference, but have been 
### refactored out at this point

def heatflow(R_material, inches, dt_f = 1, area = 144, hours = 24) :
  # area is passed in as square feet (convert to meters)
  area *= 0.092903 / 144.
  # cel to far
  dt_c = dt_f * 5/9.
  
  return 1/(R_material * inches * .17611) * dt_c * area * hours * 3.41214163

def degree_change(thermal_mass, btu) :
  # thermal mass in kJ
  liters = volume * 0.016377314814814813
  
  return btu / (liters * thermal_mass * 0.00094781712)
"""

import numpy as np
import types

def p_m(m) :
  # display a line of output showing properties of mass m

  m['btu/hour'] = min(abs(m['btu/hour_gain']), abs(m['btu/hour_loss']))
  print ' ',m['name'], '%.03f' % m['temp'], ':',
  print '%d btu/hour gain' % int(m['btu/hour_gain']), ':',
  print '%d btu/hour loss' % int(m['btu/hour_loss']), ':', 
  print '%d btu/hour delta' % int(m['btu/hour_gain'] - m['btu/hour_loss']),
  print

def simulate(model, tstep = 1, tmax = 10, method = 'tuple', accuracy = 'normal') :
  """
  simulate the heat transfer through model
  tstep is amount of time to progress at each iteration
  tmax is when the simulation will end
  method can be 'tuple' or 'normal', tuple is faster, but the code is harder
    to read, still haven't decided which version should be kept
  accuracy can be 'very low', 'low', 'normal' and 'high'
    low has been 2.5% off in the past
    normal has been 1.5% off in the past
    high t_ratio_limit has been 0.04% off in the past
    tstep is what really controls the accuracy, however the simulator
      periodically determines how accurate the tstep in this model is and will
      raise an error if falls outside of the accuracy bounds
  """
  masses               = model['masses']
  materials            = model['materials']
  connections          = model['connections']
  constant_btu_sources = model['constant_btu_sources']
  sensors              = model['sensors']
  
  # 0.25 t_ratio_limit has been 2.5% off in the past
  # 0.1  t_ratio_limit has been 1.5% off in the past
  # 0.01 t_ratio_limit has been 0.04% off in the past
  if accuracy == 'very low' :
    t_ratio_limit = 0.99
  elif accuracy == 'low' :
    t_ratio_limit = 0.25
  elif accuracy == 'normal' :
    t_ratio_limit = 0.1
  elif accuracy == 'high' :
    t_ratio_limit = 0.01
  else :
    raise Exception("unkown accuracy %s" % accuracy)
  
  # merge materials and masses; precompute thermal mass in btu
  for name, m in masses.iteritems() :
    mat = m.get('material')
    if mat :
      for k, v in materials[mat].iteritems() :
        m[k] = v
  
    # save the name if it isn't already
    m['name'] = m.get('name', name)
    
    # thermal mass in J / degree C
    m['thermal_mass'] = m['volume'] * 0.016377314814814813 * m['heat_capacity'] * m['density']
    # thermal mass in btu / degree C
    m['thermal_mass'] *= 0.00094781712
  
  # precompute connections
  for c in connections :
    c['btu_per_deg'] = 1/(c['r-value'] * c['thickness']) * c['area'] * tstep * 0.006944448691138999
    c['m1'] = masses[c['masses'][0]]
    c['m2'] = masses[c['masses'][1]]
    c['m1_temp_per_step_per_deg'] = c['btu_per_deg'] / c['m1']['thermal_mass']
    c['m2_temp_per_step_per_deg'] = c['btu_per_deg'] / c['m2']['thermal_mass']
  
  # precompute constant_btu_sources
  for b in constant_btu_sources :
    if isinstance(b['btu/hour'], types.FunctionType) :
      b['temp/step_fn'] = lambda t : (b['btu/hour'](t) * tstep) / b['mass']['thermal_mass']
      b['temp/step'] = b['temp/step_fn'](0)
    else :
      b['temp/step'] = (b['btu/hour'] * tstep) / b['mass']['thermal_mass']
  
  print 'number of masses:', len(masses)
  print 'number of connections:', len(connections)
  print 'tstep:', tstep
  
  # convert the data points necessary at each step into tuples so they can
  # be accesses more quickly.  Would otherwise need to index into dicts and
  # arrays which are fast, but not quite as fast.  roughly 15% speedup
  if method == 'tuple' :
    # add indicies to masses
    ts = [0] * len(masses)
    masses_i = [0] * len(masses)
    for i, m in enumerate(masses.itervalues()) :
      m['i'] = i
      ts[i] = m['temp']
      masses_i[i] = m
    
    cs = [(c['m1']['i'], c['m2']['i'], c['m1_temp_per_step_per_deg'], c['m2_temp_per_step_per_deg']) for c in connections]
    bs = [(b['mass']['i'], b['temp/step'], b.get('end_t', 9999999999)) for b in constant_btu_sources]
  
  t = 0
  
  # need to initialize temp/step since it is only calculated sometimes
  for b in constant_btu_sources :
    if b.get('temp/step_fn') :
      b['temp/step'] = b['temp/step_fn'](t)

  while t < tmax :
    # a sense step is a step that the sensors are activated and data is printed
    # we normally don't want to do at this every step
    sense_step = t - int(t) < tstep
    #sense_step = 1 # print every step
    #sense_step = 0 # don't print any steps
    
    # apply constant btu sources
    if method == 'tuple' :
      for ti, temp_step, end_t in bs :
        # skip sources whose end_t has past
        if t > end_t : continue
        
        # add a constant supply of heat into a mass
        ts[ti] += temp_step
    else :
      for b in constant_btu_sources :
        # skip sources whose end_t has past
        if t > b.get('end_t', 9999999999999) : continue
        
        b['mass']['temp'] += b['temp/step']
    
    # apply heat transfers
    if method == 'tuple' :
      for m1, m2, m1_temp_per_step_per_deg, m2_temp_per_step_per_deg in cs :
        t_diff = ts[m1] - ts[m2]
        
        ts[m1] -= m1_temp_per_step_per_deg * t_diff
        ts[m2] += m2_temp_per_step_per_deg * t_diff
    else :
      for c in connections :
        m1, m2 = c['m1'], c['m2']
        
        t_diff = m1['temp'] - m2['temp']
        
        m1['temp'] -= c['m1_temp_per_step_per_deg'] * t_diff
        m2['temp'] += c['m2_temp_per_step_per_deg'] * t_diff
    
    if sense_step :
      # pull out mass temperatures from array
      if method == 'tuple' :
        for i, temp in enumerate(ts) :
          masses_i[i]['temp'] = temp
      
      # calculate temp/step for use in the next set of steps
      for i, b in enumerate(constant_btu_sources) :
        if b.get('temp/step_fn') :
          b['temp/step'] = b['temp/step_fn'](t)
          bs[i] = (bs[i][0], b['temp/step'], bs[i][2])
      
      # make sure time steps are small enough
      # in order to ensure accuracy, temperatures should never change by more
      # than ratio of a temperature delta as determined by the accuracy
      max_temp_ratio = 0
      
      # we're going to sum btu/hour loss and gain for each mass, so
      # initialize with 0
      for m in masses.itervalues() :
        m['btu/hour_loss'] = 0
        m['btu/hour_gain'] = 0
      
      # for now, we only calculate btu movement through direct conduction, not
      # from constant heat sources
      for c in connections :
        m1 = c['m1']
        m2 = c['m2']
        
        btu = c['btu_per_deg'] * (m1['temp'] - m2['temp'])
        
        # calculate how many btu are passing through each material
        btu_p_tstep = btu / tstep
        if btu_p_tstep > 0 :
          # positive btu_p_tstep implies heat moving from m1 to m2
          m1['btu/hour_loss'] += btu_p_tstep
          m2['btu/hour_gain'] += btu_p_tstep
        else :
          # negative btu_p_tstep implies heat moving from m2 to m1
          # * -1 because we only care about magnitude, not direction, and the
          #   direction is negative
          m2['btu/hour_loss'] += btu_p_tstep * -1
          m1['btu/hour_gain'] += btu_p_tstep * -1

        # ensure we aren't moving to fast through the simulation
        temp_delta = m1['temp'] - m2['temp']
        if temp_delta :
          for diff in [btu / m1['thermal_mass'], btu / m2['thermal_mass']] :
            ratio = abs(diff / temp_delta)
            
            if ratio > max_temp_ratio :
              max_temp_ratio = ratio
            
            if ratio > t_ratio_limit :
              rec_tstep = tstep / (ratio / t_ratio_limit)
              #if auto_adjust_tstep :
                ## this doesn't work unless we can undo all of the previous steps
                #print 'reseting tstep to %s' % rec_tstep
                #return simulate(masses, materials, connections, constant_btu_sources, sensors, tstep = rec_tstep)
              raise Exception(("""
                timesteps are too large, temperature changed by %s due to delta
                temperature of %s in one timestep. timesteps are currently %f, 
                suggested timestep %f""" % (
                diff, m1['temp'] - m2['temp'], tstep, rec_tstep)
              ).replace('\n', '').replace('  ', ''))
        
      # display sensor values
      print '%02d:00' % int(t), '%.06f' % max_temp_ratio
      for sensor in sensors :
        p_m(masses[sensor])
      
    t += tstep
