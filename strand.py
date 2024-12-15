import pickle 
import tkinter as tk
from tkinter import messagebox

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

# board = ["EIRDFR",
#          "VNOVIE",
#          "OTETED", 
#          "IGSSTE", 
#          "OGIOAR", 
#          "TESENP", 
#          "NNISPR", 
#          "ITYOPU"]

pathU = set()
resU = set()

def span_left_to_right(path):
    start = False
    end = False
    for i in range(8):
        if (i, 0) in path:
            start = True
        if (i, 5) in path:
            end = True
    return start and end

def span_top_to_bottom(path):
    start = False
    end = False

    for i in range(6):
        if (0, i) in path:
            start = True
        if (7, i) in path:
            end = True
    return start and end

answers = {}

def dfsU(r, c, node, word, board): 
    if (r < 0 or r == len(board) or c < 0 or c == len(board[0]) or (r,c) in pathU or board[r][c].lower() not in node.children):
        return
    pathU.add((r,c))
    word += board[r][c].lower()
    node = node.children[board[r][c].lower()]
    if node.end and (span_left_to_right(pathU) or span_top_to_bottom(pathU)):
        resU.add(word)
        answers[word] = pathU.copy()
    dfsU(r - 1, c, node, word, board)  # Up
    dfsU(r + 1, c, node, word, board)  # Down
    dfsU(r, c + 1, node, word, board)  # Right
    dfsU(r, c - 1, node, word, board)  # Left
    dfsU(r - 1, c - 1, node, word, board)  # Top-left diagonal
    dfsU(r - 1, c + 1, node, word, board)  # Top-right diagonal
    dfsU(r + 1, c - 1, node, word, board)  # Bottom-left diagonal
    dfsU(r + 1, c + 1, node, word, board)  # Bottom-right diagonal
    pathU.remove((r,c))

ROWS = 8 
COLS = 6

grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

main = tk.Tk()
main.title("Strands Solver")

def solve():
    board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            letter = grid[r][c].get().strip()
            if not letter:
                messagebox.showerror("Input Error")
            else:
                row.append(letter.upper())
        board.append(row)
    
    for i in range(len(board)):
        for j in range(len(board[0])):
            dfsU(i,j,loaded_trie,"", board)
    populate_listbox(answers)

def move_focus(event, row, col):
    if len(event.widget.get()) == 1:
        next_col = col + 1
        next_row = row

        if next_col == COLS:
            next_col = 0
            next_row = row + 1
        
        if next_row < ROWS:
            grid[next_row][next_col].focus_set()

def handle_backspace(event, row, col):
    if event.widget.get() == "":
        if col > 0:
            prev_col, prev_row = col - 1, row
        elif row > 0:
            prev_col, prev_row = COLS - 1, row - 1
        else:
            return

        grid[prev_row][prev_col].focus_set()
        grid[prev_row][prev_col].delete(0, tk.END)
    else:
        event.widget.delete(0, tk.END)

def create_board():
    for r in range(ROWS):
        for c in range(COLS):
            entry = tk.Entry(main, width = 2, font=("Arial", 18), justify="center")
            entry.grid(row = r, column = c, padx=2, pady=2)
            entry.bind("<KeyRelease>", lambda event, row=r, col=c: move_focus(event, row, col))
            entry.bind("<Right>", lambda event, row=r, col=c: move_focus_by_arrow(event, row, col))
            entry.bind("<Left>", lambda event, row=r, col=c: move_focus_by_arrow(event, row, col))
            entry.bind("<Down>", lambda event, row=r, col=c: move_focus_by_arrow(event, row, col))
            entry.bind("<Up>", lambda event, row=r, col=c: move_focus_by_arrow(event, row, col))
            entry.bind("<BackSpace>", lambda event, row = r, col = c: handle_backspace(event, row, col))
            grid[r][c] = entry

def move_focus_by_arrow(event, row, col):
    if event.keysym == "Right":
        next_col, next_row = (col + 1) % COLS, row + (col + 1) // COLS
    elif event.keysym == "Left":
        next_col, next_row = (col - 1) % COLS, row - 1 if col == 0 else row
    elif event.keysym == "Down":
        next_row, next_col = (row + 1) % ROWS, col
    elif event.keysym == "Up":
        next_row, next_col = (row - 1) % ROWS, col
    else:
        return

    if 0 <= next_row < ROWS and 0 <= next_col < COLS:
        grid[next_row][next_col].focus_set()

def populate_listbox(answers):
    for solution in answers.keys():
        listbox.insert(tk.END, solution)

def handle_selection(event):
    selected_index = listbox.curselection()
    if selected_index:
        selected_solution = listbox.get(selected_index)
        print(f"Selected solution: {selected_solution}")
        color_solution(selected_solution)

def color_solution(word):
    for i in range(8):
        for j in range(6):
            grid[i][j].config(bg="white")

    for coordinate in answers[word]:
        grid[coordinate[0]][coordinate[1]].config(bg="green")


tk.Label(main, text="Enter board")
create_board()

solve = tk.Button(main, text = 'Solve', command = solve, font= ("Arial", 14))
solve.grid(row=ROWS, column = 0, columnspan = COLS, pady = 10)

listbox = tk.Listbox(main, height=15, width=20)
listbox.grid(row=0, column=COLS + 1, rowspan=ROWS, padx=10, pady=5, sticky="n")

# Add a Scrollbar to the Listbox
scrollbar = tk.Scrollbar(main, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=COLS + 2, rowspan=ROWS, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)

# Bind the Listbox selection to the handle_selection function
listbox.bind("<<ListboxSelect>>", handle_selection)

main.mainloop()