#!/usr/bin/env python
import json
import logging
import sys
import argparse
import importlib
import os
import signal
import requests


def signal_handler(signal, frame):
    sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)

def is_valid_file(parser, arg, result):
    if not os.path.exists(arg):
       if not os.path.exists("{0}/{1}".format(os.path.dirname(os.path.abspath(__file__),arg))
          parser.error("The file %s does not exist!" % arg)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argo data collector')
    parser.add_argument('-c', '--config', dest="config",
          required=True, help="config file", 
          type=lambda x: is_valid_file(parser, x, x))
    parser.add_argument('-i', '--input', dest="input",
          required=True, help="input module", 
          type=lambda x: is_valid_file(parser, x+"_module.py", x+"_module"))
    parser.add_argument('-o', '--output', dest="output",
          required=True, help="output module", 
          type=lambda x: is_valid_file(parser, x+"_module.py", x+"_module"))
    parser.add_argument('--commit', dest='commit', action='store_true',
              help="commit increments to the configuration")
    parser.add_argument('--no-commit', dest='commit', action='store_false',
              help="don't commit increments to the configuration")

    parser.add_argument('--callback-url', dest='callback_url', help="url to call after nc file is fetched")
    parser.set_defaults(commit=True,callback_url=None)

    args = parser.parse_args()
    config = None
    with open(args.config, "r") as myfile:
        config = json.load(myfile)

    logging.basicConfig(filename=config["logfile"],
                       format="%(asctime)s %(message)s",
                       level=logging.INFO)

    input = importlib.import_module(args.input).create_instance(config)
    output = importlib.import_module(args.output).create_instance(config)

    for cfg,argo in input.produce(config): 
        print argo["source_url"]
        output.publish(argo)
        if args.commit:
            with open(args.config+".new", "w") as outfile:
                json.dump(cfg, outfile, indent=4)
            os.rename(args.config+".new",args.config)
        if args.callback_url:
           requests.get(args.callback_url)

