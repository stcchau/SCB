from SCB import SCB

lexicon = {}

scb = SCB(lexicon)

sentence = input()
while sentence != 'abc':
    if sentence == '1':
        print(scb.lexicon)
    elif sentence == '2':
        print(scb.parser.verb_prob)
    elif sentence == '3':
        data = open('data.txt').read().split('\n')
        for line in data:
            scb.read(line)
    else:
        scb.read(sentence)
    sentence = input()
