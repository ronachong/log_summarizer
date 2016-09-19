#!/usr/bin/python

import threading
import subprocess
import time
import signal


class MonitoringThread(threading.Thread):
    """Monitor new lines written to @logfile and parse each new line."""
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True <-- # ! uncomment to set thread to run forever

    def run(self):
        start_time = time.time()    # ! remove this eventually
        self.set_cursor()
        prev = self.check_log()
        # while True:
        while time.time() - start_time < 30:    # ! remove this eventually
            line_count = self.check_log()
            if line_count != prev:
                thread = ParsingThread()
                thread.start()
            prev = line_count

    def set_cursor(self):
        # set cursor to end of file
        logfile.seek(0, 2)

    def check_log(self):
        return subprocess.check_output(["wc", "-l", access_log])


class ParsingThread(threading.Thread):
    """Parse a line for route and status; update stats for report."""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # do stuff here to parse a line
        global requests
        requests.total += 1
        self.parse_line()

    def parse_line(self):
        global requests

        try:
            line = logfile.readline()
            parsed_line = line.split('\t')
            route = parsed_line[1].split(' ')[1]
            status = parsed_line[2]
            requests.add_request(route, status)
            # subprocess.call(["echo", line[:-1]]) # ! remove eventually

        except(IndexError):
            # index error might arise if EOF is reached
            global logfile
            logfile.close()
            logfile = open(access_log, "r")
            self.parse_line()


class ReportingThread(threading.Thread):
    """Print a report of request stats every 10 seconds."""
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True      # ! uncomment to set thread to run forever

    def run(self):
        start_time = time.time()
        # while True:
        while time.time() - start_time < 30.25:
            time.sleep(10)
            self.print_report()

    def print_report(self):
        global requests
        print subprocess.check_output(["date"]), "============================="
        # this can be converted to list comprehensions later
        for route in requests.routes.keys():
            for status_code in requests.routes[route].keys():
                print route, '\t', status_code, '\t', requests.routes[route][status_code]
        print "total\t", requests.total, '\n'
        requests.reset()


class RequestsBatch:
    """An object representing all the requests logged over a period of time.

    Attributes:
        total (int): The total number of requests logged over a period of time.
        routes (dict): All the routes requested over a period of time. Format: route (str):status codes of requests to route (dict). Format of status codes: code (str): count of requests with given code (int).
    """
    def __init__(self):
        self.reset()

    def add_request(self, route, status):
        if route not in self.routes.keys():
            self.routes[route] = {}
        if status not in self.routes[route].keys():
            self.routes[route][status] = 0
        self.routes[route][status] += 1

    def reset(self):
        self.total = 0
        self.routes = {}


# Main
access_log = "logs/access.log"      # specify path of log to monitor here
logfile = open(access_log, "r")     # open access.log for reading
requests = RequestsBatch()

try:
    read_master = MonitoringThread()
    read_master.start()
    signal.pause()
except (KeyboardInterrupt, SystemExit):
    print '\n! Received keyboard interrupt; quitting read_master thread.\n'


report_master = ReportingThread()
report_master.start()
