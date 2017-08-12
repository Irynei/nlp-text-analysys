import string
from nltk import pos_tag
from nltk import sent_tokenize
from nltk import wordpunct_tokenize
from nltk.probability import FreqDist


class TextAnalysis:
    """
    Provides simple text analysis
    """

    def __init__(self, filepath=None, text=None):
        self.filepath = filepath
        self.text = text
        if not text:
            self.text = open(filepath).read()
        self.sent_count = 0

    def tokenize(self, text):
        """
        Generator. Yields tokens from text
        :param text: string
        """
        # break the document into sentences
        for sent in sent_tokenize(self.text):
            self.sent_count += 1
            # break the sentence into part of speech tagged tokens(words)
            for token in wordpunct_tokenize(sent):
                token = token.lower()
                token = token.strip()
                token = token.strip('_')
                # skip punctuation
                if all(char in set(string.punctuation) for char in token):
                    continue
                yield token

    def analyze(self):
        """
        Provides simple text analysis
        :return: dict with analysis result
        """
        result = {}
        adjectives, nouns, verbs = ([], [], [])
        words = [word for word in self.tokenize(self.text)]
        frequencies = FreqDist(words)
        tagged_words = pos_tag(words)
        for word in tagged_words:
            tag = word[1]
            if tag == 'JJ':
                adjectives.append(word[0])
            elif tag == 'NN':
                nouns.append(word[0])
            elif tag == 'VB':
                verbs.append(word[0])
        result['words'] = words[:3] + words[4:11]
        result['words count'] = len(frequencies)
        result['sentences count'] = self.sent_count
        result['most_common_10'] = frequencies.most_common(10)
        result['adjectives'] = list(set(adjectives))[:10]
        result['nouns'] = list(set(nouns))[:10]
        result['verbs'] = list(set(verbs))[:10]
        return result

# a = TextAnalysis(filepath='text_data/text.txt')
# print(a.analyze())
