#!/usr/bin/env python

from analyzer.audio import Analyze
from argparse import ArgumentParser





if __name__ == '__main__':
    parser = ArgumentParser(description = """
Analyzes all audio files found (recursively) in a folder using MusicExtractor.
""")

    parser.add_argument('-d', '--dir', help='input directory', required=True)
    parser.add_argument('-db', '--db', help='mongo db uri', required=True)
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

    analyzer = Analyze(args.db, args.dir, args.nvk_token, args.pio_token)

    if args.mode == 'scan':
        analyzer.scan(args.type)
    elif args.mode == 'push_pio':
        analyzer.push_pio_all()
    else:
        analyzer.watch()
