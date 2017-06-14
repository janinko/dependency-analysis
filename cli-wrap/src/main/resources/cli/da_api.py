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
import da_client

class Blacklist:

    def __init__(self, da):
        self.endpoint = da.endpoint("/listings/blacklist")

    def getAll(self):
        r = self.endpoint.get()
    
        if (r.status_code == 404):
            print("Server " + da_server + " not found")
            exit()
        for item in r.json():
            print(item['groupId'] + ':' + item['artifactId'] + ':' + item['version'])

    @arg('gav', help='groupid:artifactid:version of artifact to check if it is in blacklist')
    def getGAV(self, gav):
        if not matchGAV(gav):
            raise Exception("Expected gav in form of groupid:artifactid:version, got " + gav)

        groupId, artifactId, version = gav.split(":",3)
        r = self.endpoint.get("/gav?groupid="+groupId+"&artifactid="+artifactId+"&version="+version)

        output = r.json()
        output = (json.dumps(output))

        if '"contains": true' in output:
            print("Artifact "+gav +" is blacklisted - actual verisions in list: ")
            print(pretty.listCheck(json.loads(output)))
        elif '"contains": false' in output:
            print("Artifact "+gav +" is NOT blacklisted")
        else:
            print("Error checking " +gav)


