#!/usr/bin/env python
"""Utility script to generate any number of factoids.
"""
import argparse
import json
from papilotte.mockdata import make_factoid

def make_factoids(num_of_factoids, base_url):
    "Yield `num_of_factoid` dictionaries."
    for i in range(1, num_of_factoids + 1):
        yield make_factoid(i, base_url)

def parse_args():
    """Parse command line args."""
    parser = argparse.ArgumentParser(
        description='Generate any number of factoids.')
    parser.add_argument('num', metavar="NUM_OF_FACTOIDS",
                        type=int, help='Number of factoids to generate.')
    parser.add_argument('-u', '--base-url', metavar="URL",
                default="https://localhost:5000/api",
                help="Base URL used for internal links. Defaults to 'https://localhost:5000/api")
    parser.add_argument('-l', '--one-line-per-factoid', 
            action='store_true',
            help='Write each factory as one long line (nice for reading in single factoids')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args() 
    if args.one_line_per_factoid:
        for factoid in make_factoids(args.num, args.base_url):
            print(json.dumps(factoid, indent=None))
    else:
        factoid_data = {"factoids": []}
        for factoid in make_factoids(args.num, args.base_url):
            factoid_data["factoids"].append(factoid)
        print(json.dumps(factoid_data, indent=2))