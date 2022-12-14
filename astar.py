from os import startfile
import pygame
import math
from queue import PriorityQueue

#displaying and setting up the game
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE= (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
#Building the main visualising tool
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.width = width 
        self.total_rows = total_rows

    #Using the row & column to define the position (similar to excel)
    def get_pos(self):
        return self.row, self.col
    #If it's closed, it is now red, hence you cannot visit RED
    def is_closed(self):
        return self.color == RED
    def is_open(self):
        return self.color == GREEN
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == ORANGE
    def is_end(self):
        return self.color == PURPLE
    def reset(self):
        self.color = WHITE
    def make_closed(self):
        self.color = RED
    def make_open(self):
        self.color = GREEN
    def make_start(self):
        self.color = ORANGE
    def make_barrier(self):
        self.color = BLACK
    def make_end(self):
        self.color = TURQUOISE
    def make_path(self):
        self.color = PURPLE
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        #DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])
        #UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])
        #RIGHT 
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col + 1])
        #LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col - 1]) 


    #less than
    def __lt__(self, other):
        return False

#the heuristic, h
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1 - y2)

#basically keeps drawing each node according to the last came_from path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


#see 1hr 24 mins to see summary of how this works, https://www.youtube.com/watch?v=JtiK0DOeI4A&t=221s
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    #put is the priority queue term for push
    #0 is f score, count is so if they have same f-score, it'll go with initial node, and then the start
    open_set.put((0, count, start))
    came_from = {}
    #the simple way of doing a loop in a loop "for...row"
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    #it's the heuristic of the start to the end node
    f_score[start] = h(start.get_pos(), end.get_pos())
    #keeps track of what is in the priority queue, it merely mirrors the list
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        #taking just the node from the priority queue, which always returns the minimum value
        current = open_set.get()[2]
        #syncs the priority queue and the current set
        open_set_hash.remove(current)

        #If we're at the end, that means we've found the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        #so if path not found, consider the neighbours of the current node
        for neighbour in current.neighbours:
            #calculate their temp g_score
            temp_g_score = g_score[current] + 1

            #if is less than current g_score, then update the table because this is the better option
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                #add them into the open set hash if not inside yet
                if neighbour not in open_set_hash:
                    count+= 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw()

        if current != start:
            current.make_closed()
    
    return False

#creating the grid 
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

#creating horizontal and vertical lines for the grids
def draw_grid(win, rows, width):
    gap = width // rows
    #horizontal lines
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        #vertical lines
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y//gap
    col = x//gap
    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None 
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #if left mouse click
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
                
            #if right mouse click
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                #to clear the whole game
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()

main(WIN, WIDTH)