#!/usr/bin/env python
# coding: utf-8

import math
import numpy
import pygame
import time
import random
random.seed()

import pprint
pp = pprint.PrettyPrinter(indent=4, width=110).pprint

# import pdb

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

# create a blank image

# grid_size = [512, 384]
# image = pygame.Surface(grid_size)

# load an image
# image = pygame.image.load("glidergun.bmp")
image = pygame.image.load("Conways_game_of_life_breeder.bmp")
grid_size = image.get_size()

# set the window size
screen = pygame.display.set_mode( grid_size )
# create the pygame window
pygame.init()

image_array1 = pygame.surfarray.pixels3d( image )

# Randomly set pixel values
# for pixel in numpy.nditer(image_array1, flags=['external_loop'], op_flags=['readwrite']):
#     pixel[...] = [0, 255 if random.random() > 0.85 else 0, 0]

image_array1 = image_array1.astype(int)

# setting the borders to red
image_array1[0, :] = [255, 0, 0]
image_array1[grid_size[0]-1, :] = [255, 0, 0]
image_array1[:, 0] = [255, 0, 0]
image_array1[:, grid_size[1]-1] = [255, 0, 0]

pygame.surfarray.blit_array(screen, image_array1)
pygame.display.flip()

time.sleep(5)

def game_of_life(grid):
    """
    Calculate the next game of life iteration for the passed in ndarray
    Source http://www.loria.fr/~rougier/teaching/numpy/numpy.html#the-way-of-numpy
    """

    # create a new array with the count of the neigbors of the previous iteration
    N = (grid[0:-2,0:-2,1:2] + grid[0:-2,1:-1,1:2] + grid[0:-2,2:,1:2] +
         grid[1:-1,0:-2,1:2]                       + grid[1:-1,2:,1:2] +
         grid[2:  ,0:-2,1:2] + grid[2:  ,1:-1,1:2] + grid[2:  ,2:,1:2])

    # if we have thee neighbors and the current cell is dead, give birth
    birth = (N==(255*3)) & (grid[1:-1,1:-1,1:2] < 255)
    # if we have 2 or 3 neighbors and the current cell is alive, stay alive
    survive = ((N==(255*2)) | (N==(255*3))) & (grid[1:-1,1:-1,1:2] == 255)
    # zero out every cell
    grid[...] = 0
    # set surviving cells and birthed cells
    grid[1:-1,1:-1,1:2][birth | survive] = 255


for i in range(2400):
    # Print the array with ascii
    # it = numpy.nditer(image_array1, flags=['multi_index'], op_flags=['readwrite'])
    # while not it.finished:
    #    x = it.multi_index[0]
    #    y = it.multi_index[1]
    #    color_index = it.multi_index[2]
    #    if (color_index == 1):
    #        print "#" if image_array1[x][y][color_index] == 255 else ".",
    #        if x == grid_size[0]-1:
    #            print("")
    #    it.iternext()

    game_of_life(image_array1)

    pygame.surfarray.blit_array(screen, image_array1)
    # screen.blit(image, (0,0))
    pygame.display.flip()
