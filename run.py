from Parser import Parser

lexicon = {}

p = Parser()

sentence = input()
while sentence != 'bye':
    if sentence == '1':
        print(lexicon)
    elif sentence == '2':
        data = open('data.txt').read().split('\n')
        for line in data:
            print(p.S_tree(p.translate(line, lexicon), lexicon))
    else:
        print(p.S_tree(p.translate(sentence, lexicon), lexicon))
    sentence = input()
