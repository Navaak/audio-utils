import numpy
import os
import json
import fnmatch
import sys
import time
import requests
import subprocess

from essentia.standard import MusicExtractor, YamlOutput
from essentia import Pool
from pymongo import MongoClient
from bson.objectid import ObjectId
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Analyze(object):

    POI_BASE_URL = "http://127.0.0.1:7070/"
    NVK_BASE_URL = "http://navaak.com/pio/"

    def __init__(self, dburi, audio_dir, nvk_token=None, pio_token=None):
        self.nvk_token = nvk_token
        self.pio_token = pio_token
        self.audio_dir = audio_dir
        self.db = MongoClient(dburi).audio_analyze

    @classmethod
    def isMatch(name, patterns):
        if not patterns:
            return False
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    @staticmethod
    def add_to_dict(dict, keys, value):
        for key in keys[:-1]:
            dict = dict.setdefault(key, {})
        dict[keys[-1]] = value


    def pool_to_dict(self, pool, include_descs=None, ignore_descs=None):
        # a workaround to convert Pool to dict
        descs = pool.descriptorNames()
        if include_descs:
            descs = [d for d in descs if isMatch(d, include_descs)]
        if ignore_descs:
            descs = [d for d in descs if not isMatch(d, ignore_descs)]

        result = {}

        for d in descs:
            keys = d.split('.')
            value = pool[d]
            if type(value) is numpy.ndarray:
                value = value.tolist()
            self.add_to_dict(result, keys, value)
        return result


    def save(self, filename, stats, frames):
        base = os.path.basename(filename)
        idstr = base.split(".")[0]
        id = ObjectId(idstr)
        stats["ref_id"] = id
        frames["ref_id"] = id
        self.db.pool_stats.insert(stats)



    def get_track(self, idstr):
        url = self.NVK_BASE_URL + "tracks/" + idstr

        headers = {'auth': self.nvk_token}
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            raise Exception("navaak request err " + req.text)

        track = json.loads(req.text)

        return track




    def watch(self):
        analyze_file = self.analyze_file
        audio_types = ['*.mp3']

        class WatchHandler(FileSystemEventHandler):
            def on_created(self, event):
                process = subprocess.Popen("sync %s" % event.src_path,
                                           shell=True, stdout=subprocess.PIPE)
                process.wait()
                for root, dirnames, filenames in os.walk(event.src_path):
                    for match in audio_types:
                        for filename in fnmatch.filter(filenames, match):
                            audio_file = os.path.relpath(os.path.join(root, filename))
                            analyze_file(filenames)


        observer = Observer()
        event_handler = WatchHandler()
        observer.schedule(event_handler, path=self.audio_dir)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    def analyzed(self, filename):
        base = os.path.basename(filename)
        idstr = base.split(".")[0]
        id = ObjectId(idstr)
        stat = self.db.pool_stats.find_one({"ref_id": id})
        if not stat:
            return False

        return True


    def scan(self, audio_types=None):

        if not audio_types:
            audio_types = ['*.mp3']
            print("Audio files extensions considered by default: " +
                  ' '.join(audio_types))
        else:
            print("Searching for audio files extensions: " +
                  ' '.join(audio_types))
        print("")

        # find all audio files
        os.chdir(self.audio_dir)

        errors = 0

        for root, dirnames, filenames in os.walk("."):
            for match in audio_types:
                for filename in fnmatch.filter(filenames, match):
                    audio_file = os.path.relpath(os.path.join(root, filename))
                    if self.analyzed(audio_file):
                        print filename, " already analyzed"
                        continue
                    err = self.analyze_file(audio_file)
                    if err:
                        errors += 1

        print
        print "Analysis done.", errors, "files have been skipped due to errors"


    def analyze_file(self, audio_file):
        extractor = MusicExtractor()
        print("Analyzing %s" % audio_file)
        try:
            poolStats, poolFrames = extractor(audio_file)
        except Exception, e:
            print("Error processing", audio_file, ":", str(e))
            return str(e)

        stats = self.pool_to_dict(poolStats)
        frames = self.pool_to_dict(poolFrames)

        ### f = open("/home/ehsan/Music/stats.json", "w")
        ### f.write(json.dumps(stats))
        ### f.close()


        try:
            self.save(audio_file, stats, frames)
        except Exception, e:
            print("Error processing", audio_file, ":", str(e))
            return str(e)
