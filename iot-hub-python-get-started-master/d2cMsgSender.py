"""
Module Name:  d2cMsgSender.py
Project:      IoTHubRestSample
Copyright (c) Microsoft Corporation.

Using [Send device-to-cloud message](https://msdn.microsoft.com/en-US/library/azure/mt590784.aspx) API to send device-to-cloud message from the simulated device application to IoT Hub.

This source is subject to the Microsoft Public License.
See http://www.microsoft.com/en-us/openness/licenses.aspx#MPL
All other rights reserved.

THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, 
EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
"""

import base64
import hmac
import hashlib
import time
import requests
import urllib

class D2CMsgSender:
    
    API_VERSION = '2016-02-03'
    TOKEN_VALID_SECS = 10
    TOKEN_FORMAT = 'SharedAccessSignature sig=%s&se=%s&skn=%s&sr=%s'
    
    def __init__(self, connectionString=None):
        if connectionString != None:
            iotHost, keyName, keyValue = [sub[sub.index('=') + 1:] for sub in connectionString.split(";")]
            self.iotHost = iotHost
            self.keyName = keyName
            self.keyValue = keyValue
            
    def _buildExpiryOn(self):
        return '%d' % (time.time() + self.TOKEN_VALID_SECS)
    
    def _buildIoTHubSasToken(self, deviceId):
        resourceUri = '%s/devices/%s' % (self.iotHost, deviceId)
        targetUri = resourceUri.lower()
        expiryTime = self._buildExpiryOn()
        toSign = '%s\n%s' % (targetUri, expiryTime)
        key = base64.b64decode(self.keyValue.encode('utf-8'))
        signature = urllib.quote(
            base64.b64encode(
                hmac.HMAC(key, toSign.encode('utf-8'), hashlib.sha256).digest()
            )
        ).replace('/', '%2F')
        return self.TOKEN_FORMAT % (signature, expiryTime, self.keyName, targetUri)
    
    def sendD2CMsg(self, deviceId, message):
        sasToken = self._buildIoTHubSasToken(deviceId)
        url = 'https://%s/devices/%s/messages/events?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        r = requests.post(url, headers={'Authorization': sasToken}, data=message)
        return r.text, r.status_code
    
if __name__ == '__main__':

    ##
    iot_hub_name = 'pitchback'
    hostname = 'pitchbackraspi1'
    SharedAccessKey = 'd99AU4IJkcS9g6qFRy + MlLNPL0 / Nz5qo3LqhPuviamI ='
    connectionString = 'HostName='+hostname+'azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey='+SharedAccessKey
    #dm = DeviceManager(connectionString)
    deviceId = '13c6bfd4-6e47-4181-a6b4-c78cf650e19b'
    primarykey1 = 'd99AU4IJkcS9g6qFRy+MlLNPL0/Nz5qo3LqhPuviamI='

    ##
    connectionString2 = 'HostName=pitchbackraspi1.azure-devices.net;SharedAccessKeyName=iothubowner;' \
                        'SharedAccessKey=RlKK75FJJwdAamv7FFTyahu / P7wkF6ic85SMAXj5rxM ='
    ##


    #connectionString = 'HostName=<iot-hub-name>.azure-devices.net;SharedAccessKeyName=device;SharedAccessKey=<device-policy-key>'
    d2cMsgSender = D2CMsgSender(connectionString2)
    #deviceId = 'iotdevice1'
    message = 'Hello, IoT Hub'
    f = open('dog.jpg', 'r+')
    jpgdata = f.read()
    f.close()

    print d2cMsgSender.sendD2CMsg(deviceId, jpgdata)

