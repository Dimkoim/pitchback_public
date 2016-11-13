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



from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import urllib2
import random

def return_faces_from_base64_image(list_img_b64,max_results=70):

    """
    input:
    img_b64: list of dicts like
    [
        {id: 123, img_64: 'bd/a11s/2'
        },
        {id: 123, img_64: 'bd/a11s/2'
        }
    ]

    """

    try:

        def detect_face(img, max_results):
            """Uses the Vision API to detect faces in the given file.
            assumes the img is list of dicts with key = 'img' to retrieve the image

            Args:
                img = list of images
                #### OLD: A file-like object containing an image with faces.

            Returns:
                An array of dicts with information about the faces in the picture.
            """
            # image_content = face_file.read()

            batch_request_list=[]
            for i in img:
                batch_request = [{
                    'image': {
                        # 'content': base64.b64encode(image_content).decode('utf-8')
                        'content': i['img'].decode('utf-8')
                    },
                    'features': [{
                        'type': 'FACE_DETECTION',
                        'maxResults': max_results,
                    }]
                }]
                batch_request_list.append(batch_request)

            service = get_vision_service()
            request = service.images().annotate(body={
                'requests': batch_request_list,
            })
            response = request.execute()

            #return response['responses'][0]['faceAnnotations']
            return response



        #faces = detect_face(img_b64, max_results)
        responses = detect_face(list_img_b64, max_results)


        def get_vision_service():
            credentials = GoogleCredentials.get_application_default()
            return discovery.build('vision', 'v1', credentials=credentials)
        # [END get_vision_service]

        def return_score_enum(enum1):

            if str(enum1)=="VERY_UNLIKELY":
                return 0
            elif str(enum1)=="UNKNOWN":
                return 0
            elif str(enum1) == "UNLIKELY":
                return 1
            elif str(enum1) == "POSSIBLE":
                return 2
            elif str(enum1) == "LIKELY":
                return 3
            elif str(enum1) == "VERY_LIKELY":
                return 4
            else:
                return None

        #process faces to get joyScore and other scores

        list_ids = []
        for item in list_img_b64:
            list_ids.append(item['id'])  #process responses

        dict_face = {}
        list_dicts=[]
        for index,j in enumerate(responses):
            for face_count,face in enumerate(j['faceAnnotations']):


                dict_face['detec_confidence'] = ((face['detectionConfidence'])) #double
                dict_face['anger']=(return_score_enum(face['angerLikelihood']))
                dict_face['blurred']=(return_score_enum(face['blurredLikelihood']))
                dict_face['headwear'] = (return_score_enum(face['headwearLikelihood']))
                dict_face['joy']=(return_score_enum(face['joyLikelihood']))
                dict_face['pan_angle']=(face['panAngle']) #double
                dict_face['roll_angle']=((face['rollAngle'])) #double
                dict_face['sorrow']=(return_score_enum(face['sorrowLikelihood']))
                dict_face['surprise']=(return_score_enum(face['surpriseLikelihood']))
                dict_face['tilt_angle']=((face['tiltAngle'])) #double
                dict_face['under_exposed']=(return_score_enum(face['underExposedLikelihood']))
                dict_face['id']=list_ids[index]

                list_dicts.append(dict_face)


        #return id + labels


        return list_dicts

    except urllib2.HTTPError:
        return ""
    except KeyError:
        pass