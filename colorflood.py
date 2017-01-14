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

def get_call_all(funcs):
    def f():
        return [func() for func in funcs]

    return f


class ColorFlood:
    
    colors = ['white', 'red', 'blue', 'yellow', 'green']

    def __init__(self, num_rows, num_cols):
        self.reset_game(num_rows, num_cols)

    def reset_game(self, num_rows, num_cols, nodes=None):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.nodes = nodes
        
        if self.nodes is None:
            self.nodes = [[self.getRandomColor() for i in range(num_cols)] for j in range(num_rows)]
        
        self.nodes_init = deepcopy(self.nodes)
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
        self.all_buttons = []
        self.draw_interface()

    def draw_interface(self):
        for i in range(self.game.num_rows):
            f = Frame(self.frame)
            f.pack()
            self.buttons.append(list())
            for j in range(self.game.num_cols):
                button = Button(f, bg=game.nodes[i][j], width=self.cellWidth, height=self.cellHeight, state=DISABLED)
                button.pack(side=LEFT)
                self.buttons[i].append(button)
        
        f = Frame(self.frame,pady=20)
        f.pack()

        for color in ColorFlood.colors:
            button = Button(f, bg=color, width=self.cellWidth, height=self.cellHeight, activebackground=color)
            button.pack(side=LEFT)  
            self.controls.append(button)

        self.players = Frame(self.frame, padx=10, pady=10)
        self.players.pack()
        func = get_call_all([lambda : self.game.reset_game(self.game.num_rows, self.game.num_cols, self.game.nodes_init), self.refresh])
        b = Button(self.frame, pady=10, text='Reset Game', command=func)        
        b.pack()
        self.all_buttons.extend(self.controls)
        self.all_buttons.append(b)

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
        b = Button(gameView.players, text=string, command=get_runnable(self.play))
        gameView.all_buttons.append(b)
        b.pack(side=LEFT)
    
    # rates colors according to the length of captured nodes. useful for various players
    def get_color_score(self, color):
        nodes, counts = deepcopy(self.gameState.nodes), deepcopy(self.gameState.counts) # copy old values
        self.gameState.nodes, self.gameState.counts = self.gameState.get_new_state(color) # update
        captured_nodes = self.gameState.get_captured_nodes()
        self.gameState.nodes, self.gameState.counts = nodes, counts # reset old values
        return len(captured_nodes)

    def before_play(self):
        for control in gameView.all_buttons:
            control.config(state=DISABLED)

    def after_play(self):
        for control in gameView.all_buttons:
            control.config(state=NORMAL)
    
    def get_move(self):
        pass

    def play(self):
        self.before_play()
        
        while not self.gameState.game_finished:
            self.make_move(self.get_move())
            time.sleep(0.7)
        
        self.after_play()




class GreedyPlayer(NonHumanPlayer):
    def __init__(self, gameView, gameState):
        super(GreedyPlayer, self).__init__(gameView, gameState, 'Try Greedy')
    
    def get_moves(self):
        moves = []
        nodes, counts = deepcopy(self.gameState.nodes), deepcopy(self.gameState.counts)
        while all(count < self.gameState.num_tiles for color,count in self.gameState.counts.items()):
            color = self.get_move()
            moves.append(color)
            self.gameState.nodes, self.gameState.counts = self.gameState.get_new_state(color)

        self.gameState.nodes, self.gameState.counts = nodes, counts
        
        return moves[::-1] 

    def get_move(self):
        score, color = max((self.get_color_score(color), color) for color in ColorFlood.colors)
        return color

class OptimalPlayer(NonHumanPlayer):
    def __init__(self, gameView, gameState, max_depth):
        super(OptimalPlayer, self).__init__(gameView, gameState, 'Try Optimal Strategy')
        self.moves = None
        self.max_depth = max_depth

    def get_move(self):
        nodes, counts = deepcopy(self.gameState.nodes), deepcopy(self.gameState.counts) 
             

        # performs dfs
        def get_moves(nodes, counts, num_moves, min_moves):
            #self.gameView.refresh()
            if any(count == self.gameState.num_tiles for color, count in counts.items()):
                return (num_moves, [])
            
            colors_on_board = len([color for color, count in counts.items() if count > 0])
            if num_moves + colors_on_board > min_moves: # performed num_moves already and need atleast colors_on_board moves more 
                return (float('inf'), [])
                
            else:
                # moves stored in reverse order
                moves = []
                for color in ColorFlood.colors:
                    num_captured_ndoes = len(self.gameState.get_captured_nodes())
                    new_nodes, new_counts = self.gameState.get_new_state(color)
                    self.gameState.nodes, self.gameState.counts = deepcopy(new_nodes), deepcopy(new_counts)
                    if len(self.gameState.get_captured_nodes()) > num_captured_ndoes: # otherwise we end up getting cycles
                        new_num_moves, temp_moves = get_moves(new_nodes, new_counts, num_moves + 1, min_moves)
                        if new_num_moves <= min_moves:
                            min_moves = new_num_moves
                            moves = temp_moves
                            moves.append(color)
                    
                    self.gameState.nodes, self.gameState.counts = deepcopy(nodes), deepcopy(counts)
                
                if moves == []: # no strategy found
                    return (float('inf'), [])
                else:
                    return (min_moves, moves)


        
        if self.moves is None:
            # perform iterative deepening
            for i in range(1, self.max_depth + 1):
                print('assuming there exists a strategy of ', i)
                num_moves, self.moves = get_moves(nodes, counts, 0, i)
                if self.moves:
                    break
                else:
                    print('no such strategy exists: ', num_moves)
            print('found optimal strategy')
        if self.moves:
            return self.moves.pop()



root = Tk() #'root' gui element
game = ColorFlood(8, 8)
gameView = GameView(5, game, root)
player = HumanPlayer(gameView, game)
greedyPlayer = GreedyPlayer(gameView, game)
optimalPlayer = OptimalPlayer(gameView, game, len(greedyPlayer.get_moves()))

root.mainloop()
root.destroy()