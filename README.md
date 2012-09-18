heattransfer
============

Very simple heat transfer simulator

TODO:
  radiant & convective transfers
    need to tell make_wall to use convection sometimes
    also use convection to outside?
  use real temperature and sun data
  add windows/beams to model
  simple visualizer
  automatic timestep adjustments
    hard to do since you need to be able to undo steps if you go to fast

NOTES:

some good references:
  various heat transfer equations: http://ub.unibw-muenchen.de/dissertationen/ediss/ilgevicius-audrius/inhalt.pdf
  emissivity values for common materials: http://www.infrared-thermography.com/material-1.htm
  calculating radiant heat: http://www.engineeringtoolbox.com/radiation-heat-transfer-d_431.html
  heat transfer specifally for underfloor heating: http://en.wikipedia.org/wiki/Underfloor_heating
    Typically with underfloor heating the convective component is almost 50% of the total heat transfers
  calculating convective heat transfer: http://www.engineeringtoolbox.com/convective-heat-transfer-d_430.html