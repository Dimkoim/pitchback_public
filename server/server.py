import gzip
import uuid
import json
import base64
import dateutil.parser
import io
from opencv  import run_opencv
from flask import Flask, request
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import send_file
from flask_socketio import SocketIO, send, emit

from text_sentiments import analyze

app = Flask(__name__)
socketio = SocketIO(app, message_queue='redis://')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hostname:password@localhost/pitchbackdb'
db = SQLAlchemy(app)

class Text(db.Model):
    __tablename__ = 'Text'
    entry_id = db.Column(db.String(128), primary_key=True)
    ts_start = db.Column(db.DateTime)
    ts_end = db.Column(db.DateTime)
    text = db.Column(db.String(4096))

    # stats
    compound = db.Column(db.Float)
    readability = db.Column(db.Float)
    pos_nltk = db.Column(db.Float)
    neg_nltk = db.Column(db.Float)
    neu_nltk = db.Column(db.Float)
    label_nltk = db.Column(db.String(128))
    pos_rest = db.Column(db.Float)
    neg_rest = db.Column(db.Float)
    neu_rest = db.Column(db.Float)
    pos_rest = db.Column(db.Float)
    label_rest = db.Column(db.String(128))

    def __init__(self, ts_start, ts_end, text, compound, readability,
                 pos_nltk, neg_nltk , neu_nltk, label_nltk, pos_rest, neg_rest,
                 neu_rest, label_rest):
        self.entry_id = str(uuid.uuid4())
        self.ts_start = ts_start
        self.ts_end = ts_end
        self.text = text
        self.compound = compound
        self.readability = readability
        self.pos_nltk = pos_nltk
        self.neg_nltk = neg_nltk
        self.neu_nltk = neu_nltk
        self.label_nltk = label_nltk
        self.pos_rest = pos_rest
        self.neg_rest = neg_rest
        self.neu_rest = neu_rest
        self.label_rest = label_rest

    def to_dict(self):
        return {
            'ts_start': self.ts_start.isoformat(),
            'ts_end': self.ts_end.isoformat(),
            'text': self.text,
            'compound': self.compound,
            'readability' : self.readability,
            'pos_nltk': self.pos_nltk, 'neg_nltk' : self.neg_nltk,
            'neu_nltk' : self.neu_nltk, 'label_nltk' : self.label_nltk,
            'pos_rest': self.pos_rest, 'neg_rest' : self.neg_rest,
            'neu_rest' : self.neu_rest, 'label_rest' : self.label_rest,
        }

class Frame(db.Model):
    __tablename__ = 'Frame'
    frame_id = db.Column(db.String(128), primary_key=True)
    ts = db.Column(db.DateTime)
    img = db.Column(db.LargeBinary)

    def __init__(self, ts, img, nr_faces, nr_profiles, img_annotated):
        self.frame_id = str(uuid.uuid4())
        self.ts = ts
        self.img = img
        self.nr_faces = nr_faces
        self.nr_profiles = nr_profiles
        self.img_annotated = img_annotated

    def to_dict(self):
        return {'ts' : self.ts, 'img' : self.img,
        'nr_faces': self.nr_faces, 'nr_profiles': self.nr_profiles,
        'img_annotated': self.img_annotated}

class FrameAPI(MethodView):
    def get(self):
        ts = request.args.get('ts')
        obj = Frame.query.order_by(Frame.ts.desc()).first().img
        return send_file(io.BytesIO(obj),
                         attachment_filename='image.jpg',
                         mimetype='image/jpeg')

    def post(self):
        fakefile = io.BytesIO(request.data)
        uncompressed = gzip.GzipFile(fileobj=fakefile, mode='rb')
        req = json.loads(uncompressed.read().decode('utf-8'))
        ts = dateutil.parser.parse(req['ts'])
        img = base64.b64decode(req['img'])

        # call our external computations
        nr_faces, nr_profiles, img_boxes = run_opencv(img)

        f = Frame(ts, img, nr_faces, nr_profiles, img_boxes)
        db.session.add(f)
        db.session.commit()
        socketio.emit('frame', {'data': 42})
        return ('', 204)


app.add_url_rule('/api/frame', view_func=FrameAPI.as_view('frame'))

class TextAPI(MethodView):
    def post(self):
        req = json.loads(request.data.decode('utf-8'))
        ts_start = dateutil.parser.parse(req['ts_start'])
        ts_end = dateutil.parser.parse(req['ts_end'])
        text = req['text']

        # do text analysis
        res = analyze(text, ts_start, ts_end)

        t = Text(
            ts_start, ts_end, text, res['compound'], res['readability'],
            res['sentiment_nltk']['pos'],
            res['sentiment_nltk']['neg'],
            res['sentiment_nltk']['neu'],
            res['label_nltk'],
            res['sentiment_rest']['pos'],
            res['sentiment_rest']['neg'],
            res['sentiment_rest']['neu'],
            res['label_rest']
        )

        db.session.add(t)
        db.session.commit()
        return ('', 204)

app.add_url_rule('/api/text', view_func=TextAPI.as_view('text'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    socketio.run(app)
