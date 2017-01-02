from tkinter import *
from tkinter import messagebox
from threading import Thread
import time
from random import randint          
from collections import Counter
from copy import deepcopy

#utility functions
def get_runnable(func):
    return lambda : Thread(target=func).start()

def add_before_after(before, func, after):
    def f():
        before()
        to_ret = func()
        after()
        return to_ret

    return f

def set_button_color(button, color):
    button.config(bg=color)

def get_button_color(button):
    return button.cget('bg')

def flatten(lists):
    return [item for sublist in lists for item in sublist]

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


class ColorFlood:
    
    colors = ['white', 'red', 'blue', 'yellow', 'green', 'black']

    def __init__(self, num_rows, num_cols):
        self.reset_game(num_rows, num_cols)

    def reset_game(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.nodes = [[self.getRandomColor() for i in range(num_cols)] for j in range(num_rows)]
        self.counts = Counter(flatten(self.nodes))
        self.num_tiles = num_cols * num_rows
        self.turns = 0
        self.game_finished = False
        
    def getRandomColor(self):
        return ColorFlood.colors[randint(0,len(ColorFlood.colors)-1)]

    def get_captured_nodes(self):
        color = self.nodes[0][0]

        def dfs(i, j, visited):
            visited.add((i,j))
            toRet = []
            if self.nodes[i][j] == color:
                toRet.append((i,j))
                for row,col in get_neighbors(i,j,self.nodes):
                    if not (row, col) in visited:
                        toRet.extend(dfs(row, col, visited))

            return toRet

        return dfs(0, 0, set([]))

    def get_new_state(self, color):
        new_nodes = self.nodes[:]
        new_counts = dict(self.counts)
        
        captured_nodes = self.get_captured_nodes()
        new_counts[color] += len(captured_nodes)
        new_counts[self.nodes[0][0]] -= len(captured_nodes)

        for i,j in captured_nodes:
            new_nodes[i][j] = color

        return (new_nodes, new_counts)

    def apply_move(self, color):
        self.turns += 1
        self.nodes, self.counts = self.get_new_state(color)
        if self.counts[color] == self.num_tiles:
            self.game_finished = True
        
        return self.game_finished

class GameView:
    def __init__(self, cellSize, game, rootView):
        screenWidth  = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        self.cellWidth = cellSize
        self.cellHeight = round(self.cellWidth * screenHeight/screenWidth)
        self.frame = Frame(rootView) #create a new frame, as a child of root
        self.frame.pack() #make the frame visible
        self.game = game
        self.buttons = []
        self.controls = []
        self.players = None
        self.draw_interface()

    def draw_interface(self):
        for i in range(game.num_rows):
            f = Frame(self.frame)
            f.pack()
            self.buttons.append(list())
            for j in range(game.num_cols):
                button = Button(f, bg=game.nodes[i][j], width=self.cellWidth, height=self.cellHeight, state=DISABLED)
                button.pack(side=LEFT)
                self.buttons[i].append(button)
        
        f = Frame(self.frame,pady=20)
        f.pack()

        for color in ColorFlood.colors:
            button = Button(f, bg=color, width=self.cellWidth, height=self.cellHeight, activebackground=color)
            button.pack(side=LEFT)  
            self.controls.append(button)

        self.players = Frame(self.frame)
        self.players.pack(side=LEFT)

    def refresh(self):
        for i in range(game.num_rows):
            for j in range(game.num_cols):
                self.buttons[i][j].config(bg=game.nodes[i][j])




class GamePlayer:
    def __init__(self, gameView, gameState):
        self.gameView = gameView
        self.gameState = gameState

    def make_move(self, new_color):
        game_finished = self.gameState.apply_move(new_color)
        gameView.refresh()
        
        if game_finished:
            messagebox.showinfo('Congratulations', 'You won\nTurns taken = ' + str(game.turns))


class HumanPlayer(GamePlayer):
    def __init__(self, gameView, gameState):
        super(HumanPlayer, self).__init__(gameView, gameState)
        for button in gameView.controls:
            button.config(command=self.get_button_callback(button))


    def get_button_callback(self, button):
        return lambda : self.make_move(get_button_color(button))

class NonHumanPlayer(GamePlayer):
    def __init__(self, gameView, gameState, string):
        super(NonHumanPlayer, self).__init__(gameView, gameState)
        Button(gameView.players, text=string, command=get_runnable(self.play)).pack(side=LEFT)
        self.get_move = add_before_after(self.before_move, self.get_move, self.after_move)

    def before_move(self):      
        for control in gameView.controls:
            control.config(state=DISABLED)

    def after_move(self):
        for control in gameView.controls:
            control.config(state=NORMAL)
    
    def get_move(self):
        pass

    def play(self):
        while not self.gameState.game_finished:
            self.make_move(self.get_move())
            time.sleep(0.7)

class GreedyPlayer(NonHumanPlayer):
    def __init__(self, gameView, gameState):
        super(GreedyPlayer, self).__init__(gameView, gameState, 'Try Greedy')
        
    def get_move(self):
        num_nodes = 0
        best_color = ColorFlood.colors[0]
        nodes, counts = deepcopy(self.gameState.nodes), deepcopy(self.gameState.counts) 
        for color in ColorFlood.colors:
            temp_nodes, temp_counts = self.gameState.get_new_state(color)
            self.gameState.nodes, self.gameState.counts = temp_nodes, temp_counts
            temp = self.gameState.get_captured_nodes()
            if len(temp) >= num_nodes:
                best_color = color
                num_nodes = len(temp)
            self.gameState.nodes, self.gameState.counts = deepcopy(nodes), deepcopy(counts)
        return best_color


root = Tk() #'root' gui element
game = ColorFlood(8, 10)
gameView = GameView(5, game, root)
player = HumanPlayer(gameView, game)
greedyPlayer = GreedyPlayer(gameView, game)

root.mainloop()
root.destroy()