import re
import string
from collections import Counter


class SpellChecker:
    """
    Check spelling and provides corrections.
    """

    def __init__(self, filepath='text_data/big.txt'):
        self.words = Counter(SpellChecker._find_words(open(filepath).read()))

    @staticmethod
    def _find_words(text):
        """
        Split text to words
        :param text: string text
        :return: list of words
        """
        return re.findall(r'\w+', text.lower())

    @staticmethod
    def _one_edit(word):
        """
        All edits(deletes,transposes, replaces, inserts)
        that are one edit away from word.
        :param word: string word
        :return: set of edited words
        """
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    @staticmethod
    def _two_edits(word):
        """
        All edits that are two edits away from word."
        :param word: string word
        :return: generator of edited words
        """
        return (e2 for e1 in SpellChecker._one_edit(word) for e2 in SpellChecker._one_edit(e1))

    def _get_probability(self, word):
        """
        Get word probability
        :param word: string word
        :return: float probability
        """
        n = sum(self.words.values())
        return self.words[word] / n

    def _candidates(self, word):
        """
        Generate possible spelling corrections for word.
        :param word: string
        :return: word from dictionary or word get by 1 correction
         or word get by 2 corrections or word itself
        """
        return (
            self._known([word]) or
            self._known(self._one_edit(word)) or
            self._known(self._two_edits(word)) or
            [word]
        )

    def check(self, word, count=2):
        """
        Most probable spelling correction for word.
        :param word: string
        :param count: int number of returned corrected words
        :return: list of  words
        """
        sorted_candidates = sorted(self._candidates(word), key=self._get_probability, reverse=True)
        return sorted_candidates[:count]

    def multiple_check(self, words_to_analyze, count=2):
        """
        Check multiple words
        :param words_to_analyze: lsit of words
        :param count: int number of returned corrected words
        :return: dict of words
        """
        result = {}
        for word in self.find_words(words_to_analyze):
            result[word] = self.check(word, count)
        return result

    def _known(self, words):
        """
        The subset of `words` that appear in the dictionary of words
        :param words: list of words
        :return: set of known words
        """
        return set(w for w in words if w in self.words)
