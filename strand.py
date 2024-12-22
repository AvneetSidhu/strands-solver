import pickle 
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import random
class TrieNode():
    def __init__(self):
        self.children = {}
        self.end = False
    
    def addWord(self, word):
        cur = self 
        for letter in word:
            if letter not in cur.children: 
                cur.children[letter] = TrieNode()
            cur = cur.children[letter]
        cur.end = True


with open("trie.pkl", "rb") as f:
    loaded_trie = pickle.load(f)


class App:

    def __init__(self):
        self.path = set()
        self.res = set()
        self.span = set()
        self.starts = {}
        self.ends = {}
        self.answers = {}
        self.usedColors = set()
        self.usedSpaces = set()
        self.ROWS = 8 
        self.COLS = 6
        self.grid = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.firstPick = True

    def span_left_to_right(self,path):
        start = False
        end = False
        for i in range(8):
            if (i, 0) in path:
                start = True
            if (i, 5) in path:
                end = True
        return (start and end)

    def span_top_to_bottom(self,path):
        start = False
        end = False

        for i in range(6):
            if (0, i) in path:
                start = True
            if (7, i) in path:
                end = True
        return start and end

    def valid_moves(self,r,c,path):
        moves = [(1,0),(1,1),(0,1),(-1,0),(-1,1),(1,-1),(-1,-1),(0,-1)]
        valid = []
        for (x,y) in moves:
            if 0 <= r + x < self.ROWS and 0 <= c + y < self.COLS and (r + x, c + y) not in path:
                valid.append((r + x, c + y))
        return valid

    def dfs(self,r, c, node, word, board, start, first_word_found = False): 
        if (r < 0 or r == len(board) or c < 0 or c == len(board[0]) or (r,c) in self.path or board[r][c].lower() not in node.children):
            return
        self.path.add((r,c))
        word += board[r][c].lower()
        node = node.children[board[r][c].lower()]
        if node.end:

            self.ends[word] = (r,c)
            self.starts[word] = start

            if not first_word_found:

                first_word_found = True

                new_search_positions = self.valid_moves(r, c, self.path)

                for (x, y) in new_search_positions:
                    self.dfs(x,y, loaded_trie, word, board, start, first_word_found)
                
                first_word_found = False

            if(self.span_left_to_right(self.path) or self.span_top_to_bottom(self.path)):
                self.span.add(word)
            else:
                if not first_word_found:
                    self.res.add(word)

            if word not in self.answers:
                self.answers[word] = self.path.copy()
            elif self.span_left_to_right(self.path) or self.span_top_to_bottom(self.path):
                self.answers[word] = self.path.copy()

        self.dfs(r - 1, c, node, word, board, start, first_word_found)  # Up
        self.dfs(r + 1, c, node, word, board, start,first_word_found)  # Down
        self.dfs(r, c + 1, node, word, board, start,first_word_found)  # Right
        self.dfs(r, c - 1, node, word, board, start,first_word_found)  # Left
        self.dfs(r - 1, c - 1, node, word, board, start,first_word_found)  # Top-left diagonal
        self.dfs(r - 1, c + 1, node, word, board, start,first_word_found)  # Top-right diagonal
        self.dfs(r + 1, c - 1, node, word, board, start,first_word_found)  # Bottom-left diagonal
        self.dfs(r + 1, c + 1, node, word, board, start,first_word_found)  # Bottom-right diagonal
        self.path.remove((r,c))

    def solve(self):
        board = []
        for r in range(self.ROWS):
            row = []
            for c in range(self.COLS):
                letter = self.grid[r][c].get().strip()
                if not letter:
                    messagebox.showerror("Input Error")
                else:
                    row.append(letter.upper())        
            board.append(row)
        
        for i in range(len(board)):
            for j in range(len(board[0])):
                start = (i, j)
                self.dfs(i,j,loaded_trie,"", board, start)
        self.populate_listbox(list(self.span))

    def move_focus(self,event, row, col):
        if len(event.widget.get()) == 1:
            next_col = col + 1
            next_row = row

            if next_col == self.COLS:
                next_col = 0
                next_row = row + 1
            
            if next_row < self.ROWS:
                self.grid[next_row][next_col].focus_set()

    def handle_backspace(self,event, row, col):
        if event.widget.get() == "":
            if col > 0:
                prev_col, prev_row = col - 1, row
            elif row > 0:
                prev_col, prev_row = self.COLS - 1, row - 1
            else:
                return

            self.grid[prev_row][prev_col].focus_set()
            self.grid[prev_row][prev_col].delete(0, tk.END)
        else:
            event.widget.delete(0, tk.END)

    def create_board(self):
        for r in range(self.ROWS):
            for c in range(self.COLS):
                entry = tk.Entry(main, width = 2, font=("Arial", 18), justify="center")
                entry.grid(row = r, column = c, padx=2, pady=2)
                entry.bind("<KeyRelease>", lambda event, row=r, col=c: self.move_focus(event, row, col))
                entry.bind("<Right>", lambda event, row=r, col=c: self.move_focus_by_arrow(event, row, col))
                entry.bind("<Left>", lambda event, row=r, col=c: self.move_focus_by_arrow(event, row, col))
                entry.bind("<Down>", lambda event, row=r, col=c: self.move_focus_by_arrow(event, row, col))
                entry.bind("<Up>", lambda event, row=r, col=c: self.move_focus_by_arrow(event, row, col))
                entry.bind("<BackSpace>", lambda event, row = r, col = c: self.handle_backspace(event, row, col))
                self.grid[r][c] = entry

    def move_focus_by_arrow(self,event, row, col):
        if event.keysym == "Right":
            next_col, next_row = (col + 1) % self.COLS, row + (col + 1) // self.COLS
        elif event.keysym == "Left":
            next_col, next_row = (col - 1) % self.COLS, row - 1 if col == 0 else row
        elif event.keysym == "Down":
            next_row, next_col = (row + 1) % self.ROWS, col
        elif event.keysym == "Up":
            next_row, next_col = (row - 1) % self.ROWS, col
        else:
            return

        if 0 <= next_row < self.ROWS and 0 <= next_col < self.COLS:
            self.grid[next_row][next_col].focus_set()

    def filter(self,currentList, selection):
        filtered = []
        self.usedSpaces = self.usedSpaces | self.answers[selection]
        for word in currentList:
            if not self.usedSpaces.intersection(self.answers[word]):
                filtered.append(word)
        return filtered

    def reset(self):
        self.populate_listbox(list(self.span))
        self.usedColors = set()
        self.usedSpaces = set()
        self.firstPick = True
        for i in range(8):
            for j in range(6):
                self.grid[i][j].config(bg="white")

    def populate_listbox(self, toShow):
        listbox.delete(0,'end')
        for solution in sorted(toShow[::-1]):
            listbox.insert(tk.END, solution)

    def handle_selection(self,event):
        # if self.firstPick: 
        #     self.populate_listbox(list(self.res))
        #     self.firstPick = False
        selected_index = listbox.curselection()
        if selected_index:
            selected_solution = listbox.get(selected_index)
            selected_solution = selected_solution.split(" ")[0]
            self.populate_listbox(self.filter(listbox.get(0, 'end'),selected_solution))
            print(f"Selected solution: {selected_solution}")
            self.color_solution(selected_solution)

    def generate_color(self):
        r = lambda: random.randint(0, 255)
        return f'#{r():02x}{r():02x}{r():02x}'

    def color_solution(self, word):
        random_color = self.generate_color()

        while random_color in self.usedColors:
            random_color = self.generate_color()

        for coordinate in self.answers[word]:
            self.grid[coordinate[0]][coordinate[1]].config(bg=random_color)

app = App()
main = tk.Tk()
main.title("Strands Solver")

tk.Label(main, text="Enter board")
app.create_board()

solve = tk.Button(main, text='Solve', command=app.solve, font=("Arial", 14))
solve.grid(row=app.ROWS, column=0, columnspan = app.COLS, pady=10)   

reset = tk.Button(main, text = 'Reset', command = app.reset, font = ("Arial", 14)) 
reset.grid(row = app.ROWS, column=3, columnspan = app.COLS, pady=10)

search = tk.Text()

listbox = tk.Listbox(main, height=15, width=20)
listbox.grid(row=0, column=app.COLS + 1, rowspan=app.ROWS, padx=10, pady=5, sticky="n")

scrollbar = tk.Scrollbar(main, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=app.COLS + 2, rowspan=app.ROWS, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)


listbox.bind("<<ListboxSelect>>", app.handle_selection)
main.mainloop()