from tkinter import *
from tkinter import messagebox
from threading import Thread
import time
from random import randint			

colors = ['white', 'red', 'blue', 'yellow', 'green', 'black']
counts = {color:0 for color in colors}
numCols = 10
numRows = 8
numTiles = numCols * numRows
turns = 0
GAME_WON = 1
controls = []

def getRandomColor():
	global colors
	return colors[randint(0,len(colors)-1)]

def get_button_callback(button):
	return lambda : onButtonPress(button)

def onButtonPress(button):
	global turns
	turns += 1
	prevColor = get_node_color(grid[0][0])
	nodes = dfs(0, 0, grid, set([]), prevColor)
	newColor = get_node_color(button)
	if updateColor(nodes, newColor) == GAME_WON:
		messagebox.showinfo('Congratulations', 'You won\nTurns taken = ' + str(turns))

def updateColor(nodes, newColor):
	global counts
	for node in nodes:
		counts[get_node_color(node)] -= 1
		counts[newColor] += 1
		set_node_color(node, newColor)
	if counts[newColor] == numTiles:
		return GAME_WON

def set_node_color(node, color):
	node.config(bg=color)

def get_node_color(node):
	return node.cget('bg')

def get_neighbors(i, j, grid):
	neighbors = []
	if i-1 >= 0:
		neighbors.append((i-1, j))
	if i+1 < len(grid):
		neighbors.append((i+1, j))
	if j-1 >= 0:
		neighbors.append((i, j-1))
	if j+1 < len(grid[0]):
		neighbors.append((i, j+1))

	return neighbors


def dfs(i,j, grid, visited, color):
	visited.add((i,j))
	toRet = []
	if get_node_color(grid[i][j]) == color:
		toRet.append(grid[i][j])
		for row,col in get_neighbors(i,j,grid):
			if not (row, col) in visited:
				toRet.extend(dfs(row, col, grid, visited, color))

	return toRet

def try_strategy(strategy):
	global controls
	for control in controls:
		control.config(state=DISABLED)
	if strategy == 'greedy':
		greedy()

	for control in controls:
		control.config(state=NORMAL)
def greedy():
	global grid, turns
	while True:
		captured_nodes = dfs(0,0,grid,set([]),get_node_color(grid[0][0]))  
		numNodes = 0
		bestColor = colors[0]
		for color in colors:
			updateColor(captured_nodes, color)
			temp = dfs(0,0,grid,set([]),color)
			if len(temp) >= numNodes:
				bestColor = color
				numNodes = len(temp)
		turns += 1
		if updateColor(captured_nodes, bestColor) == GAME_WON:
			messagebox.showinfo('Congratulations', 'You won\nTurns taken = ' + str(turns))
			break
		else:
			time.sleep(0.5)




root = Tk() #'root' gui element

f1 = Frame(root) #create a new frame, as a child of root
f1.pack() #make the frame visible


screenWidth  = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
cellWidth = 5
cellHeight = round(cellWidth * screenHeight/screenWidth)
grid = [[] for i in range(numRows)]

for i in range(numRows):
	f = Frame(f1)
	f.pack()
	for j in range(numCols):
		c = getRandomColor()
		b = Button(f, bg=c, width=cellWidth, height=cellHeight, state=DISABLED)
		counts[c] += 1
		b.pack(side=LEFT)
		grid[i].append(b)

f = Frame(f1,pady=20)
f.pack()

for color in colors:
	b = Button(f, bg=color, width=cellWidth, height=cellHeight, activebackground=color)
	b.config(command=get_button_callback(b))
	b.pack(side=LEFT)	
	controls.append(b)

# for auto-play
f = Frame(f1)
f.pack(side=LEFT)
strategies = ['greedy']

for strategy in strategies:
	b = Button(f, text='Try ' + strategy, command=lambda : Thread(target= lambda : try_strategy(strategy)).start())
	b.pack(side=LEFT)

root.mainloop()
root.destroy()