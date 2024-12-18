import pickle 

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

with open('enable.txt', 'r') as filtered:
    words = filtered.readlines()
    words_strip = [word.strip() for word in words]

root = TrieNode()

for word in words_strip:
    root.addWord(word)

with open("trie.pkl", 'wb') as f:
    pickle.dump(root, f)

