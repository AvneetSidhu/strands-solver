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

def valid_moves(r,c,path):
    moves = [(1,0),(1,1),(0,1),(-1,0),(-1,1),(1,-1),(-1,-1),(0,-1)]
    valid = []
    for (x,y) in moves:
        if 0 <= r + x < ROWS and 0 <= c + y < COLS and (r + x, c + y) not in path:
            valid.append((r + x, c + y))
    return valid

def dfs(r, c, node, word, board, start, first_word_found = False): 
    if (r < 0 or r == len(board) or c < 0 or c == len(board[0]) or (r,c) in path or board[r][c].lower() not in node.children):
        return
    path.add((r,c))
    word += board[r][c].lower()
    node = node.children[board[r][c].lower()]
    if node.end:
        ends[word] = (r,c)
        starts[word] = start
        if not first_word_found:
            first_word_found = True
            new_search_positions = valid_moves(r, c, path)
            for (x, y) in new_search_positions:
                dfs(x,y, loaded_trie, word, board, start, first_word_found)
        if(span_left_to_right(path) or span_top_to_bottom(path)):
            span.add(word)
        else:
            res.add(word)

        if word not in answers:
            answers[word] = path.copy()
        elif span_left_to_right(path) or span_top_to_bottom(path):
            answers[word] = path.copy()

    dfs(r - 1, c, node, word, board, start, first_word_found)  # Up
    dfs(r + 1, c, node, word, board, start,first_word_found)  # Down
    dfs(r, c + 1, node, word, board, start,first_word_found)  # Right
    dfs(r, c - 1, node, word, board, start,first_word_found)  # Left
    dfs(r - 1, c - 1, node, word, board, start,first_word_found)  # Top-left diagonal
    dfs(r - 1, c + 1, node, word, board, start,first_word_found)  # Top-right diagonal
    dfs(r + 1, c - 1, node, word, board, start,first_word_found)  # Bottom-left diagonal
    dfs(r + 1, c + 1, node, word, board, start,first_word_found)  # Bottom-right diagonal
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
    populate_listbox()


def find_solution_combinations():
    return

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

def intersection(setA, setB):
    return setA.intersection(setB)

def populate_listbox():
    for solution in sorted(list(span))[::-1]:
        listbox.insert(tk.END, solution + " SPAN")

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