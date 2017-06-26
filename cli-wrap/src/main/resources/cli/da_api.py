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

def verify_response(response, failure_msg):
    if 'success' in response and not response['success']:
        print(failure_msg)
    if 'message' in response:
        print(response['message'])

def get_gav(item):
    return item['groupId'] + ':' + item['artifactId'] + ':' + item['version']

def get_product(item):
    product = item['name']
    product_version = item['version']
    product_support = item['supportStatus']
    product_id = ""
    if('id' in item):
        product_id = " ("+str(item['id'])+")"

    return product+':'++product_version':'+product_support+product_id

class Blacklist:

    def __init__(self, da):
        self.endpoint = da.endpoint("/listings/blacklist")
    
    def get_all(self):
        r = self.endpoint.get()
    
        for item in r.json():
            print(get_gav(item))

    def get_gav(self, gav):
        groupId, artifactId, version = gav.split(":",3)
        r = self.endpoint.get("/gav?groupid="+groupId+"&artifactid="+artifactId+"&version="+version)

        output = r.json()

        if output['contains']:
            print("Artifact "+gav +" is blacklisted - actual verisions in list: ")
            print(pretty.listCheck(output))
        else:
            print("Artifact "+gav +" is NOT blacklisted")

    def add(self, gav):
        gid, aid, ver = gav.split(':')
        json_request = {}
        json_request['groupId'] = gid
        json_request['artifactId'] = aid
        json_request['version'] = ver
        self.endpoint.post("/gav", json_request)
        verify_response(r.json(), "Addition failed")


class Products:

    def __init__(self, da):
        self.endpoint = da.endpoint("/listings/whitelist")

    def get_all(self):
        r = self.endpoint.get()

        for item in r.json():
            print(get_gav(item)+"\t"+get_product(item))

    def 

