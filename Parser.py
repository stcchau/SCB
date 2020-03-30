import math
from queue import PriorityQueue as pq

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
        if type(tokens[0]) == tuple:
            for token in tokens:
                lexicon[token[0]][token[1]] += 1
                lexicon[token[0]]['~'] += 1
        else:
            for token in tokens:
                self.update_scores(token, lexicon)

    def update_lexicon(self, words, lexicon):  # adds new information into the lexicon
        for word in words:
            if word not in lexicon:
                lexicon[word] = {'determiner': 0, 'noun': 0, 'adverb': 0, 'adjective': 0, 'verb': 0, 'preposition': 0, '~': 1}

    def translate(self, sentence, lexicon):  # simplifies sentence into word array

        for end in self.ends:  # converts sentence string to token array
            sentence = sentence.replace(end, ' ')
        sentence = sentence.lower()
        words = sentence.split()

        i = 0
        while i < len(words):  # conjugates to-be verbs and switches point of view
            if words[i] == 'you':
                words[i] = 'i'
            elif words[i] == 'i':
                words[i] = 'you'
            elif words[i] in self.to_be:
                words[i] = 'BE'
            elif words[i] == 'my':
                words[i] = 'your'
            elif words[i] == 'your':
                words[i] = 'my'
            i += 1

        self.update_lexicon(words, lexicon)

        return words

    def S_tree(self, words, lexicon):

        tree = []

        for i in range(1 if words[0] not in (self.poss_adjs + self.arts) else 2, len(words)):
            if words[i] in self.dets:
                pass
            else:
                sentence = [self.NP_tree(words[:i], lexicon), self.VP_tree(words[i:], lexicon)]
                score = sentence[0][0] + sentence[1][0]
                tree.append((score, [sentence[0][1], sentence[1][1]]))

        best_sentence_set = tree[0]
        for sentence_set in tree:
            if sentence_set[0] > best_sentence_set[0]:
                best_sentence_set = sentence_set

        self.update_scores(best_sentence_set[1], lexicon)

        return best_sentence_set[1]

    def NP_tree(self, words, lexicon):

        if len(words) == 1:
            token = words[0], 'noun'
            score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        words_length = len(words)
        tree = [(0, [])]

        if words[0] in self.dets:
            tree.pop(0)
            token = words[0], 'determiner'
            score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            phrase = [token]
            tree.append((score, phrase))
            words.pop(0)

        for word in words:  # gives every possibility of POS of words
            for i in range(len(tree)):
                phrase_set = tree.pop(0)
                score = phrase_set[0]
                phrase = phrase_set[1]
                for POS in ['determiner', 'noun', 'preposition', 'adverb', 'adjective']:
                    if len(phrase) > 0:
                        if POS != 'noun' and len(phrase) == words_length - 1:  # only nouns are allowed at the end
                            pass
                        elif (POS == 'determiner' and word not in self.dets) and (phrase[-1][1] != 'preposition'):  # determiners only come after prepositions
                            pass
                        elif (POS == 'noun' or POS == 'adjective' or POS == 'adverb') and phrase[-1][1] == 'noun':  # nouns are never followed by another noun or adjective
                            pass
                        elif POS == 'noun' and phrase[-1][1] == 'adverb':  # nouns cannot follow adverbs
                            pass
                        elif POS == 'adverb' and phrase[-1][1] == 'adjective':  # adverbs cannot follow adjectives
                            pass
                        elif POS == 'preposition' and (phrase[-1][1] != 'noun'):  # prepositions only come after nouns
                            pass
                        elif len(phrase) == words_length:
                            tree.append((score, phrase))
                        elif len(phrase) < words_length:
                            token = word, POS
                            new_score = score + lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
                            new_phrase = phrase + [token]
                            tree.append((new_score, new_phrase))
                    elif POS == 'noun' or POS == 'adjective' or POS == 'adverb':
                        token = word, POS
                        new_score = score + lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
                        new_phrase = phrase + [token]
                        tree.append((new_score, new_phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def VP_tree(self, words, lexicon):

        if len(words) == 1:
            token = words[0], 'verb'
            score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(1, len(words)):
            phrase = words[:i]
            phrase = [(phrase[j], 'adverb') for j in range(len(phrase) - 1)] + [(phrase[-1], 'verb')]
            score = 0
            for token in phrase:
                score += lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            np = self.NP_tree(words[i:], lexicon)
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