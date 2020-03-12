import math


class Parser:  # simplifies sentence string into array of tokens
    def __init__(self, lexicon):
        self.lexicon = lexicon
        self.verb_prob = {}
        self.poss_prons = ['mine', 'yours', 'his', 'hers', 'ours', 'yours', 'theirs']
        self.poss_adjs = ['my', 'your', 'his', 'her', 'its', 'our', 'your', 'their']
        self.to_be = ['am', 'are', 'is', 'was', 'were', 'been', 'being']
        self.arts = ['a', 'an', 'the']
        self.q_word = ['who', 'what', 'when', 'where' 'why', 'how']
        self.ends = ['.', '!', '?']

    def normal_distr(self, sigma, mu, x):
        return (-(x - mu) ** 2) / ((2 * sigma) ** 2) - math.log(sigma * math.sqrt(2 * math.pi))

    def update_verb_probs(self, words):
        sigma = math.sqrt(len(words) / 2)
        mu = (2 + (sigma - 1)) * 0.75
        for i in range(len(words)):
            if words[i] == 'BE':
                mu = i
                break
        delta = (mu * (8 / 3)) / (len(words) - 1)
        for i in range(len(words)):
            if words[i] not in self.verb_prob:
                self.verb_prob[words[i]] = [self.normal_distr(sigma, mu, delta * i), 1]
            else:
                self.verb_prob[words[i]][0] = (self.verb_prob[words[i]][0] * self.verb_prob[words[i]][
                    1] + self.normal_distr(sigma, mu, delta * i)) / (self.verb_prob[words[i]][1] + 1)
                self.verb_prob[words[i]][1] += 1

    def update_lexicon(self, tokens):  # adds new information into the lexicon
        for token in tokens:
            if token not in self.lexicon and token != 'BE' and token not in self.poss_adjs + self.poss_prons  + self.arts + self.q_word:
                self.lexicon[token] = {}

    def tokenize(self, sentence):  # simplifies sentence into word array

        for end in self.ends:  # converts sentence string to word array
            sentence = sentence.replace(end, ' ')
        sentence = sentence.lower()
        tokens = sentence.split()

        i = 0
        while i < len(tokens):  # conjugates to-be verbs and switches point of view
            if tokens[i] == 'you':
                tokens[i] = 'i'
            elif tokens[i] == 'i':
                tokens[i] = 'you'
            elif tokens[i] in self.to_be:
                tokens[i] = 'BE'
            elif tokens[i] == 'my':
                tokens[i] = 'your'
            elif tokens[i] == 'your':
                tokens[i] = 'my'
            i += 1

        self.update_lexicon(tokens)

        return tokens

    def divide(self, tokens):
        temp = tokens
        temp = ' '.join(temp)
        for word in self.poss_adjs + self.poss_prons  + self.arts + self.q_word:
            temp = temp.replace(' ' + word + ' ', ' ')
        temp = temp.split()
        self.update_verb_probs(temp)
        verb = temp[0]
        for i in range(len(temp)):
            if self.verb_prob[temp[i]][0] > self.verb_prob[verb][0]:
                verb = temp[i]
            if temp[i] == 'BE':
                verb = temp[i]
                break
        verb_index = tokens.index(verb)
        subjects = self.subject_list(tokens[:verb_index])
        predicate = ' '.join(tokens[verb_index:])
        print('Subject:', ' '.join(tokens[:verb_index]))
        print('Predicate:', ' '.join(tokens[verb_index:]))
        if predicate.split()[0] != 'BE':
            self.update_lexicon([predicate])
        return subjects, predicate

    def subject_list(self, subject):  # returns list of all subjects in need of association

        subject_list = [' '.join(subject)]
        if len(subject) > 1:
            if subject[0] in self.poss_adjs:
                subject_list.append(subject[0] + ' ' + subject[-1])

        self.update_lexicon(subject_list)

        return subject_list

    def reduce_predicate(self, predicate):
        for i in range(len(predicate)):
            if predicate[i] in self.arts:
                pass