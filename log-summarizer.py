#!/usr/bin/python

"""Access log summarizer.

Running this script starts two threads: readd and reportd.

readd continuously monitors an access log, specified by the variable @logfile. This thread creates a parsing subthread to read one line, parse the same line, and update stats (stored in the @requests object) every time the line count of the logfile changes. If the logfile is rotated out, readd closes and reopens the file.

reportd prints a readout of the stats stored in the @requests object every 10 seconds, then resets those stats.

Currently, the commands to make these threads run in the background are commented out. Uncomment #readd.daemon = True and #reportd.daemon = True to make threads more daemon-like.

To run this script, make sure it is executable first by running
    chmod +x log-summarizer
Then run
    ./log-summarizer

Alternatively just run
    python ./log-summarizer
"""

import signal
import subprocess
import threading
import time


class MonitoringThread(threading.Thread):
    """Monitor new lines written to @logfile and parse each new line.

    Every time a new line is written to the specified log file, create a
    subthread to read one line, parse it, and update stats for the current
    report.
    """
    def __init__(self):
        """Initialize the thread object."""
        threading.Thread.__init__(self)

    def run(self):
        """Continuously monitor specified logfile; parse every new line."""
        self.set_cursor()           # ensure that reading begins at latest line
        prev = self.check_log()
        # whenever linecount of logfile changes,
        # start thread to read and parse line.
        '''
        Although starting a new thread to parse each line is
        resource-intensive, using threads prevents the parsing from
        inadvertently blocking the monitoring of the logfile (no new line will
        be missed).
        If it's possible to verify that parsing one line takes less time than a
        new write to the logfile, then it may make sense to call a parsing
        function instead creating a new thread to parse.
        Another possibility is to read and parse lines in batches to reduce the
        number of threads made, but this requires extra logic.
        '''
        while True:
            line_count = self.check_log()
            if line_count != prev:
                thread = ParsingThread()
                thread.start()
            prev = line_count

    def set_cursor(self):
        """Set cursor for reading to end of @logfile."""
        logfile.seek(0, 2)

    def check_log(self):
        """Return current line count of @logfile."""
        return subprocess.check_output(["wc", "-l", access_log])


class ParsingThread(threading.Thread):
    """Parse a logfile line for route and status; update stats for report."""
    def __init__(self):
        """Initialize the thread object."""
        threading.Thread.__init__(self)

    def run(self):
        """Update count of total requests; parse a line from the logfile."""
        global requests
        requests.total += 1
        self.parse_line()

    def parse_line(self):
        """Update requests object with status and route from a logfile line."""
        global requests
        global logfile

        # retrieve route and status from line; update requests object
        try:
            line = logfile.readline()
            parsed_line = line.split('\t')
            route = parsed_line[1].split(' ')[1]
            status = parsed_line[2]
            requests.add_request(route, status)

        # index error might arise if end of file is reached;
        # if so, close and switch to new logfile
        except(IndexError):
            logfile.close()
            logfile = open(access_log, "r")
            self.parse_line()


class ReportingThread(threading.Thread):
    """Print a report of request stats every 10 seconds."""
    def __init__(self):
        """Initialize the thread object."""
        threading.Thread.__init__(self)

    def run(self):
        """Every 10 seconds, print a report of current stats."""
        while True:
            time.sleep(10)
            self.print_report()

    def print_report(self):
        """Print a report of recent HTTP requests according to requests object."""
        global requests
        print subprocess.check_output(["date"]), "============================="
        # this could be converted to list comprehensions later, or values could
        # be stored in one string so as not to call print several times
        for route in requests.routes.keys():
            for status_code in requests.routes[route].keys():
                print route, '\t', status_code, '\t', requests.routes[route][status_code]
        print "total\t", requests.total, '\n'
        requests.reset()


class RequestsBatch:
    """An object representing all the requests logged over a period of time.

    Attributes:
        total (int): The total number of requests logged over a period of time.
        routes (dict): All the routes requested over a period of time.
            Format: route (str):status codes of requests to route (dict).
            Format of status codes: code (str): count of requests to route with
            given code (int).
    """
    def __init__(self):
        """Initialize the RequestsBatch object."""
        self.reset()

    def add_request(self, route, status):
        """Document a new request made to given route with given status code."""
        '''Because there is a potential conflict between this method and the
        reset method being called, it would make some sense to protect this
        operation with a lock, though adding and releasing the lock would bring
        some performance costs. So far no such conflicts have been observed,
        but if it ever becomes an issue, a lock could be implemented here.'''
        if route not in self.routes.keys():
            self.routes[route] = {}
        if status not in self.routes[route].keys():
            self.routes[route][status] = 0
        self.routes[route][status] += 1

    def reset(self):
        """Reset total line count and requested routes."""
        self.total = 0
        self.routes = {}


# Main
access_log = "access.log"      # specify path of log to monitor here
logfile = open(access_log, "r")     # open access.log for reading
requests = RequestsBatch()

readd = MonitoringThread()
#readd.daemon = True
readd.start()

reportd = ReportingThread()
#reportd.daemon = True
reportd.start()
