#!/usr/bin/env python

from heatflow import simulate

# heat_capacity in J/kg
# density in kg/L
materials = {
  'ceb' : {
    'heat_capacity' : 2000,
    'density' : 1.922,
  }, 'air' : {
    'heat_capacity' : 1000,
    'density' : 0.00129269,
  },
}

initial_indoor_temp = 60

# volume in cubic inches
masses = {
  'outside' : {
    'volume'   : 100000000000000,
    'temp'     : 40,
    'material' : 'air',
  }, 'pex' : {
    'volume'   : 12 * 12 * 12 * 12,
    'temp'     : initial_indoor_temp,
    'material' : 'ceb',
  }, 'inside' : {
    #'volume'   : 20 * 20 * 20 * 12 * 12 * 12,
    'volume'   : 100000000000000,
    'temp'     : initial_indoor_temp,
    'material' : 'air',
  }
}

connections = []

slice_thickness = 3
floor_thickness = 6
slices = int(floor_thickness / slice_thickness)
if slice_thickness * slices - floor_thickness > 0.01 :
  print "warning slices dont go into floor thickness evenly"

previous_mass = 'outside'
for i in range(slices) :
  name = 'floor%02d' % (i+1)
  masses[name] = {
    'volume'   : 400 * 144 * slice_thickness,
    'temp'     : initial_indoor_temp,
    'material' : 'ceb',
    'depth'    : i * slice_thickness
  }
  
  if i :
    thickness = slice_thickness
  else :
    thickness = slice_thickness/2.0
  connections.append({
    'masses'    : [previous_mass, name],
    'r-value'   : 0.25,
    'area'      : 400 * 144,
    'thickness' : thickness,
  })
  previous_mass = name

connections.append({
  'masses'    : [previous_mass, 'inside'],
  'r-value'   : 0.25,
  'area'      : 400 * 144,
  'thickness' : slice_thickness/2.0,
})

for c in connections :
  print c

constant_btu_sources = [
  #{
    #'name' : 'radiant floor',
    #'btu/hour'  : 5118, # 1500 W electric
    ##'btu/hour'  : 20000, # small fireplace
    ##'btu/hour'  : 50000, # medium fireplace
    ##'btu/hour'  : 110000, # medium/large fireplace
    #'mass' : masses['pex'],
##    'end_t' : 4,
  #}, {
    #'name' : 'general winter heat loss',
    #'btu/hour'  : -90000/24., # 20 F average day
    #'mass' : masses['pex'],
    #'end_t' : 0,
  #}
]

sensors = ['outside', 'pex']
for i in range(6) :
  sensors.append('floor%02d' % int(i/6. * slices + 1))
sensors.append('floor%02d' % int(6/6. * slices))
sensors.append('inside')

simulate(masses, materials, connections, constant_btu_sources, sensors, 0.0002, 1000)
