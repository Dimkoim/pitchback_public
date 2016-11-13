import speech_recognition as sr
#import time
import requests
import sys
import datetime
import simplejson
from threading import Thread

r=sr.Recognizer()

# change these if necessary
URL = "http://pitchback.tech:5000/api/text"
API_KEY = None

def parse(audio_rec):
    return r.recognize_google(audio_rec, key=API_KEY)

def send(text, start_time, end_time):
    # ignore empty texts
    if text == "":
        print("Error, not sending", file=sys.stderr)
        return
    requests.post(URL, data=simplejson.dumps({'text': text, 'ts_start': start_time, 'ts_end': end_time}))
    print(text + "\t" + str(start_time) + "\t" + str(end_time))


def thread_call(audio, start, end):
    send(parse(audio), start, end)
 
def main():
    while True:
        try:
            with sr.Microphone() as src:
                start = datetime.datetime.now().isoformat()
                audio = r.listen(src,0.5)
                end = datetime.datetime.now().isoformat()
                t = Thread(target=thread_call, args=(audio, start, end))
                t.start()
        except sr.WaitTimeoutError:
            # ignore timeouts
            print("timeout", file=sys.stderr)


if __name__ == '__main__':
    main()
