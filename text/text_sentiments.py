#import fileinput
#import time
import nltk
import requests
#import sys
import re

# launch this if nltk is
# nltk.download('punkt')
# nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

REST_URL = "http://text-processing.com/api/sentiment/"
REST_POST = "text=%s"
RE = re.compile('[0-9a-z-]', re.I)


class Sentence:
    # this is not really necessary anymore, but it works, so whatever
    def __init__(self, sentence, time_start, time_end):
        self.full_sentence = sentence
        self.words = []
        self.time_start = time_start
        self.time_end = time_end
        self.sentiment = ""
        self.probabilities = {}
        self.readability = 0.0


def get_label(sentence):
    # call the rest service for classification and probability
    response = requests.post(REST_URL, REST_POST % sentence.full_sentence)
    json_resp = response.json()
    sentence.sentiment = json_resp['label']
    sentence.probabilities = json_resp['probability']


def calc_readability(sentence):
    raw_words = filter(lambda w: RE.search(w) and w.replace('-', ''), nltk.wordpunct_tokenize(sentence.full_sentence))
    sentence.words = nltk.word_tokenize(sentence.full_sentence)

    wc = len(list(raw_words))
    sc = len(sentence.words)
    cc = sum(len(word) for word in sentence.words)

    # automated readability index http://blog.yjl.im/2012/04/calculating-automated-readability-index.html
    sentence.readability = 4.71 * cc / wc + 0.5 * wc / sc - 21.43


def analyze(sentence_string, time_start, time_end):
    # create new sentence object from the string and times
    s = Sentence(sentence_string, time_start, time_end)
    # set the sentiment for the sentence
    get_label(s)
    # get readability score
    sid = SentimentIntensityAnalyzer()
    calc_readability(s)
    # get nltk scores
    ss = sid.polarity_scores(s.full_sentence)
    # find best nltk label
    label_nltk = ""
    max_val_nltk = 0
    if ss['pos'] > max_val_nltk:
        label_nltk = 'pos'
    if ss['neg'] > max_val_nltk:
        label_nltk = 'neg'
    if ss['neu'] > max_val_nltk:
        label_nltk = 'neu'
    
    # create result dict
    res = {
        'compound': ss['compound'],
        'readability': s.readability,
        'sentiment_nltk': {'pos': ss['pos'], 'neu': ss['neu'], 'neg': ss['neg']},
        'label_nltk': label_nltk,
        'label_rest': s.sentiment,
        'sentiment_rest': {'pos': s.probabilities['pos'], 'neu': s.probabilities['neutral'],
                           'neg': s.probabilities['neg']},
        'text': s.full_sentence,
        'start_time': s.time_start,
        'end_time': s.time_end
    }
    return res

