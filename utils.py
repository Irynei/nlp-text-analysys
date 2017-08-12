import time
import string
import logging
from functools import wraps
from nltk import sent_tokenize
from nltk import word_tokenize


logger = logging.getLogger(__name__)


def __get_start_data(start_time, func):
    human_date = '{time.tm_hour}:{time.tm_min}:{time.tm_sec}'.format(time=time.localtime(start_time))
    text = 'Function "{}" was called on "{}" with params:\n'.format(func.__name__, human_date)
    return text


def logger_exception(func):
    """Wrapper to log all exceprions. Method DOES NOT catch exceptions
    Returns:
        Function response
    Raises:
        All exceptions from function, if it was catched
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        except Exception:
            text = __get_start_data(start_time, func)
            logger.exception('FUNCTION ERROR:\n' + text + 'Exception:\n')  # Logging start params
            raise
    return wrapper


def tokenize(text):
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