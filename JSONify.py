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
    def __init__(self, hostname, ip):

        # when setting hostname, add fqdn
        self.hostname = "{0}.garmin.com".format(hostname)
        self.subjectAlternateNames = []
        self.clientauth = "false"
        self.requestor = "staticuser"

        # populate the subjectAlternateNames now
        self.subjectAlternateNames.append(ip)

    # used when adding a cluster to this entry
    def add_cluster(self, hostname, ip):

        # cluster hostname gets inserted after other cluster hostnames
        # we can calculate the correct position easily
        # and insert there
        if len(self.subjectAlternateNames) == 1:
            pos = 0
        else:
            pos = int((len(self.subjectAlternateNames) - 1) / 2)

        # when adding alternate names, add fqdn
        self.subjectAlternateNames.insert(pos, "{0}.garmin.com".format(hostname))     

        # while cluster IP gets inserted to back of list
        self.subjectAlternateNames.append(ip)

    # override the print methods to return json for this object
    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def encode(self):
        return self.__dict__


def gethostname(entry):
    # retreives a node hostname from entry string
    try:
        logging.debug("gethostname: /{0}/".format(entry))
        hostname = "unknown"
        # run regex putting hostname in match group
        rex = re.search("^\w+\s+([\w\d\-\._]*)", entry)
        if rex:
            hostname = rex.group(1).strip()
        logging.debug("hostname is {0}".format(hostname))
        return hostname

    except Exception as e:
        print("Caught exception in gethostname : {0}".format(e))


def getip(entry):
    # retreives the IP from entry string
    try:
        logging.debug("getip: /{0}/".format(entry))
        ip = "unknown"
        # run regex putting ip in match group
        rex = re.search("(\d+\.\d+\.\d+\.\d+)", entry)
        if rex:
            ip = rex.group(1).strip()
        logging.debug("ip is {0}".format(ip))
        return ip

    except Exception as e:
        print("Caught exception in getip : {0}".format(e))

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
        logging.debug("version is {0}".format(version))
        return version

    except Exception as e:
        print("Caught exception in getversion : {0}".format(e))

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
                hostname = gethostname(line.strip())
                ip = getip(line.strip())

                # determine whether this is a cluster instance or not
                # cluster instances have a -a,-b,-c, etc format at end of hostname
                if re.search("-\w$", hostname):
                    logging.debug("Adding cluster instance for {0}".format(hostname))

                    # pull hostname from cluster hostname; this pulls out everything but the -a, -b, etc.
                    # so we can organize the cluster hostname under the correct parent node
                    rex = re.search("(.*)-\w$", hostname)
                    if rex:
                        parenthostname = rex.group(1).strip()
                    else:
                        throw("Unable to parse parent hostname from cluster hostname!")

                    # add the cluster to the parent
                    JSON[parenthostname].add_cluster(hostname, ip)

                # this is not a cluster instance, add it
                else:
                    JSON[hostname] = Entry(hostname, ip)

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