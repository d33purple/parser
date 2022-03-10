import os
import os.path
import re
import sys
import argparse
import threading
import logging
import json
from datetime import datetime

if os.path.exists("jsonify.log"):
    os.remove("jsonify.log")

logging.basicConfig(filename='jsonify.log', encoding='utf-8', level=logging.DEBUG)

JSON = {}


# Note we define the class with class members that mimic final JSON entries
# to make export to JSON seemless
class Entry:
    def __init__(self, hostname, ip, version):
        self.hostname = name
        self.subjectAlternateNames = []
        self.clientauth = "false"
        self.requestor = "staticuser"

        # populate the subjectAlternateNames now
        self.subjectAlternateNames.append(name)
        self.subjectAlternateNames.append(ip)

    # override the print methods to return json for this object
    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def encode(self):
        return self.__dict__

    # JSON serializer
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


def getname(entry):
    # retreives a node name from entry string
    try:
        logging.debug("getname: /{0}/".format(entry))
        name = "unknown"
        # run regex putting name in match group
        rex = re.search("^\w+\s+([\w\d\-\._]*)", entry)
        if rex:
            name = rex.group(1).strip()
        logging.debug("name is {0}".format(name))
        return name

    except Exception as e:
        print("Caught exception in getname : {0}".format(e))


def getip(entry):
    # retreives the IP from entry string
    try:
        logging.debug("getip: /{0}/".format(entry))
        ip = "unknown"
        # run regex putting ip in match group
        rex = re.search("(\d+.\d+\.\d+.\d+)", entry)
        if rex:
            ip = rex.group(1).strip()
        logging.debug("ip is {0}".format(name))
        return ip

    except Exception as e:
        print("Caught exception in getname : {0}".format(e))

def getversion(entry):
    # retreives the IP from entry string
    try:
        logging.debug("getversion: /{0}/".format(entry))
        version = "unknown"
        # run regex putting ip in match group
        rex = re.search("(\s([\w\d\-\._]+)$)", entry)
        if rex:
            version = rex.group(1).strip()
        logging.debug("version is {0}".format(name))
        return version

    except Exception as e:
        print("Caught exception in getname : {0}".format(e))

# SCRIPT ENTRY POINT
try:

    parser = argparse.ArgumentParser(
        description="Neinhalts JSONify script"
    )
    parser.add_argument(
        '-p',
        '--path',
        required=True,
        help="path to source file"
    )
    parser.add_argument(
        '-q',
        '--query',
         required=False,
        help="returns JSON for a single node"
    )
    args = parser.parse_args()

    print("JSONify.py")
    print("    --path     : {0}".format(args.path))
    print("    --query    : {0}".format(args.query))

    logging.debug("Starting")

    # check file path is correct
    if not os.path.exists(args.path):
        throw("{0] is an invalid file path!".format(args.path))

    # open file and parse line by line
    with open(args.path) as file:
        for line in file:
            # check if this line is a valid entry
            if re.search("^\w+\s.*\s+\d+\.\d+\.\d+\.\d+\s.*$", line.strip()):
                name = getname(line.strip())
                ip = getip(line.strip())
                version = getversion(line.strip())

                # add new class instance to list
                JSON[name] = Entry(name, ip, version)

    print("Parsed {0} nodes".format(len(JSON)))

    # Need to decide we want to print the data
    # If user requested a single node, we print that
    # else we print everything

    if args.query:
        if args.query in JSON.keys():
            print(JSON[args.query])
        else:
            print("entry [{0}] was not found!".format(args.query))
    else:

        print(json.dumps(JSON, default=lambda o: o.encode(), indent=4))



except Exception as e:

    print("Caught exception {0}".format(e))