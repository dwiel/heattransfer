"""
very very very rudimentary proof of concept
"""

import sys
import math
import pygame
pygame.init() 

#create the screen
window = pygame.display.set_mode((640, 480)) 

#draw it to the screen
pygame.display.flip() 

backgroundColor = (0,0,0)

#input handling (somewhat boilerplate code):
i = 0
while True: 
  
  window.fill(backgroundColor)
  #pygame.draw.line(window, (255, 255, 255), (320, 240), (320 + math.cos(i/10000.) * 100, 480 + math.sin(i/10000.)*100))
  
  pygame.draw.rect(window, (255, 0, 0), pygame.Rect(10, 10, 90, 90))

  #draw it to the screen
  pygame.display.update() 

  i += 1
  
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
      sys.exit(0) 
    else: 
      print event 
