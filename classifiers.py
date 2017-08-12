import os
import random
import string
import pickle
import collections
from sklearn import svm
from nltk.metrics import *
import nltk.classify.util
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.metrics import BigramAssocMeasures
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews, stopwords
from sklearn.metrics import classification_report
from nltk.probability import FreqDist, ConditionalFreqDist
from sklearn.feature_extraction.text import TfidfVectorizer


class SVMClassifier:
    """
    SVM Classifier.
    Predicts pos/neg label for words.
    """
    def __init__(self, data_dir='text_data/txt_sentoken', cfr=svm.LinearSVC()):
        self.data_dir = data_dir
        self.classifier = cfr
        self.train_labels = []
        self.train_data = []
        self.test_labels = []
        self.test_data = []
        self.classes = ['pos', 'neg']
        self.train_vectors = None
        self.test_vectors = None
        self.vectorizer = None

    def prepare_data(self):
        """
        Prepare data.
        """
        for i in self.classes:
            dirname = os.path.join(self.data_dir, i)
            for filename in os.listdir(dirname):
                with open(os.path.join(dirname, filename), 'r') as f:
                    data = f.read()
                    # split data to test and training sets
                    if filename.startswith('cv9'):
                        self.test_data.append(data)
                        self.test_labels.append(i)
                    else:
                        self.train_data.append(data)
                        self.train_labels.append(i)

    def train(self):
        """
        Train classifier
        """
        self.vectorizer = TfidfVectorizer(
            min_df=5,
            max_df=0.8,
            sublinear_tf=True,
            use_idf=True,
        )
        self.train_vectors = self.vectorizer.fit_transform(self.train_data)
        self.test_vectors = self.vectorizer.transform(self.test_data)

        self.classifier.fit(self.train_vectors, self.train_labels)

    def validate(self):
        """
        Validate classifier
        :return: classification report
        """
        predicted_labels = self.classifier.predict(self.test_vectors)
        return classification_report(self.test_labels, predicted_labels)

    def predict(self, data):
        """
        Predict label
        :param data: string text
        :return: list of predicted labels
        """
        # probability predict 'pos' class
        return [i[1] for i in self.classifier._predict_proba_lr(self.vectorizer.transform(data)).tolist()]


class BayesClassifier:
    """
    Naive Bayes classifier. Predicts pos/neg label for words.
    """
    def __init__(self, model='bag_of_words', cfr=NaiveBayesClassifier):
        self.classifier = cfr
        self.train_data = []
        self.test_data = []
        self.best_words_set = None
        self.classes = ['pos', 'neg']
        self.stopset = set(stopwords.words('english')).union(set(string.punctuation))
        self.models = {
            'bag_of_words': self.bag_of_words,
            'best_words': self.best_word_feats,
        }
        self.model = model

    def bag_of_words(self, words):
        """
        Bag of words model.
        :param words: list of words
        :return: dict
        """
        return dict([(word, True) for word in words if word not in self.stopset])

    def best_word_feats(self, words):
        """
        Bag of words model using only best words
        :param words: list of words
        :return: dict
        """
        if not self.best_words_set:
            self._get_best_words()
        return dict([(word, True) for word in words if word in self.best_words_set])

    def _get_best_words(self):
        """
        Get best words set
        """
        words_frequencies = FreqDist()
        label_words_frequencies = ConditionalFreqDist()

        for word in movie_reviews.words(categories=['pos']):
            words_frequencies[word.lower()] += 1
            label_words_frequencies['pos'][word.lower()] += 1

        for word in movie_reviews.words(categories=['neg']):
            words_frequencies[word.lower()] += 1
            label_words_frequencies['neg'][word.lower()] += 1

        pos_words_count = label_words_frequencies['pos'].N()
        neg_words_count = label_words_frequencies['neg'].N()
        total_words_count = pos_words_count + neg_words_count

        words_scores = {}

        for word, frequency in words_frequencies.items():
            pos_score = BigramAssocMeasures.chi_sq(label_words_frequencies['pos'][word],
                (frequency, pos_words_count), total_words_count)
            neg_score = BigramAssocMeasures.chi_sq(label_words_frequencies['neg'][word],
                (frequency, neg_words_count), total_words_count)
            words_scores[word] = pos_score + neg_score

        best_words = sorted(words_scores.items(), key=lambda x: x[1], reverse=True)[:10000]
        self.best_words_set = set([w for w, s in best_words if w not in self.stopset])

    @staticmethod
    def tokenize(text):
        """
        Generator. Yields tokens from text
        :param text: string
        """
        # break the document into sentences
        for sent in sent_tokenize(text):
            # break the sentence into part of speech tagged tokens(words)
            for token in word_tokenize(sent):
                token = token.lower()
                token = token.strip()
                token = token.strip('_')

                if all(char in set(string.punctuation) for char in token):
                    continue

                yield token

    def prepare_simple_data(self):
        """
        Prepare test and train sets
        """
        neg_files = movie_reviews.fileids('neg')
        pos_files = movie_reviews.fileids('pos')

        neg_data = [(self.models.get(self.model)(movie_reviews.words(fileids=[f])), 'neg') for f in neg_files]
        pos_data = [(self.models.get(self.model)(movie_reviews.words(fileids=[f])), 'pos') for f in pos_files]

        # split data to positive and negative
        neg_data_cut_index = int(len(neg_data) * 3 / 4)
        pos_data_cut_index = int(len(pos_data) * 3 / 4)

        train_data = neg_data[:neg_data_cut_index] + pos_data[:pos_data_cut_index]
        test_data = neg_data[neg_data_cut_index:] + pos_data[pos_data_cut_index:]

        # shuffle test and train data
        random.shuffle(train_data)
        random.shuffle(test_data)

        self.train_data = train_data
        self.test_data = test_data

    def train(self):
        """
        Train classifier
        """
        self.classifier = self.classifier.train(self.train_data)

    def validate(self):
        """
        Validate classifier
        :return: dict of validation statistics
        """
        ref_sets = collections.defaultdict(set)
        test_sets = collections.defaultdict(set)

        for i, (feats, label) in enumerate(self.test_data):
                ref_sets[label].add(i)
                observed = self.classifier.classify(feats)
                test_sets[observed].add(i)
        self.classifier.show_most_informative_features()
        return {
            'accuracy:': nltk.classify.util.accuracy(self.classifier, self.test_data),
            'pos precision:': precision(ref_sets['pos'], test_sets['pos']),
            'pos recall:': recall(ref_sets['pos'], test_sets['pos']),
            'neg precision:': precision(ref_sets['neg'], test_sets['neg']),
            'neg recall:': recall(ref_sets['neg'], test_sets['neg'])
        }

    def predict(self, data):
        """
        Predict label for text
        :param data: string text
        :return: list of labels
        """
        predictions = self.classifier.prob_classify_many(
            self.models[self.model](self.tokenize(words)) for words in data
        )
        return [p.max() for p in predictions]

    def predict_prob(self, data):
        """
        Prediction probabilities
        :param data: string text
        :return: list of probabilities
        """
        predictions = self.classifier.prob_classify_many(
            self.models[self.model](self.tokenize(words)) for words in data
        )
        preds = [p.prob('pos') for p in predictions if p.prob('pos') != 0.5]
        return preds


class Classifiers:
    def __init__(self):
        self.naive_bag_of_words = BayesClassifier()
        self.naive_best_words = BayesClassifier(model='best_words')
        self.svm = SVMClassifier()

    def train_and_save(self):
        """
        Train and serialize classifiers
        """
        self.naive_bag_of_words.prepare_simple_data()
        self.naive_bag_of_words.train()

        self.naive_best_words.prepare_simple_data()
        self.naive_best_words.train()

        self.svm.prepare_data()
        self.svm.train()

        with open('naive_bag_of_words.pickle', 'wb') as f:
            pickle.dump(self.naive_bag_of_words, f, -1)

        with open('naive_best_words.pickle', 'wb') as f:
            pickle.dump(self.naive_best_words, f, -1)

        with open('svm.pickle', 'wb') as f:
            pickle.dump(self.svm, f, -1)

    def get_trained(self):
        """
        Get trained classifiers
        """
        with open('naive_bag_of_words.pickle', 'rb') as f:
            self.naive_bag_of_words = pickle.load(f)

        with open('naive_best_words.pickle', 'rb') as f:
            self.naive_best_words = pickle.load(f)

        with open('svm.pickle', 'rb') as f:
            self.svm = pickle.load(f)
