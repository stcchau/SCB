from Parser import Parser

class Brain:
    def __init__(self):
        self.taxonomy = {}
        self.verb_associations = {}
        self.descriptions = {}
        self.parser = Parser()
        self.lexicon = {}
