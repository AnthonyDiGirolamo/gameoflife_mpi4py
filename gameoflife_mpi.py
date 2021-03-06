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

def game_of_life(grid):
    """
    Calculate the next game of life iteration for the passed in ndarray
    Source http://www.loria.fr/~rougier/teaching/numpy/numpy.html#the-way-of-numpy
    """

    # create a new array with the count of the neigbors of the previous iteration
    N = (grid[0:-2,0:-2] + grid[0:-2,1:-1] + grid[0:-2,2:] +
         grid[1:-1,0:-2]                   + grid[1:-1,2:] +
         grid[2:  ,0:-2] + grid[2:  ,1:-1] + grid[2:  ,2:])

    # if we have thee neighbors and the current cell is dead, give birth
    birth = (N==3) & (grid[1:-1,1:-1] == 0)
    # if we have 2 or 3 neighbors and the current cell is alive, stay alive
    survive = ((N==2) | (N==3)) & (grid[1:-1,1:-1] == 1)
    # zero out every cell
    grid[...] = 0
    # set surviving cells and birthed cells
    grid[1:-1,1:-1][birth | survive] = 1

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Game of Life MPI 1.0')

    size = MPI.COMM_WORLD.Get_size()
    rank = MPI.COMM_WORLD.Get_rank()

    if rank == 0:
        print(arguments)

    # global size of the image / starting array
    grid_size = numpy.array([16, 16])

    if arguments['random']:
        grid_size = [int(arguments['--rows']), int(arguments['--columns'])]
        if rank == 0:
            image = pygame.Surface(grid_size)
            # load the pygame surface as an array
            image_array1 = pygame.surfarray.pixels3d( image )
            # cast to int instead of int8
            image_array1 = image_array1.astype(int)
            # Randomly set pixel values
            it = numpy.nditer(image_array1, flags=['multi_index'], op_flags=['readwrite'])
            while not it.finished:
               x = it.multi_index[0]
               y = it.multi_index[1]
               color_index = it.multi_index[2]
               if (color_index == 1):
                   image_array1[x][y][color_index] = 255 if random.random() > 0.85 else 0
               it.iternext()

    elif arguments['image']:
        if rank == 0:
            # load an image
            image = pygame.image.load( arguments['FILENAME'] )
            grid_size[0] = image.get_size()[0]
            grid_size[1] = image.get_size()[1]
            # load the pygame surface as an array
            image_array1 = pygame.surfarray.pixels3d( image )
            # cast to int instead of int8
            image_array1 = image_array1.astype(int)

            # screen = pygame.display.set_mode( grid_size )
            # pygame.display.set_caption("Rank {}".format(rank))
            # pygame.init()
            # pygame.surfarray.blit_array(screen, image_array1)
            # pygame.display.flip()
            # time.sleep(10)

        # Let every process know the global grid size
        MPI.COMM_WORLD.Bcast(grid_size, root=0)
    else:
        # Should not ever get here
        MPI.Finalize()

    processor_grid_size = [size, 1]
    # processor_grid_size = MPI.Compute_dims(size, 2)
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

    file_type = MPI.INT.Create_subarray(grid_size, local_size, start_indices).Commit()
    # MPI_Type_create_subarray(2, grid_size, local_size, start_indices, MPI_ORDER_C, MPI_CHAR, &filetype);
    # MPI_Type_commit(&filetype);

    mem_size = [local_size[0] + 2, local_size[1] + 2]
    start_indices = [1, 1]

    mem_type = MPI.INT.Create_subarray(mem_size, local_size, start_indices).Commit()
    # MPI_Type_create_subarray(2, mem_size, local_size, start_indices, MPI_ORDER_C, MPI_CHAR, &memtype);
    # MPI_Type_commit(&memtype);

    NORTH = 0
    SOUTH = 1
    EAST  = 2
    WEST  = 3
    neighbors = [0, 0, 0, 0]

    neighbors[NORTH], neighbors[SOUTH] = communicator.Shift(0, 1)
    neighbors[EAST],  neighbors[WEST]  = communicator.Shift(1, 1)
    print("Rank {} Neighbors: North:{} South:{} East:{} West:{}".format(rank, *neighbors))

    # # Initialize the pygame window
    # if rank == 0:
    #     # create the pygame window
    #     screen = pygame.display.set_mode( grid_size )
    #     pygame.init()
    #     # load the pygame surface as an array
    #     image_array1 = pygame.surfarray.pixels3d( image )
    #     # cast to int instead of int8
    #     image_array1 = image_array1.astype(int)
    #     # setting the borders to red
    #     image_array1[0, :] = [255, 0, 0]
    #     image_array1[grid_size[0]-1, :] = [255, 0, 0]
    #     image_array1[:, 0] = [255, 0, 0]
    #     image_array1[:, grid_size[1]-1] = [255, 0, 0]
    #     # ouput to the screen
    #     pygame.surfarray.blit_array(screen, image_array1)
    #     pygame.display.flip()

    # allocate a local array
    local_array = numpy.zeros(local_size, int)
    mem_array = numpy.zeros(mem_size, int)
    mem_array[1:-1, 1:-1] = rank+1

    if rank == 0:
        # does this always allocate a new contiguous array?
        global_grid = numpy.array((image_array1[:,:,1:2] / 255).reshape((image_array1.shape[0], image_array1.shape[1])))
        # print("Rank {} Global Grid Shape {} \n{}".format(rank, global_grid.shape, global_grid))
    else:
        global_grid = numpy.zeros([0], int)

    # communicator.Scatter( [global_grid, 1, file_type], [local_array, mem_type], root=0 )

    # This is transposing the data for some reason
    # communicator.Scatter( global_grid, local_array, root=0 )

    # manually distribute data with send and recvs
    if rank == 0:
        # get rank 0's copy
        local_array = global_grid[0:local_size[0],:]

        # send rank 1 and up their copy
        for node in range(1, size):
            this_processor_grid_coords = communicator.Get_coords(node)
            this_start_indices = [this_processor_grid_coords[0] * local_size[0], this_processor_grid_coords[1] * local_size[1]]
            print("{} {}".format(node, this_start_indices))
            communicator.Send(global_grid[this_start_indices[0]:this_start_indices[0]+local_size[0],:].copy(), node)
    else:
        communicator.Recv(local_array, source=0)

    mem_array[1:-1, 1:-1] = local_array

    print("Rank {} Array Shape {} \n{}".format(rank, mem_array.shape, mem_array))
    sys.stdout.flush()

    # recreate the pygame window
    image = pygame.Surface( mem_size )
    screen = pygame.display.set_mode( mem_size )
    # load the pygame surface as an array
    image_array1 = pygame.surfarray.pixels3d( image )
    # cast to int instead of int8
    image_array1 = image_array1.astype(int)

    # copy mem_array into the image array
    image_array1[:,:,1:2] = numpy.expand_dims(mem_array, axis=2) * 255

    # it = numpy.nditer(image_array1, flags=['multi_index'], op_flags=['readwrite'])
    # while not it.finished:
    #    x = it.multi_index[0]
    #    y = it.multi_index[1]
    #    color_index = it.multi_index[2]
    #    if (color_index == 1):
    #        image_array1[x][y][color_index] = mem_array[x,y] * 255
    #    it.iternext()

    # for pixel in numpy.nditer(image_array1, flags=['external_loop'], op_flags=['readwrite']):
    #     pixel[...] = [0, 255 if random.random() > 0.85 else 0, 0]

    # ouput to the screen
    pygame.display.set_caption("Rank {}".format(rank))
    pygame.init()
    pygame.surfarray.blit_array(screen, image_array1)
    pygame.display.flip()

    # Done with the setup, sleep and wait for everyone to catch up
    time.sleep(20)
    communicator.barrier()

    for i in range( int(arguments['--iterations']) ):
        # Send my top row to my north neighbor, receive my bottom ghost row from my south neighbor
        communicator.Sendrecv(sendbuf=mem_array[1, :], dest=neighbors[NORTH], source=neighbors[SOUTH], recvbuf=mem_array[-1, :])

        # Send my bottom row to my sour neighbor, receive my top ghost row from my north neighbor
        communicator.Sendrecv(sendbuf=mem_array[-2, :], dest=neighbors[SOUTH], source=neighbors[NORTH], recvbuf=mem_array[0, :])

        # # Send my left column to my east neighbor, receive my right ghost column from my west neighbor
        # left_column          = numpy.array(mem_array[1:-1, 1].transpose())
        # received_left_column = numpy.zeros(mem_size[0]-2, int)
        # communicator.Sendrecv(sendbuf=left_column, dest=neighbors[EAST], source=neighbors[WEST], recvbuf=received_left_column)
        # mem_array[1:-1, 0] = received_left_column.transpose().copy()

        # copy the left column to the right column
        mem_array[1:-1, 0] = mem_array[1:-1, -2]

        # # Send my right column to my west neighbor, receive my left ghost column from my east neighbor
        # right_column          = numpy.array(mem_array[1:-1, -2].transpose())
        # received_right_column = numpy.zeros(mem_size[0]-2, int)
        # communicator.Sendrecv(sendbuf=right_column, dest=neighbors[WEST], source=neighbors[EAST], recvbuf=received_right_column)
        # mem_array[1:-1, -1] = received_right_column.transpose().copy()

        # copy the right column to the left column
        mem_array[1:-1, -1] = mem_array[1:-1, 1]

        # run game of life
        game_of_life(mem_array)

        # mem_array[1:-1, 1:-1] = rank+1

        # copy mem_array into the image array
        image_array1[:,:,1:2] = numpy.expand_dims(mem_array, axis=2) * 255
        pygame.surfarray.blit_array(screen, image_array1)
        pygame.display.flip()

        # if rank == 0:
        #     print("Rank {} Global Grid Shape {} \n{}".format(rank, global_grid.shape, global_grid))

    # print("Rank {} Array \n{}".format(rank, local_array))
    # sys.stdout.flush()

    # copy back to local_array
    # local_array = mem_array[1:-1, 1:-1].copy()
    # free the local_array
    # import gc
    # gc.collect()
    # print("Rank {} Array Shape {} \n{}".format(rank, local_array.shape, local_array))
    # sys.stdout.flush()
    # gather to the root
    # communicator.Gather( local_array, global_grid, root=0 )

    MPI.Finalize()
