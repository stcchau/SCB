from Parser import Parser

lexicon = {}

p = Parser()

sentence = input()
while sentence != 'bye':
    if sentence == '1':
        print('Enter word:')
        print(lexicon[input()])
    elif sentence == '2':
        data = open('data.txt').read().split('\n')
        for line in data:
            p.display(p.S_tree(p.translate(line, lexicon), lexicon))
            print()
    else:
        p.display(p.S_tree(p.translate(sentence, lexicon), lexicon))
        print()
    sentence = input()
