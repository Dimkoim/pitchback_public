#!/usr/bin/env python

# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Draws squares around faces in the given image."""

import argparse
import base64
import io

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from PIL import Image
from PIL import ImageDraw

import json


# [START get_vision_service]
def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials)
# [END get_vision_service]


def detect_face(img, max_results=25):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.

    Returns:
        An array of dicts with information about the faces in the picture.
    """
    #image_content = face_file.read()
    batch_request = [{
        'image': {
            #'content': base64.b64encode(image_content).decode('utf-8')
            'content': img.decode('utf-8')
            },
        'features': [{
            'type': 'FACE_DETECTION',
            'maxResults': max_results,
            }]
        }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
        })
    response = request.execute()

    return response['responses'][0]['faceAnnotations']


def highlight_faces(image, faces, output_filename):
    """Draws a polygon around the faces, then saves to output_filename.

    Args:
      image: a file containing the image with the faces.
      faces: a list of faces found in the file. This should be in the format
          returned by the Vision API.
      output_filename: the name of the image file to be created, where the
          faces have polygons drawn around them.
    """
    stream = io.BytesIO(image)
    im = Image.open(stream)
    draw = ImageDraw.Draw(im)

    for face in faces:
        box = [(v.get('x', 0.0), v.get('y', 0.0))
               for v in face['fdBoundingPoly']['vertices']]
        draw.line(box + [box[0]], width=5, fill='#00ff00')

    im.save(output_filename)


def main(image, img64, output_filename, max_results):
    #with open(input_filename, 'rb') as image:
    #faces=[]
    faces = detect_face(img64, max_results)
    print('Found {} face{}'.format(
        len(faces), '' if len(faces) == 1 else 's'))

    print('Writing to file {}'.format(output_filename))
    # Reset the file pointer, so we can read the file again
    #image.seek(0)
    with open("foo.jpg", "wb") as f:
        f.write(image)

    highlight_faces(image, faces, output_filename)

    #print type(faces)
    with open('text.txt','w') as f:
        json.dump(faces, f)
        #    f.write("%s\n" % item)


if __name__ == '__main__':
    #parser = argparse.ArgumentParser(
    #    description='Detects faces in the given image.')
    #parser.add_argument(
    #    'input_image', help='the image you\'d like to detect faces in.')
    #parser.add_argument(
    #    '--out', dest='output', default='out.jpg',
    #    help='the name of the output file.')
    #parser.add_argument(
    #    '--max-results', dest='max_results', default=100,
    #    help='the max results of face detection.')
    #args = parser.parse_args()

    #open dict and pass image to google
    #print args.input_image

    filepath = '/Users/gabrielfior/pitchback/face-recognition-google/foo.json'
    max_results=100
    output_name = filepath + 'out.jpg'

    from cStringIO import StringIO
    from PIL import Image

    with open(filepath, "r") as data_file:
        data = json.load(data_file)

    img_b64 = data['img']
    img =  base64.b64decode(img_b64)

    #main(args.input_image, args.output, args.max_results)
    main(img, img_b64,output_name, max_results)