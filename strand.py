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

path = set()
res = set()
span = set()
starts = {}
ends = {}
answers = {}

def span_left_to_right(path):
    start = False
    end = False
    for i in range(8):
        if (i, 0) in path:
            start = True
        if (i, 5) in path:
            end = True
    return (start and end)

def span_top_to_bottom(path):
    start = False
    end = False

    for i in range(6):
        if (0, i) in path:
            start = True
        if (7, i) in path:
            end = True
    return start and end

def possible_moves(r, c):

    directions = [
        (-1, 0),    # Up
        (1, 0),     # Down
        (0, -1),    # Left
        (0, 1),     # Right
        (-1, -1),   # Up-Left Diagonal
        (-1, 1),    # Up-Right Diagonal
        (1, -1),    # Down-Left Diagonal
        (1, 1)      
    ]

    valid_moves = set()
    for dr, dc in directions:
        new_r, new_c = r + dr, c + dc
        if 0 <= new_r < ROWS and 0 <= new_c < COLS:
            valid_moves.add((new_r, new_c))

    return valid_moves
    

def are_compoundable(wordA, wordB):
    if wordA == wordB:
        return False
    possible_starts = possible_moves(ends[wordA][0], ends[wordA][1])
    wordBPath = answers[wordB]
    if starts[wordB] in possible_starts:
        for coordinate in answers[wordA]:
            if coordinate in wordBPath:
                return False
        return True
    else:
        return False
    
def compound_words():
    for wordA in starts: #loop over all words
        for wordB in starts:
            if are_compoundable(wordA, wordB) and (span_left_to_right(answers[wordA] | answers[wordB]) or span_top_to_bottom(answers[wordA] | answers[wordB])):
                span.add(wordA + wordB) 
                answers[wordA + wordB] = answers[wordA] | answers[wordB]


def dfs(r, c, node, word, board, start): 
    if (r < 0 or r == len(board) or c < 0 or c == len(board[0]) or (r,c) in path or board[r][c].lower() not in node.children):
        return
    path.add((r,c))
    word += board[r][c].lower()
    node = node.children[board[r][c].lower()]
    if node.end:
        ends[word] = (r,c)
        starts[word] = start
        if(span_left_to_right(path) or span_top_to_bottom(path)):
            span.add(word)
        else:
            res.add(word)

        if word not in answers:
            answers[word] = path.copy()
        elif span_left_to_right(path) or span_top_to_bottom(path):
            answers[word] = path.copy()

    dfs(r - 1, c, node, word, board, start)  # Up
    dfs(r + 1, c, node, word, board, start)  # Down
    dfs(r, c + 1, node, word, board, start)  # Right
    dfs(r, c - 1, node, word, board, start)  # Left
    dfs(r - 1, c - 1, node, word, board, start)  # Top-left diagonal
    dfs(r - 1, c + 1, node, word, board, start)  # Top-right diagonal
    dfs(r + 1, c - 1, node, word, board, start)  # Bottom-left diagonal
    dfs(r + 1, c + 1, node, word, board, start)  # Bottom-right diagonal
    path.remove((r,c))

ROWS = 8 
COLS = 6

grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

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
            start = (i, j)
            dfs(i,j,loaded_trie,"", board, start)
    # compound_words()
    populate_listbox()
    

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

def populate_listbox():
    for solution in sorted(list(span), key = len)[::-1]:
        listbox.insert(tk.END, solution + " SPAN")
    
    for solution in sorted(list(res), key = len)[::-1]:
        listbox.insert(tk.END, solution)

def handle_selection(event):
    selected_index = listbox.curselection()
    if selected_index:
        selected_solution = listbox.get(selected_index)
        selected_solution = selected_solution.split(" ")[0]
        print(f"Selected solution: {selected_solution}")
        color_solution(selected_solution)

def color_solution(word):
    for i in range(8):
        for j in range(6):
            grid[i][j].config(bg="white")

    for coordinate in answers[word]:
        grid[coordinate[0]][coordinate[1]].config(bg="green")


main = tk.Tk()
main.title("Strands Solver")

tk.Label(main, text="Enter board")
create_board()

solve1 = tk.Button(main, text='Words', command=solve, font=("Arial", 14))
solve1.grid(row=ROWS, column=0, columnspan = COLS, pady=10)    

listbox = tk.Listbox(main, height=15, width=20)
listbox.grid(row=0, column=COLS + 1, rowspan=ROWS, padx=10, pady=5, sticky="n")

scrollbar = tk.Scrollbar(main, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=COLS + 2, rowspan=ROWS, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)


listbox.bind("<<ListboxSelect>>", handle_selection)
main.mainloop()