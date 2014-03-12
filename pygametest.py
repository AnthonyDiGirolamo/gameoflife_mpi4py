#!/usr/bin/env python
# coding: utf-8

import numpy
import pygame
import time
import random
random.seed()

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

# image = pygame.image.load("Passion_flower.jpg")

grid_size = [1440, 850]
screen = pygame.display.set_mode( grid_size )
pygame.init()

image = pygame.Surface(grid_size)
image_array1 = pygame.surfarray.pixels3d( image )
image_array2 = pygame.surfarray.pixels3d( image )

for pixel in numpy.nditer(image_array1, flags=['external_loop'], op_flags=['readwrite']):
    pixel[...] = [0, random.randint(0,1) * 255, 0]

pygame.surfarray.blit_array(screen, image_array1)

it = numpy.nditer(image_array2, flags=['multi_index'])
while not it.finished:
    total = image_array1[ it.multi_index[0]-1 ][ it.multi_index[1]-1 ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]-1 ][ it.multi_index[1]   ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]-1 ][ it.multi_index[1]+1 ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]   ][ it.multi_index[1]-1 ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]   ][ it.multi_index[1]+1 ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]+1 ][ it.multi_index[1]-1 ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]+1 ][ it.multi_index[1]   ][ it.multi_index[2] ] + image_array1[ it.multi_index[0]+1 ][ it.multi_index[1]+1 ][ it.multi_index[2] ]
    pp(total)
    # it[0] =
    it.iternext()

pygame.surfarray.blit_array(screen, image_array2)
# screen.blit(image, (0,0))
pygame.display.flip()
time.sleep(2)

