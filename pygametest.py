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

grid_size = [160, 120]
screen = pygame.display.set_mode( grid_size )
pygame.init()

image = pygame.Surface(grid_size)
image_array1 = pygame.surfarray.pixels3d( image )
image_array2 = pygame.surfarray.pixels3d( image )

for pixel in numpy.nditer(image_array1, flags=['external_loop'], op_flags=['readwrite']):
    pixel[...] = [0, 254 if random.random() > 0.75 else 0, 0]

pygame.surfarray.blit_array(screen, image_array1)
pygame.display.flip()

for i in range(200):
    it = numpy.nditer(image_array2, flags=['multi_index'], op_flags=['readwrite'])
    while not it.finished:
        x = it.multi_index[0]
        y = it.multi_index[1]
        color_index = it.multi_index[2]
        if (color_index == 1):
            # pp((x, y, color_index))
            total = 0
            total += image_array1[ x-1 ][ y-1 ][ color_index ]
            total += image_array1[ x-1 ][ y   ][ color_index ]
            if (y < grid_size[1]-1):
                total += image_array1[ x-1 ][ y+1 ][ color_index ]
            total += image_array1[ x   ][ y-1 ][ color_index ]
            if (y < grid_size[1]-1):
                total += image_array1[ x   ][ y+1 ][ color_index ]
            if (x < grid_size[0]-1):
                total += image_array1[ x+1 ][ y-1 ][ color_index ]
                total += image_array1[ x+1 ][ y   ][ color_index ]
                if (y < grid_size[1]-1):
                    total += image_array1[ x+1 ][ y+1 ][ color_index ]

            neighbors = int(total / 254)
            cell = image_array1[x][y][color_index]
            pp("old cell: {}, neighbors: {}, total: {}".format(cell, neighbors, total))
            new_cell = 0
            if (cell == 0):
                if (neighbors == 3):
                    new_cell = 1
            else:
                if (neighbors == 2 or neighbors == 3):
                    new_cell = 1
                elif (neighbors < 2 or neighbors > 3):
                    new_cell = 0

            it[0] = new_cell * 254
        it.iternext()

    pp("update")
    pygame.surfarray.blit_array(screen, image_array2)
    # screen.blit(image, (0,0))
    pygame.display.flip()

    image_array1, image_array2 = image_array2, image_array1

