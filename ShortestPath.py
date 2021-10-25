import pygame
from queue import PriorityQueue

width = 800
pygame.init()
win = pygame.display.set_mode((width, width)) #win stands for window
pygame.display.set_caption("Shortest Path")

RED = (255, 0, 0)
GREEN = (0, 240, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (120, 0, 120)
ORANGE= (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node: #keeps track of the colour of the node so as to know its function
    def __init__(self,row,col,width,total_row):
        self.row = row
        self.col = col
        self.x = row*width #gives us the x co-ordinate of the node
        self.y = col*width
        self.color = WHITE #because initially all nodes are white 
        self.neighbours = []
        self.width = width
        self.total_rows = total_row

    def get_pos(self):
        return self.row, self.col

    def is_closed(self): #checks if the node has already been visited 
        return self.color == GREEN
    def is_open(self):
        return self.color == YELLOW
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == RED
    def is_end(self):
        return self.color == BLUE
    def make_closed(self):
        self.color = YELLOW
    def reset(self):
        self.color = WHITE
    def make_open(self):
        self.color = GREEN
    def make_start(self):
        self.color = RED
    def make_barrier(self):
        self.color = BLACK
    def make_end(self):
        self.color = BLUE
    def make_path(self):
        self.color = TURQUOISE

    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.width)) 
    def update_neighbours(self,grid):
        self.neighbours = []
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():#down
            self.neighbours.append(grid[self.row+1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():#up
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():#right
            self.neighbours.append(grid[self.row][self.col+1])

        if self.col>0 and not grid[self.row][self.col-1].is_barrier():#left
            self.neighbours.append(grid[self.row][self.col-1])


#making heurisitc function
def h(p1,p2): #calculates manhattan distance 
    x1,y1 = p1
    x2,y2 = p2
    return abs(x1-x2) + abs(y1-y2)
def reconstruct_path(came_from,current,draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()# making the open set
	open_set.put((0, count, start)) #used for appending, 0 is the fscore, count is used as a tiebreaker
	came_from = {}
	#making the g(n) and h(n) and finally the f(n)
	#putting all values infinty to begin with
	g_score = {node: float("inf") for row in grid for node in row} 
	g_score[start] = 0
	f_score = {node: float("inf") for row in grid for node in row} #fscore is the distance we guessed to reach to the end node 
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)#popping from the open 

		if current == end:#checking if we are at the goal state
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

                #exploring the neighbours
		for neighbour in current.neighbours:
			temp_g_score = g_score[current] + 1 
			#comparing g and f of neighbours for traversal

			if temp_g_score < g_score[neighbour]: #if a better way is found, we update the path
				came_from[neighbour] = current
				g_score[neighbour] = temp_g_score
				f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
				if neighbour not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbour], count, neighbour))
					open_set_hash.add(neighbour)
					neighbour.make_open() #it is open now, yet to be explored further 

		draw()

		if current != start:
			current.make_closed()

	return False #if the while loop fails to find a path, we return false meaning we did not find a path

def make_grid(rows,width):
    grid = [] 
    gap = width//rows #gives us width of each cube
    for i in range(rows):
        grid.append([])
        for j in range(rows):
             node = Node(i,j,gap,rows) # i and j are our rows and columns respectively 
             grid[i].append(node)
    return grid #grid is a 2-d list containing all the nodes 

def draw_grid(win,rows,width): #this function draws the lines in the window 
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY,(0,i*gap),(width, i*gap))
    for j in range(rows):
        pygame.draw.line(win, GREY,(j*gap,0),(j*gap,width))
        
def draw(win, grid,rows,width):
    win.fill(WHITE) 

    for row in grid:
        for node in row:
            node.draw(win) #draws a coloured cube depending on the function of the node 
    
    draw_grid(win,rows,width) #calling the function that draws the grid lines 
    pygame.display.update()

def click(pos, rows,width): #translates the mouse click position into a row column position so as to know the exact node which is being clicked 
    gap = width//rows
    y,x = pos
    row = y//gap
    col = x//gap
    return row,col


def main(win, width):
	rows = 40
	grid = make_grid(rows, width)

	start = None
	end = None

	run = True #loop control variable 
	while run: #main game loop 
		draw(win, grid, rows, width)
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: #if the x button is pressed then the program is stopped 
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = click(pos, rows, width)  # gets the clicked position 
				node = grid[row][col] 
				if not start and node != end: # this makes the starting position our first click
					start = node
					start.make_start()

				elif not end and node != start: #this makes the ending position our second click
					end = node
					end.make_end()

				elif node != end and node != start: #rest of our left clicks make barriers 
					node.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # on right clicking we can change the starting and ending points 
				pos = pygame.mouse.get_pos()
				row, col = click(pos, rows, width) # gets the clicked position 
				node = grid[row][col] 
				node.reset()
				if node == start: #enables us to clear our starting position
					start = None
				elif node == end: #enables us to clear our ending position
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end: #checks if we pressed the spacebar
					for row in grid:
						for node in row:
							node.update_neighbours(grid) #stores the possible neighbours of the node 

					algorithm(lambda: draw(win, grid, rows, width), grid, start, end) #lambda enables us to pass the draw function as an argument 

				if event.key == pygame.K_f: #this clears our screen on pressing the f key 
					start = None
					end = None
					grid = make_grid(rows, width)
                            
	pygame.quit()

main(win, width) 

            

            
