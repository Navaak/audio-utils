#!/usr/bin/env python

import json
import requests

from argparse import ArgumentParser
from pymongo import MongoClient


POI_BASE_URL = "http://127.0.0.1:7070/"

if __name__ == '__main__':

    parser = ArgumentParser(description = """
    user pusher on event server.
    """)
    parser.add_argument('-t', '--token', help='pio token', required=True)
    args = parser.parse_args()

    db = MongoClient().navaak

    url = POI_BASE_URL + "events.json?accessKey=" + args.token
    headers = {"Content-Type": "application/json"}

    users = db.users.find({})
    data = []

    for user in users:


        data.append({
            "event": "$set",
            "entity": "user",
            "entityId": str(user["_id"]),
            "properties": {
                "gender": user["profile"]["gender"]
            }
        })

        if len(data) >= 500:
            req = requests.post(url, headers=headers, json=data)
            print req.status_code, req.text
            print
            data = []


    if len(data) > 1:
        req = requests.post(url, headers=headers, json=data)
        print req.status_code, req.text
        print
