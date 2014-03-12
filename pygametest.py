#!/usr/bin/env python
# coding: utf-8

import numpy
import pygame
import time
import pprint
pp = pprint.PrettyPrinter(indent=4, width=110).pprint

# def getPixelArray(filename):
#     try:
#         image = pygame.image.load(filename)
#     except pygame.error, message:
#         print "Cannot load image:", filename
#         raise SystemExit, message

#     return pygame.surfarray.array3d(image)
# def saveSurface(pixels, filename):
#     try:
#         surf = pygame.surfarray.make_surface(pixels)
#     except IndexError:
#         (width, height, colours) = pixels.shape
#         surf = pygame.display.set_mode((width, height))
#         pygame.surfarray.blit_array(surf, pixels)

#     pygame.image.save(surf, filename)

image = pygame.image.load("Passion_flower.jpg")

screen = pygame.display.set_mode([800,420])
pygame.init()
# screen.fill([0,0,0])
# screen.blit( image, (0, 0) )
# pygame.display.flip()

# time.sleep(2)

surf3d = pygame.surfarray.pixels3d( image )
pp(type(surf3d))

for xpx in xrange( len(surf3d) ):
    surf3d = pygame.surfarray.pixels3d( image )
    surf3d[ xpx][240] = [255, 255, 255]

del surf3d
screen.blit( image, (0,0))
pygame.display.flip()

time.sleep(2)

