import fileinput
import time
import nltk
import requests
import sys
import re

# nltk.download()
from nltk.sentiment import SentimentIntensityAnalyzer

REST_URL = "http://text-processing.com/api/sentiment/"
REST_POST = "text=%s"
# session_words = []
RE = re.compile('[0-9a-z-]', re.I)

'''
class Word:
    def __init__(self, word, timestamp):
        self.word = word
        self.timestamp = timestamp
'''


class Sentence:
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


'''
def words_per_minute(word_list):
    min_time = 999999999999999
    max_time = 0

    # find min/max time
    for element in word_list:
        if element.time_start < min_time:
            min_time = element.time_start
        if element.time_start > max_time:
            max_time = element.time_start

    # difference in seconds
    diff = max_time - min_time
    return int(len(word_list) / 2.0)
'''


def main():
    # replace this with rest post later
    for line in fileinput.input(sys.argv[1]):
        s = analyze(line, time.time(), time.time())
        # session_words.append(s)
        # wpm = words_per_minute(session_words)


if __name__ == "__main__":
    main()

    '''
    for line in fileinput.input(sys.argv[1]):
        tokens = nltk.word_tokenize(line)
        curr_time = time.time()


        for token in tokens:
            curr_word = Word(token, curr_time)
            get_label(curr_word)
            session_words.append(curr_word)

    print(session_words)
    print(words_per_minute(session_words))
    '''
