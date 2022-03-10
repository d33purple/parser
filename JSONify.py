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
    def __init__(self, name, ip):
        self.name = name
        self.subjectAlternateNames = []
        self.clientauth = "false"
        self.requestor = "staticuser"

        # populate the subjectAlternateNames now
        self.subjectAlternateNames.append(ip)

    # used when adding a cluster to this entry
    def add_cluster(self, name, ip):

        # cluster name gets inserted after other cluster names
        # we can calculate the correct position easily
        # and insert there
        if len(self.subjectAlternateNames) == 1:
            pos = 0
        else:
            pos = int((len(self.subjectAlternateNames) - 1) / 2)

        self.subjectAlternateNames.insert(pos,name)     

        # while cluster IP gets inserted to back of list
        self.subjectAlternateNames.append(ip)

    # override the print methods to return json for this object
    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def encode(self):
        return self.__dict__


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
        rex = re.search("(\d+\.\d+\.\d+.\d+)", entry)
        if rex:
            ip = rex.group(1).strip()
        logging.debug("ip is {0}".format(name))
        return ip

    except Exception as e:
        print("Caught exception in getname : {0}".format(e))

# not used right now
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

    # check file path is correct
    if not os.path.exists(args.path):
        throw("{0] is an invalid file path!".format(args.path))

    # open file and parse line by line
    with open(args.path) as file:
        for line in file:

            # sanitize the line, we have some \t characters hanging out
            line = line.replace("\t", " ")

            # check if this line is a valid entry
            if re.search("^\w+\s.*\s+\d+\.\d+\.\d+\.\d+\s.*$", line.strip()):
                name = getname(line.strip())
                ip = getip(line.strip())

                # determine whether this is a cluster instance or not
                # cluster instances have a -a,-b,-c, etc format at end of name
                if re.search("-\w$", name):
                    logging.debug("Adding cluster instance for {0}".format(name))

                    # pull name from cluster name; this pulls out everything but the -a, -b, etc.
                    # so we can organize the cluster name under the correct hoe
                    rex = re.search("(.*)-\w$", name)
                    if rex:
                        parentname = rex.group(1).strip()
                    else:
                        throw("Unable to parse parent name from cluster name!")

                    # add the cluster to the parent
                    JSON[parentname].add_cluster(name, ip)

                # this is not a cluster instance, add it
                else:
                    JSON[name] = Entry(name, ip)

    # Need to decide we want to print the data
    # If user requested a single node, we print that
    # else we print everything

    if args.query:
        if args.query in JSON.keys():
            print(JSON[args.query])
        else:
            print("entry [{0}] was not found!".format(args.query))
    else:

        # enable if you want to dump dictionary as single JSON dump
        #print(json.dumps(JSON, default=lambda o: o.encode(), indent=4))

        # iterate dictionary and print all the values as JSOn
        for key in JSON:
            print(JSON[key])

except Exception as e:

    print("Caught exception {0}".format(e))