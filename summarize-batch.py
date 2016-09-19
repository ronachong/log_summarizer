#!/usr/bin/python

import subprocess
import time
import sys

def parse_line(line):
    global requests

    try:
        parsed_line = line.split('\t')
        route = parsed_line[1].split(' ')[1]
        status = parsed_line[2]
        requests.add_request(route, status)
        # subprocess.call(["echo", line[:-1]]) <-- toggle for troubleshooting

    except(IndexError):
        # index error might arise if EOF is reached
        logfile.close()


class RequestsBatch:
    def __init__(self):
        self.total = 0
        self.routes = {}

    def add_request(self, route, status):
        if route not in self.routes.keys():
            self.routes[route] = {}
        if status not in self.routes[route].keys():
            self.routes[route][status] = 0
        self.routes[route][status] += 1

def print_report():
    global requests
    print subprocess.check_output(["date"]), "============================="
    # this can be converted to list comprehensions later
    for route in requests.routes.keys():
        for status_code in requests.routes[route].keys():
            print route, '\t', status_code, '\t', requests.routes[route][status_code]
    print "total\t", requests.total, '\n'

# Main
logfile = open(sys.argv[1], "r")     # open access.log for reading
requests = RequestsBatch()

for line in logfile:
    requests.total += 1
    parse_line(line)

print_report()
