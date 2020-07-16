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
        self.to_be = ['am', 'are', 'is', 'was', 'were', 'being', 'been', 'be']
        self.helping = ['BE'] + self.modals + ['have', 'has', 'had', 'do', 'does', 'did']
        self.q_word = ['who', 'what', 'when', 'where' 'why', 'how']
        self.ends = '.?!'

    def update_scores(self, tree, lexicon):

        """updates scores for part of speech"""

        for branch in tree:
            if type(branch) == tuple:
                lexicon[branch[0]][branch[1]] += 1
                lexicon[branch[0]]['~'] += 1
            else:
                self.update_scores(branch, lexicon)

    def token_score(self, token, lexicon):
        return lexicon[token[0]][token[1]] / lexicon[token[0]]['~']

    def display(self, tree):

        """prints out sentence parse tree"""

        for branch in tree:
            if type(branch) == tuple:
                print(branch, end=' ')
            else:
                self.display(branch)

    def update_lexicon(self, words, lexicon):

        """adds new words into the lexicon"""

        for word in words:
            if word not in lexicon:

                if word[-3:] == 'ing':  # checks if base verb exists
                    if word[:-3] in lexicon:  # trying = try
                        lexicon[word] = lexicon[word[:-3]]
                    elif word[:-3] + 'e' in lexicon:  # leaving = leave
                        lexicon[word] = lexicon[word[:-3] + 'e']
                    elif word[-4:] == 'ying' and word[:-4] + 'ie' in lexicon:  # tying = tie
                        lexicon[word] = lexicon[word[:-4] + 'ie']
                    elif word[:-4] in lexicon:  # fitting = fit
                        lexicon[word] = lexicon[word[:-4]]
                    else:
                        lexicon[word] = {'Det': 0,
                                         'N': 0,
                                         'Adv': 0,
                                         'Adj': 0,
                                         'V': 1,
                                         'HV': 0,
                                         'P': 0,
                                         '~': 2}
                    continue

                elif word + 'ing' in lexicon:  # try = trying
                    lexicon[word] = lexicon[word + 'ing']
                    continue
                elif word + word[-1] + 'ing' in lexicon:  # fit = fitting
                    lexicon[word] = lexicon[word + word[-1] + 'ing']
                    continue
                elif word[:-2] == 'ie' and word[-2:] + 'ying' in lexicon:  # tie = tying
                    lexicon[word] = lexicon[word[-2:] + 'ying']
                    continue

                elif word[-2:] == 'ly':  # words ending in ly tend to be adverbs
                    lexicon[word] = {'Det': 0,
                                     'N': 0,
                                     'Adv': 1,
                                     'Adj': 0,
                                     'V': 0,
                                     'HV': 0,
                                     'P': 0,
                                     '~': 2}
                    continue

                elif word[-2:] == "'s":  # words with 's tend to be adjectives
                    lexicon[word] = {'Det': 0,
                                     'N': 0,
                                     'Adv': 0,
                                     'Adj': 1,
                                     'V': 0,
                                     'HV': 0,
                                     'P': 0,
                                     '~': 2}
                    continue

                elif word[-1] == 's' and word[-2] != 's':  # plurals
                    if word[:-1] in lexicon:
                        lexicon[word] = lexicon[word[:-1]]
                        continue
                    elif word[-2] == 'e' and word[:-2] in lexicon:
                        lexicon[word] = lexicon[word[:-2]]
                        continue

                elif word + 's' in lexicon:
                    lexicon[word] = lexicon[word + 's']
                    continue
                elif word + 'es' in lexicon:
                    lexicon[word] = lexicon[word + 'es']
                    continue

                if word in self.modals:
                    lexicon[word] = {'Det': 0,
                                     'N': 0,
                                     'Adv': 0,
                                     'Adj': 0,
                                     'V': 0,
                                     'HV': 1,
                                     'P': 0,
                                     '~': 2}
                else:
                    lexicon[word] = {'Det': 0,
                                     'N': 0,
                                     'Adv': 0,
                                     'Adj': 0,
                                     'V': 0,
                                     'HV': 0,
                                     'P': 0,
                                     '~': 1}

    def translate(self, sentence, lexicon):

        """simplifies sentence into word array"""

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

        """
        S -> NP VP
        """

        tree = []

        for i in range(1 if words[0] not in (self.poss_adjs + self.arts) else 2, len(words)):
            if words[i] in self.dets:
                continue
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

        """
        NP -> [Det] [ND] N [PP]
        """

        if len(words) == 1:
            token = words[0], 'N'
            score = self.token_score(token, lexicon)
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(len(words)):  # words[i] = noun
            if i == len(words) - 2:  # nouns cannot be second to last
                continue

            if i < len(words) - 2 and words[i + 1] in self.dets:  # determiners cannot start PP
                continue

            score = 0
            phrase = []

            is_det = False
            if words[0] in self.dets:
                if i == 0:
                    continue
                token = words[0], 'Det'
                score += self.token_score(token, lexicon)
                phrase.append(token)
                is_det = True

            if len(words[1 if is_det else 0:i]) > 0:
                nd = self.ND_tree(words[1 if is_det else 0:i], lexicon)
                score += nd[0]
                phrase.append(nd[1])

            token = words[i], 'N'
            score += self.token_score(token, lexicon)
            phrase.append(token)

            if len(words[i + 1:]) > 0:
                pp = self.PP_tree(words[i + 1:], lexicon)
                score += pp[0]
                phrase.append(pp[1])

            tree.append((score, phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def ND_tree(self, words, lexicon):

        """
        ND -> {Adv} {Adj} Adj
        """

        if len(words) == 1:
            token = words[0], 'Adj'
            score = self.token_score(token, lexicon)
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(len(words)):

            score = 0
            phrase = [(words[j], 'Adv') for j in range(i)] + [(words[k], 'Adj') for k in range(i, len(words))]

            for token in phrase:
                score += self.token_score(token, lexicon)
            tree.append((score, phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def VP_tree(self, words, lexicon):

        """
        VP -> [{Adv} HV] VPH
        """

        if len(words) == 1:
            token = words[0], 'V'
            score = lexicon[token[0]]['V'] / lexicon[token[0]]['~']
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(len(words)):  # words[i] = first word of VPH

            if words[i] in self.modals + self.dets:  # modals and dets cannot start VPH
                continue

            score = 0
            phrase = []

            if i > 0:

                if words[i - 1] not in self.helping:  # words not in self.helping cannot be HV
                    continue

                phrase = [(words[j], 'Adv') for j in range(i - 1)] + [(words[i - 1], 'HV')]

                for token in phrase:
                    if token[1] == 'HV':
                        score += (self.token_score((token[0], 'V'), lexicon) +
                                  self.token_score(token, lexicon)) / 2
                    else:
                        score += self.token_score(token, lexicon)

            vph = self.VPH_tree(words[i:], lexicon)
            score += vph[0]
            phrase = vph[1] if len(phrase) == 0 else [phrase, vph[1]]
            tree.append((score, phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def VPH_tree(self, words, lexicon):

        """
        VPH -> {Adv} V [NP | ND [PP] | PP]
        TODO: VPH -> {Adv} V [NP | ND [PP] | PP] {Adv}
        """

        if len(words) == 1:
            token = words[0], 'V'
            score = self.token_score(token, lexicon)
            phrase = [token]
            phrase_set = score, phrase
            return phrase_set

        tree = []

        for i in range(1, len(words) + 1):  # words[i] = first word after verb

            score = 0
            phrase = [(words[j], 'Adv') for j in range(i - 1)] + [(words[i - 1], 'V')]
            for token in phrase:
                score += self.token_score(token, lexicon)
            if i == len(words):
                tree.append((score, phrase))
                continue

            np = self.NP_tree(words[i:], lexicon)
            new_score = score + np[0]
            new_phrase = [phrase, np[1]]
            tree.append((new_score, new_phrase))

            modifier = words[i:]
            if modifier[0] in self.dets:
                continue
            if len(modifier) == 1:
                nd = self.ND_tree(modifier, lexicon)
                new_score = score + nd[0]
                new_phrase = [phrase, nd[1]]
                tree.append((new_score, new_phrase))

            else:
                for j in range(1, len(modifier) + 1):
                    if j > len(modifier) - 2:
                        continue
                    if modifier[j] in self.dets:
                        continue
                    nd = self.ND_tree(modifier[:j], lexicon)
                    pp = self.PP_tree(modifier[j:], lexicon)
                    new_score = score + nd[0] + pp[0]
                    new_phrase = [phrase, nd[1], pp[1]]
                    tree.append((new_score, new_phrase))

                nd = self.ND_tree(modifier, lexicon)
                new_score = score + nd[0]
                new_phrase = [phrase, nd[1]]
                tree.append((new_score, new_phrase))

                pp = self.PP_tree(modifier, lexicon)
                new_score = score + pp[0]
                new_phrase = [phrase, pp[1]]
                tree.append((new_score, new_phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set

    def PP_tree(self, words, lexicon):

        """
        PP -> {Adv} P NP
        """

        if len(words) == 1:
            raise ValueError('prepositional phrase needs more than one word')

        tree = []

        for i in range(1, len(words)):
            score = 0
            phrase = [(words[j], 'Adv') for j in range(i - 1)] + [(words[i - 1], 'P')]
            for token in phrase:
                score += self.token_score(token, lexicon)

            np = self.NP_tree(words[i:], lexicon)
            score += np[0]
            phrase.append(np[1])
            tree.append((score, phrase))

        best_phrase_set = tree[0]
        for phrase_set in tree:
            if phrase_set[0] > best_phrase_set[0]:
                best_phrase_set = phrase_set

        return best_phrase_set
