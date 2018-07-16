#!/usr/bin/env python

import json

from analyzer.audio import Analyze
from argparse import ArgumentParser





if __name__ == '__main__':
    config = {}
    try:
        confile = open("config.json")
        config = json.loads(confile.read())
    except Exception, e:
        print e

    parser = ArgumentParser(description = """
Analyzes all audio files found (recursively) in a folder using MusicExtractor.
""")

    parser.add_argument('-d', '--dir', help='input directory', required=True)
    parser.add_argument('-db', '--db', help='mongo db uri', required=False)
    parser.add_argument('-nvk_token', '--nvk_token', help='navaak app token',
                        required=False)
    parser.add_argument('-pio_token', '--pio_token', help='pio token',
                        required=False)
    parser.add_argument('-mode', '--mode',
                        help='analyzer scan mode [scan, watch, push_pio]',
                        required=False)
    parser.add_argument(
        '-t', '--type', nargs='+',
        help='type of audio files to include (can use wildcards)',
        required=False)


    args = parser.parse_args()

    if not args.db and "db" in config:
        args.db = config["db"]

    if not args.nvk_token and "nvk_token" in config:
        args.nvk_token = config["nvk_token"]

    if not args.pio_token and "pio_token" in config:
        args.pio_token = config["pio_token"]


    analyzer = Analyze(args.db, args.dir, args.nvk_token, args.pio_token)

    if args.mode == 'scan':
        analyzer.scan(args.type)
    elif args.mode == 'push_pio':
        analyzer.push_pio_all()
    else:
        analyzer.watch()
