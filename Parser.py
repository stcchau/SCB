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
            if words[i] in self.to_be:
                words[i] = 'BE'
            elif words[i] == 'you':
                words[i] = 'i'
            elif words[i] == 'i':
                words[i] = 'you'
            elif words[i] == 'your':
                words[i] = 'my'
            elif words[i] == 'my':
                words[i] = 'your'
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

        best_sentence = best_sentence_set[1]

        self.update_scores(best_sentence, lexicon)

        return best_sentence

    def NP_tree(self, words, lexicon):

        if len(words) == 1:
            token = words[0], 'noun'
            score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = [(False, 0, [])]

        for i in range(len(words)):
            for j in range(len(tree)):
                phrase_set = tree.pop(0)
                if phrase_set[0]:
                    tree.append(phrase_set)
                else:
                    score = phrase_set[1]
                    phrase = phrase_set[2]
                    for POS in ['determiner', 'noun', 'preposition', 'adverb', 'adjective']:
                        if len(phrase) > 0:
                            if POS != 'noun' and len(phrase) == len(words) - 1:  # only nouns are allowed at the end
                                pass
                            elif (POS == 'noun' or POS == 'adjective' or POS == 'adverb') and phrase[-1][1] == 'noun':  # nouns are never followed by another noun or adjective
                                pass
                            elif POS == 'noun' and phrase[-1][1] == 'adverb':  # nouns cannot follow adverbs
                                pass
                            elif POS == 'adverb' and phrase[-1][1] == 'adjective':  # adverbs cannot follow adjectives
                                pass
                            elif POS == 'preposition' and (phrase[-1][1] != 'noun' or len(words) - len(phrase) < 2):  # prepositions only come after nouns
                                pass
                            elif POS == 'determiner' and (words[i] not in self.dets or len(phrase) != 0):  # determiners only allowed in beginning
                                pass
                            elif len(phrase) < len(words):
                                if POS == 'preposition':
                                    pp = self.PP_tree(words[i:], lexicon)
                                    new_score = score + pp[0]
                                    new_phrase = [phrase, pp[1]]
                                    tree.append((True, new_score, new_phrase))
                                else:
                                    token = words[i], POS
                                    new_score = score + lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
                                    new_phrase = phrase + [token]
                                    if len(new_phrase) == len(words):
                                        tree.append((True, new_score, new_phrase))
                                    else:
                                        tree.append((False, new_score, new_phrase))
                        elif POS == 'noun' or POS == 'adjective' or POS == 'adverb' or (POS == 'determiner' and words[i] in self.dets):
                            token = words[i], POS
                            new_score = score + lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
                            new_phrase = phrase + [token]
                            tree.append((False, new_score, new_phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[1] > best_phrase_set[1]:
                best_phrase_set = phrase_set

        return best_phrase_set[1:]

    def VP_tree(self, words, lexicon):

        if len(words) == 1:
            token = words[0], 'verb'
            score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(1, len(words) + 1):
            phrase = words[:i]
            phrase = [(phrase[j], 'adverb') for j in range(len(phrase) - 1)] + [(phrase[-1], 'verb')]
            score = 0
            for token in phrase:
                score += lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
            if i == len(words):
                new_score = score
                new_phrase = phrase
            else:
                np = self.NP_tree(words[i:], lexicon)
                new_score = score + np[0]
                new_phrase = [phrase, np[1]]
            tree.append((new_score, new_phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def PP_tree(self, words, lexicon):
        token = words[0], 'preposition'
        score = lexicon[token[0]][token[1]] / lexicon[token[0]]['~']
        phrase = [token]
        np = self.NP_tree(words[1:], lexicon)
        new_score = score + np[0]
        new_phrase = [phrase, np[1]]
        phrase_set = (new_score, new_phrase)
        return phrase_set
