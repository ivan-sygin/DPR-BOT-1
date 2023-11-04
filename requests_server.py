import os

import requests

protocol = 'https://'
ip_server = '26.0.102.28'
port = '7278'

class BackendConnector:
    protocol = 'https'
    ip_server = '26.0.102.28'
    port = '7278'
    url = 'https://26.0.102.28:7278'

    def __init__(self, protocol,ip_server,port):
        self.protocol = protocol
        self.ip_server = ip_server
        self.port = port
        self.url = f'{self.protocol}://{self.ip_server}:{port}'

    def fetchGet(self, address_api, data:dict = None, auth:bool = False):
        temp_url = f'{self.url}{address_api}'
        if data or auth:
            temp_url += '?'
            if auth:
                temp_url += "token" + "=" + os.environ["SECRET_TOKEN"] + "&"
            if data:
                for k,val in data.items():
                    temp_url += k + "=" + str(val) + "&"
            temp_url = temp_url[:-1]
        r = requests.get(temp_url,verify=False)
        print(r.request.url)
        return r.json()

