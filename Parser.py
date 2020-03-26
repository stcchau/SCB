import math

class Parser:  # simplifies sentence string into array of tokens
    def __init__(self):
        self.poss_prons = ['mine', 'yours', 'his', 'hers', 'ours', 'yours', 'theirs']
        self.arts = ['a', 'an', 'the']
        self.poss_adjs = ['my', 'your', 'his', 'her', 'its', 'our', 'your', 'their']
        self.dems = ['this', 'that', 'these', 'those']
        self.dets = self.arts + self.poss_adjs + self.dems
        self.modals = ['can', 'may', 'must', 'shall', 'will', 'could', 'might', 'ought to', 'should', 'would']
        self.to_be = ['am', 'are', 'is', 'was', 'were']
        self.q_word = ['who', 'what', 'when', 'where' 'why', 'how']
        self.ends = '.?!'

    '''
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
    '''

    def update_scores(self, tokens, lexicon):
        for token in tokens:
            lexicon[token[0]][token[1]] -= 1
            lexicon[token[0]]['~'] += 1

    def update_lexicon(self, tokens, lexicon):  # adds new information into the lexicon
        for token in tokens:
            if token not in lexicon:
                lexicon[token] = {'determiner': 0, 'noun': 0, 'adverb': 0, 'adjective': 0, 'verb': 0, 'preposition': 0, '~': 1}

    def tokenize(self, sentence, lexicon):  # simplifies sentence into word array

        for end in self.ends:  # converts sentence string to token array
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

        self.update_lexicon(tokens, lexicon)

        return tokens

    def S_tree(self, tokens, lexicon):

        tree = []

        for i in range(1 if tokens[0] not in (self.poss_adjs + self.arts) else 2, len(tokens)):
            if tokens[i] in self.dets:
                pass
            else:
                sentence = [self.NP_tree(tokens[:i], lexicon), self.VP_tree(tokens[i:], lexicon)]
                score = sentence[0][0] + sentence[1][0]
                tree.append((score, [sentence[0][1], sentence[1][1]]))

        best_sentence_set = tree[0]
        for sentence_set in tree:
            if sentence_set[0] > best_sentence_set[0]:
                best_sentence_set = sentence_set

        return best_sentence_set[1]

    def NP_tree(self, tokens, lexicon):

        if len(tokens) == 1:
            score = lexicon[tokens[0]]['noun'] / lexicon[tokens[0]]['~']
            phrase = [(tokens[0], 'noun')]
            phrase_set = score, phrase
            return phrase_set

        tokens_length = len(tokens)
        tree = [[]]

        if tokens[0] in self.dets:
            tree[0].append((tokens[0], 'determiner'))
            tokens.pop(0)

        for i in range(len(tokens)):  # gives every possibility of POS of words
            for j in range(len(tree)):
                phrase = tree.pop(0)
                for POS in ['determiner', 'noun', 'preposition', 'adverb', 'adjective']:
                    if len(phrase) > 0:
                        if POS != 'noun' and len(phrase) == tokens_length - 1:  # only nouns are allowed at the end
                            pass
                        elif (POS == 'determiner' and tokens[i] not in self.dets) and (phrase[-1][1] != 'preposition'):  # determiners only come after prepositions
                            pass
                        elif (POS == 'noun' or POS == 'adjective') and phrase[-1][1] == 'noun':  # nouns are never followed by another noun or adjective
                            pass
                        elif POS == 'noun' and phrase[-1][1] == 'adverb':  # nouns cannot follow adverbs
                            pass
                        elif POS == 'adverb' and phrase[-1][1] == 'adjective':  # adverbs cannot follow adjectives
                            pass
                        elif POS == 'preposition' and (phrase[-1][1] != 'noun'):  # prepositions only come after nouns
                            pass
                        else:
                            tree.append(phrase + [(tokens[i], POS)])
                    elif POS == 'noun' or POS == 'adjective':
                        tree.append(phrase + [(tokens[i], POS)])
                if len(tree[-1]) == tokens_length:
                    score = 0
                    phrase = tree.pop(-1)
                    for tup in phrase:
                        score += lexicon[tup[0]][tup[1]] / lexicon[tup[0]]['~']
                    tree.append((score, phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def VP_tree(self, tokens, lexicon):

        if len(tokens) == 1:
            score = lexicon[tokens[0]]['verb'] / lexicon[tokens[0]]['~']
            phrase = [(tokens[0], 'verb')]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(1, len(tokens)):
            phrase = tokens[:i]
            phrase = [(phrase[j], 'adverb') for j in range(len(phrase) - 1)] + [(phrase[-1], 'verb')]
            score = 0
            for tup in phrase:
                score += lexicon[tup[0]][tup[1]] / lexicon[tup[0]]['~']
            np = self.NP_tree(tokens[i:], lexicon)
            tree.append((score + np[0], [phrase, np[1]]))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    '''
    def sentence(self, tokens, lexicon):
        string = '<S>' + '\n'
        parsable = False
        verb = 0
        for i in range(len(tokens)):
            if 'verb' in lexicon[tokens[i]] or tokens[i] == 'BE':
                verb = i
            elif (tokens[i] in self.dets or 'adjective' in lexicon[tokens[i]] or 'noun' in lexicon[tokens[i]]) and (i >= 2 and 'noun' in lexicon[tokens[i - 2]]):
                verb = i - 1
        if verb > 0:
            np = self.noun_phrase(tokens[:verb], lexicon, 1)
            vp = self.verb_phrase(tokens[verb:], lexicon, 1)
            if np[0] and vp[0]:
                string += np[1]
                string += vp[1]
                parsable = True
            string += '</S>'
        if not parsable:
            string = 'i cannot understand you'
        return string
    
    def noun_phrase(self, tokens, lexicon, indents):
        correct = True
        string = indents * '\t' + '<NP>' + '\n'
        i = 0
        if tokens[0] in self.dets:
            string += (indents + 1) * '\t' + 'Determiner:' + tokens.pop(0) + '\n'
        while len(tokens) > 0 and i < len(tokens):
            if ('adjective' in lexicon[tokens[i]] or 'noun' in lexicon[tokens[i]]) and i > 0:
                string += self.noun_description(tokens[:i], lexicon, indents)
                for j in range(len(tokens[:i])):
                    tokens.pop(0)
                    i -= 1
            elif 'noun' in lexicon[tokens[i]]:
                string += (indents + 1) * '\t' + 'Noun:' + tokens.pop(i) + '\n'
            elif len(tokens) == 1:
                lexicon[tokens[i]]['noun'] = {}
                print('learned noun:', tokens[i])
                tokens.pop(0)
            else:
                i += 1
        if len(tokens) > 0:
            correct = False
        string += indents * '\t' + '</NP>' + '\n'
        return correct, string
    
    def noun_description(self, tokens, lexicon, indents):
        string = ''
        lexicon[tokens[-1]]['adjective'] = {}
        print('learned adjective:', tokens[-1])
        if len(tokens) > 1:
            string += self.noun_description(tokens[:-1], lexicon, indents)
        string += (indents + 1) * '\t' + 'Adjective:' + tokens[-1] + '\n'
        return string

    def verb_phrase(self, tokens, lexicon, indents):
        correct = True
        string = indents * '\t' + '<VP>' + '\n'
        i = 0
        noun_found = False
        verb_found = False
        while len(tokens) > 0 and i < len(tokens):
            if tokens[i] in self.dets or 'noun' in lexicon[tokens[i]] or 'adjective' in lexicon[tokens[i]]:
                np = self.noun_phrase(tokens[i:], lexicon, indents + 1)
                if np[0]:
                    string += np[1]
                    noun_found = True
                for j in range(len(tokens[i:])):
                    tokens.pop(i)
                i = 0
            elif 'verb' in lexicon[tokens[i]]:
                string += (indents + 1) * '\t' + 'Verb:' + tokens.pop(i) + '\n'
                verb_found = True
            elif len(tokens) == 1:
                if noun_found and not verb_found:
                    lexicon[tokens[i]]['verb'] = {}
                    print('learned verb:', tokens[i])
                elif verb_found and not noun_found:
                    lexicon[tokens[i]]['noun'] = {}
                    print('learned noun:', tokens[i])
                else:
                    lexicon[tokens[i]]['adjective'] = {}
                    print('learned adjective:', tokens[i])
                tokens.pop(0)
            else:
                i += 1
        if len(tokens) > 0:
            correct = False
        string += indents * '\t' + '</VP>' + '\n'
        return correct, string

    def PP(self, tokens, lexicon, anchors, indents):
        pass
    '''