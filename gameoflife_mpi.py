#!/usr/bin/env python

from mpi4py import MPI
import numpy
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4, width=110).pprint

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
# pp( "Hello from process {}/{}".format(rank, size) )

grid_size           = [1920, 1080]
processor_grid_size = MPI.Compute_dims(size, 2)
local_size          = [grid_size[0] / processor_grid_size[0] , grid_size[1] / processor_grid_size[1]]
remainder_size      = [grid_size[0] % processor_grid_size[0] , grid_size[1] % processor_grid_size[1]]

communicator = MPI.COMM_WORLD.Create_cart((processor_grid_size[0], processor_grid_size[1]), periods=(True, True), reorder=True)
rank = communicator.rank
processor_grid_coords = communicator.Get_coords(rank)

if (rank == 0):
    print("Grid Size:            [{}, {}]".format(grid_size[0], grid_size[1]))
    print("Processor Grid Size:  [{}, {}]".format(processor_grid_size[0], processor_grid_size[1]))
    print("Local Chunk Size:     [{}, {}]".format(local_size[0], local_size[1]))
    print("Remainder Chunk Size: [{}, {}]".format(remainder_size[0], remainder_size[1]))
    # sys.stdout.flush()

start_indices = [processor_grid_coords[0] * local_size[0], processor_grid_coords[1] * local_size[1]]
print("Rank {} location in Processor Grid: [{}, {}]  Starting Index: [{}, {}]".format(rank, processor_grid_coords[0], processor_grid_coords[1], start_indices[0], start_indices[1]))

NORTH = 0
SOUTH = 1
EAST  = 2
WEST  = 3
neighbors = [0, 0, 0, 0]

neighbors[NORTH], neighbors[SOUTH] = communicator.Shift(0, 1)
neighbors[EAST],  neighbors[WEST]  = communicator.Shift(1, 1)
print("Rank {} Neighbors: {} {} {} {}".format(rank, *neighbors))

