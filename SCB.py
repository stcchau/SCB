import random
from Parser import Parser

class SCB:
    def __init__(self, lexicon):
        self.lexicon = lexicon
        self.parser = Parser(lexicon)
        self.q_word = ['who', 'what', 'when', 'where' 'why', 'how']
        self.ends = ['.', '!', '?']

    def sentence_type(self, words):  # determines sentence type
        if words[0] in self.q_word:
            return 'question', 'open'
        elif words[0] == 'BE':
            return 'question', 'closed'
        else:
            return 'statement', ' '

    def respond(self, words, q_type):
        words = words.split()
        responses = []
        if q_type == 'open':
            if words[0] == 'BE' and ' '.join(words[1:]) in self.lexicon:
                keys = list(self.lexicon[' '.join(words[1:])].keys())
                for key in keys:
                    if key.split()[0] == words[0]:
                        responses.append(' '.join(key.split()[1:]))
            elif ' '.join(words) in self.lexicon:
                keys = list(self.lexicon[' '.join(words)].keys())
                for key in keys:
                    responses.append(key)
        elif q_type == 'closed':
            responses.append('yes')
        if len(responses) > 0:
            print(random.choice(responses))
        else:
            print('i do not know')

    def read(self, sentence):
        tokens = self.parser.tokenize(sentence)
        if len(tokens) <= 2:
            return
        sent_type, q_type = self.sentence_type(tokens)

        subjects, predicate = self.parser.divide(tokens)

        if sent_type == 'question':
            self.respond(predicate, q_type)
        else:
            p = predicate.split()
            for subject in subjects:
                self.lexicon[subject][predicate] = {}
                if p[0] != 'BE':
                    self.lexicon[predicate][subject] = {}
