#!/usr/bin/env python3
import requests
requests.packages.urllib3.disable_warnings()
import sys
import json
import os
import getpass
import time
import asyncio
import websockets

class DAClient:

    def __init__(self, url, keycloak_server=None, keycloak_client_id=None, keycloak_realm=None):
        if not url:
            raise ValueError('Empty Dependency Analyzer url')
        self.url_rest = url + "/da/rest/v-1"
        self.url_ws = url + "/da/ws"
        self.auth = AuthToken(keycloak_server, keycloak_client_id, keycloak_realm)

    def endpoint(self, endpoint):
        return DAEndpoint(self, endpoint)

    def _get(self, path):
        return self._request(requests.get, path)

    def _put(self, path, data, auth=True):
        session = self._auth(auth)
        return self._request(session.put, path, data)

    def _post(self, path, data, auth=True):
        session = self._auth(auth)
        return self._request(session.post, path, data)

    def _delete(self, path, data, auth=True):
        session = self._auth(auth)
        return self._request(session.delete, path, data)

    def _ws(self, method, data):
        query = '{"jsonrpc": "2.0", "method":"'+method+'","id": "request_0", "params":'+data+'}'
        return self._ws(query)

    def _ws(self, query):
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(self._request_ws(query))

    def _auth(self, auth):
        session = requests.Session() 
        if not auth:
            return session;

        token = self.auth.get_token()
        
        session.headers.update({'Authorization': " Bearer " + token})
        return session

    def _handle_error(self, response):
        if type(response) == dict and response['errorMessage']:
            print(response['errorMessage'])
        else:
            print("Got 404 status from the server "+self.url_rest+".")
        sys.exit(1)
       
    def _request(self, requests_method, path, json_request=None):
        link = self.url_rest + path
        try:
            if json_request:
                reply = requests_method("http://"+link, json=json_request)
            else:
                reply = requests_method("http://"+link)
            # this call throws an exception if the status is 4xx or 5xx
            # we have an exception for 404, since 404 can indicate other
            # normal stuff to the caller of the method
            if reply.status_code == 404:
                self._handle_error(reply)
            else:
                reply.raise_for_status()
            return reply
        except requests.exceptions.HTTPError:          
            print(">>> ERROR: Request to: {} failed <<<".format(link))
            print(">>> Status: {} <<<".format(reply.status_code))
            
            if reply.status_code == 403:
                print("Not authorized!")
                exit()
            if json_request:
                print(">>> JSON Data: {} <<<".format(json.dumps(json_request)))
            print("")
            if reply.status_code != 500 and reply.status_code != 503:
                try:
                    print(reply.json()["details"])
                except (json.decoder.JSONDecodeError):
                    pass
                    
        except requests.exceptions.SSLError:
            print("Not authorized!")
                    
            sys.exit(1)

    async def _request_ws(self, query):
        try:
            async with websockets.connect("ws://"+self.url_ws) as websocket:
                await websocket.send(query)
                output = await websocket.recv()
            try:
                output = json.loads(output)["result"]
                return output
            except KeyError:
                print(json.loads(output)["error"]["message"])
                if "data" in json.loads(output)["error"]:
                    print(json.loads(output)["error"]["data"])
                exit()
        except websockets.exceptions.InvalidHandshake:
            print("Server ws://" + self.url_ws + " not found!")
            exit()
    
class DAEndpoint:

    def __init__(self, da, endpoint):
        self.da = da
        self.endpoint = endpoint

    def get(self, path=""):
        return self.da._get(self.endpoint+path)

    def put(self, path, data):
        return self.da._put(self.endpoint+path, data)

    def put(self, data):
        return self.da._put(self.endpoint, data)

    def post(self, path, data):
        return self.da._post(self.endpoint+path, data)

    def post(self, data):
        return self.da._post(self.endpoint, data)

    def delete(self, path, data):
        return self.da._delete(self.endpoint+path, data)

    def delete(self, data):
        return self.da._delete(self.endpoint, data)

    def ws(self, method, data):
        return self.da._ws(method, data)

class AuthToken:

    def __init__(self, keycloak_server, keycloak_client_id, keycloak_realm):
        if not keycloak_server or not keycloak_client_id or not keycloak_realm:
            print("Keycloak server is not configured, authenticated methods will not work")
        self.keycloak_server = keycloak_server
        self.keycloak_client_id = keycloak_client_id
        self.keycloak_realm = keycloak_realm
        self.token = None

    def get_token(self):
        if self.token:
            return self.token

        self._find_local_token()

        if not self.token:
            if not self.keycloak_server or not self.keycloak_client_id or not self.keycloak_realm:
                raise ValueError("Keycloak server is not configured and authentication required")

            login = input("Enter login name ["+getpass.getuser()+"]:")
            if not login:
                login = getpass.getuser()
            print("Enter password for " + login)
            pswd = getpass.getpass()
            self.token = self._get_token(login, pswd)
            self._store_local_token()

        return self.token
 
    def _find_local_token(self):
        path = os.path.expanduser("~") + "/.config/dependency-analyzer/auth-token"

        if not os.path.isfile(path):
            return

        mt = os.path.getmtime(path)
        ct = time.time()

        if ct - mt > 60*115: # token created more then 115 minutes ago
            return

        f = open(path, 'r')
        self.token = f.read()
        f.close()

        print("Using stored auth token.")

    def _store_local_token(self):
        path = os.path.expanduser("~") + "/.config/dependency-analyzer/"
        if not os.path.exists(path):
            os.makedirs(path)

        f = open(path+"auth-token", 'w')
        f.write(self.token)
        f.close()

    def _get_token(self, login, pswd):
        url = self.keycloak_server
        url += "/realms/" + self.keycloak_realm + "/protocol/openid-connect/token"
        grant_type="password"
        params = {'grant_type': grant_type,'client_id': self.keycloak_client_id,'username': login,'password': pswd}
        r = requests.post(url, params, verify=False)
        if r.status_code == 200:
            reply = json.loads(r.content.decode('utf-8'))
            return( str(reply.get('access_token')))
        else:
            raise Exception("Failed to obtain token from " + url)


