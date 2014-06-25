#!/usr/bin/env python
# coding: utf-8

"""Naval Fate.

Usage:
  naval_fate.py ship new <name>...
  naval_fate.py ship <name> move <x> <y> [--speed=<kn>]
  naval_fate.py ship shoot <x> <y>
  naval_fate.py mine (set|remove) <x> <y> [--moored | --drifting]
  naval_fate.py (-h | --help)
  naval_fate.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""
from mpi4py import MPI
import numpy
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4, width=110).pprint
from docopt import docopt

if __name__ == '__main__':
    # arguments = docopt(__doc__, version='Naval Fate 2.0')
    # print(arguments)

    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()

    grid_size           = [16, 16]
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
