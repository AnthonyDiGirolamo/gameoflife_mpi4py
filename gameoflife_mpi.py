#!/usr/bin/env python
# coding: utf-8

"""Game of Life MPI

Usage:
  gameoflife_mpi.py [-i NUMBER] random [-r ROWS] [-c COLUMNS]
  gameoflife_mpi.py [--iterations=NUMBER] image FILENAME

Options:
  -h --help                      Show this screen.
  --version                      Show version.
  -r ROWS --rows=ROWS            Number of Rows [default: 640]
  -c COLS --columns=cols         Number of Columns [default: 480]
  -i NUMBER --iterations=NUMBER  Total iterations [default: 2400]

"""

from mpi4py import MPI
from docopt import docopt
import numpy
import sys
import pygame
import time
import random
random.seed()

# import pprint
# pp = pprint.PrettyPrinter(indent=4, width=110).pprint

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Game of Life MPI 1.0')

    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()

    # if rank == 0:
    #     print(arguments)

    grid_size = numpy.array([16, 16])

    if arguments['random']:
        grid_size = [int(arguments['--rows']), int(arguments['--columns'])]
        image = pygame.Surface(grid_size)
        # Randomly set pixel values
        # for pixel in numpy.nditer(image_array1, flags=['external_loop'], op_flags=['readwrite']):
        #     pixel[...] = [0, 255 if random.random() > 0.85 else 0, 0]

    elif arguments['image']:
        if rank == 0:
            # load an image
            image = pygame.image.load( arguments['FILENAME'] )
            grid_size[0] = image.get_size()[0]
            grid_size[1] = image.get_size()[1]
        MPI.COMM_WORLD.Bcast(grid_size, root=0)
    else:
        MPI.Finalize()

    if rank == 0:
        # create the pygame window
        screen = pygame.display.set_mode( grid_size )
        pygame.init()

        image_array1 = pygame.surfarray.pixels3d( image )
        image_array1 = image_array1.astype(int)

        # setting the borders to red
        image_array1[0, :] = [255, 0, 0]
        image_array1[grid_size[0]-1, :] = [255, 0, 0]
        image_array1[:, 0] = [255, 0, 0]
        image_array1[:, grid_size[1]-1] = [255, 0, 0]

        pygame.surfarray.blit_array(screen, image_array1)
        pygame.display.flip()

    processor_grid_size = MPI.Compute_dims(size, 2)
    local_size          = [grid_size[0] / processor_grid_size[0] , grid_size[1] / processor_grid_size[1]]
    remainder_size      = [grid_size[0] % processor_grid_size[0] , grid_size[1] % processor_grid_size[1]]

    communicator = MPI.COMM_WORLD.Create_cart(
        (processor_grid_size[0], processor_grid_size[1]),
        periods=(True, True),
        reorder=True)

    rank = communicator.rank
    processor_grid_coords = communicator.Get_coords(rank)

    if (rank == 0):
        print("Grid Size:            [{}, {}]".format(grid_size[0], grid_size[1]))
        print("Processor Grid Size:  [{}, {}]".format(processor_grid_size[0], processor_grid_size[1]))
        print("Local Chunk Size:     [{}, {}]".format(local_size[0], local_size[1]))
        print("Remainder Chunk Size: [{}, {}]".format(remainder_size[0], remainder_size[1]))
        sys.stdout.flush()

    communicator.barrier()

    start_indices = [processor_grid_coords[0] * local_size[0], processor_grid_coords[1] * local_size[1]]
    print("Rank {} location in Processor Grid: [{}, {}]  Starting Index: [{}, {}]".format(rank, processor_grid_coords[0], processor_grid_coords[1], start_indices[0], start_indices[1]))

    NORTH = 0
    SOUTH = 1
    EAST  = 2
    WEST  = 3
    neighbors = [0, 0, 0, 0]

    neighbors[NORTH], neighbors[SOUTH] = communicator.Shift(0, 1)
    neighbors[EAST],  neighbors[WEST]  = communicator.Shift(1, 1)
    print("Rank {} Neighbors: North:{} South:{} East:{} West:{}".format(rank, *neighbors))

    local_array = numpy.zeros(local_size, int)
    local_array[1:-1, 1:-1] = rank+1

    # Done with the setup, sleep and wait for everyone to catch up
    time.sleep(5)
    communicator.barrier()

    # print("Rank {} Array \n{}".format(rank, local_array))
    # sys.stdout.flush()

    # Send my top row to my north neighbor, receive my bottom ghost row from my south neighbor
    communicator.Sendrecv(sendbuf=local_array[1, :], dest=neighbors[NORTH], source=neighbors[SOUTH], recvbuf=local_array[-1, :])

    # Send my bottom row to my sour neighbor, receive my top ghost row from my north neighbor
    communicator.Sendrecv(sendbuf=local_array[-2, :], dest=neighbors[SOUTH], source=neighbors[NORTH], recvbuf=local_array[0, :])

    # Send my left column to my east neighbor, receive my right ghost column from my west neighbor
    left_column          = numpy.array(local_array[1:-1, 1].transpose())
    received_left_column = numpy.zeros(local_size[0]-2, int)
    communicator.Sendrecv(sendbuf=left_column, dest=neighbors[EAST], source=neighbors[WEST], recvbuf=received_left_column)
    local_array[1:-1, 0] = received_left_column.transpose()

    # Send my right column to my west neighbor, receive my left ghost column from my east neighbor
    right_column          = numpy.array(local_array[1:-1, -2].transpose())
    received_right_column = numpy.zeros(local_size[0]-2, int)
    communicator.Sendrecv(sendbuf=right_column, dest=neighbors[WEST], source=neighbors[EAST], recvbuf=received_right_column)
    local_array[1:-1, -1] = received_right_column.transpose()

    print("Rank {} Array \n{}".format(rank, local_array))
    sys.stdout.flush()

    MPI.Finalize()
