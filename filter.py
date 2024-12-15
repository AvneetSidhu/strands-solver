def filter_wordList(path, output_file):
    with open("enable.txt", "r") as f:
        words = f.readlines()
    
    long_words = [word.strip() for word in words if len(word.strip()) >= 6]

    with open(output_file, 'w') as f:
        for word in long_words:
            f.write(word + '\n')
    
filter_wordList('enable.txt', 'filtered.txt')