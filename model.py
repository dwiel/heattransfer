#!/usr/bin/env python

from heatflow import simulate

# heat_capacity in J/kg
# density in kg/L
# r value in english per inch
materials = {
  'ceb' : {
    'heat_capacity' : 2000,
    'density' : 1.922,
    'rvalue' : 0.25,
  }, 'air' : {
    'heat_capacity' : 1000,
    'density' : 0.00129269,
  }, 'rice' : {
    'heat_capacity' : 2000,
    'density' : 0.144,
    'rvalue' : 3,
  }
}

initial_indoor_temp = 60

# volume in cubic inches
masses = {
  'outside' : {
    'volume'   : 10000000000000000,
    'temp'     : 40,
    'material' : 'air',
  }, 'pex' : {
    'volume'   : 12 * 12 * 12 * 12, # 12 cubic feet
    'temp'     : initial_indoor_temp,
    'material' : 'ceb',
  }, 'inside' : {
    'volume'   : 20 * 20 * 20 * 12 * 12 * 12,
    #'volume'   : 10000000000000000,
    'temp'     : initial_indoor_temp,
    'material' : 'air',
  }
}

connections = []
sensors = []

def make_wall(name, area, thickness, slice_thickness, material, surface1, surface2, initial_temp) :
  # area in square inches
  
  rvalue = materials[material]['rvalue']
  
  slices = int(thickness / slice_thickness)
  if slice_thickness * slices - thickness > 0.01 :
    print "warning slices dont go into floor thickness evenly"

  previous_mass = surface1
  for i in range(slices) :
    slice_name = name+'%02d' % (i+1)
    masses[slice_name] = {
      'volume'   : area * slice_thickness,
      'temp'     : initial_temp,
      'material' : material,
      'depth'    : i * slice_thickness
    }
    
    # the 2 masses on the edge have r-value thickness of half so that the sum
    # adds to the correct thickness.  Considering the case where there are only
    # 1, 2 or 3 layers in the mass helped me understand why this works
    if i :
      this_slice_thickness = slice_thickness
    else :
      this_slice_thickness = slice_thickness/2.0
    connections.append({
      'masses'    : [previous_mass, slice_name],
      'r-value'   : rvalue,
      'area'      : area,
      'thickness' : this_slice_thickness,
    })
    previous_mass = slice_name

  connections.append({
    'masses'    : [previous_mass, surface2],
    'r-value'   : rvalue,
    'area'      : area,
    'thickness' : slice_thickness/2.0,
  })

  #for i in range(int(thickness)) :
    #sensors.append(name+'%02d' % int(i/float(thickness) * slices + 1))
  #sensors.append(name+'%02d' % int(1 * slices))
  sensors.append(name+'%02d' % 1)
  sensors.append(name+'%02d' % (slices/2))
  sensors.append(name+'%02d' % slices)

make_wall('floor', 400 * 144, 6, 0.1, 'ceb', 'pex', 'inside', initial_indoor_temp)
for d in ['N', 'S', 'E', 'W'] :
  make_wall(d+' outside',    400 * 144, 6, 0.1,  'ceb',  'outside',         d+' insulation01', initial_indoor_temp)
  make_wall(d+' insulation', 400 * 144, 12, 0.2, 'rice', d+' outside60',    d+' inside01',     initial_indoor_temp)
  make_wall(d+' inside',     400 * 144, 6, 0.1,  'ceb',  d+' insulation60', 'inside',          initial_indoor_temp)

#connections.append({
  #'masses'    : ['inside', 'east wall inside'],
  #'r-value'   : 0.25,
  #'area'      : 17 * 23.5 * 144,
  #'thickness' : 6,
#})

#for c in connections :
  #print c

def sun_btu(t) :
  print 'sun', t
  h = t % 24
  if h >= 11 and h <= 17 :
    return 11000
  else :
    return 0

constant_btu_sources = [
  {
    'name' : 'radiant floor',
    'btu/hour' : 0,
    #'btu/hour'  : 51180, # 1500 W electric
    #'btu/hour'  : 20000, # small fireplace
    #'btu/hour'  : 50000, # medium fireplace
    #'btu/hour'  : 110000, # medium/large fireplace
    'mass' : masses['pex'],
    'end_t' : 4,
  },
  #{
    #'name' : 'general winter heat loss',
    #'btu/hour'  : -90000/24., # 20 F average day
    #'mass' : masses['pex'],
    ##'end_t' : ,
  #}
  {
    'name' : 'sun',
    #'btu/hour' : sun_btu,
    'btu/hour' : 0,
    'mass' : masses['floor60'],
  },
  {
    'name' : 'simple windows',
    'btu/hour' : -1700,
    'mass' : masses['inside'],
  }
]

sensors.append('outside')
sensors.append('pex')
#sensors.append('east wall inside')
sensors.append('inside')

print masses.keys()

simulate({
    'masses' : masses,
    'materials' : materials,
    'connections' : connections,
    'constant_btu_sources' : constant_btu_sources,
    'sensors' : sensors,
  }, tstep = 0.00008, tmax = 240
)
