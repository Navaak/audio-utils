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

    url = POI_BASE_URL + "batch/events.json?accessKey=" + args.token
    headers = {"Content-Type": "application/json"}

    users = db.users.find({})
    data = []
    for user in users:
        gender = ""
        if "gender" in user["profile"]:
            gender = user["profile"]["gender"]

        data.append({
            "event": "$set",
            "entityType": "user",
            "entityId": str(user["_id"]),
            "properties": {
                "gender": gender
            }
        })

        if len(data) >= 50:
            req = requests.post(url, headers=headers, json=data)
            print req.status_code, req.text
            print
            data = []


    if len(data) > 1:
        req = requests.post(url, headers=headers, json=data)
        print req.status_code, req.text
        print
