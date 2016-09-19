#!/usr/bin/python

import threading
import subprocess
import time
import signal

"""
things to consider:
Is it possible for the script to raise an exception in the brief time between the current logfile being moved and the new logfile being placed? Currently I only open access.log upon starting the script and whenever EOF/index error occurs, but if reopening of access.log fires before new logfile is created, it could cause:

Traceback (most recent call last):
  File "./try-w-python-threading.py", line 96, in <module>
    logfile = open(access_log, "r")    # open access.log for reading
IOError: [Errno 2] No such file or directory: 'logs/access.log'

Is it problematic that my script only reads a line when a new line is written, but the cursor will be placed at the beginning of the file? For instance, if access.log is 50 lines in when my script starts, my script may end up reporting 50 lines behind real time traffic. <-- possible solution: finding position of written line and seeking one line behind it to report

My current method of pacing my reads is to monitor change in line count and read whenever line count changes. This requires a loop and may be resource intensive. Is it better to hook into the program and make a callback whenever the write to access.log occurs? Or does this require just as much CPU and memory?

My current organization is to have one monitoring thread, which fires off ephemeral subthreads whenever wc changes, and one reporting thread, which calls a print function every 10 seconds. What are the pros and cons of using threads instead of including all of the execution in one stream?
    makes sense to separate monitoring and reporting because both need to be happening semi-simultaneously/continuously/we don't want one process to block the other.
    why fire off subthreads to read and parse instead of using function calls? if two writes happen in very close conjunction, having threads to handle each read means that reads will happen for each write; reduces the potential of missing a write because the monitoring was held up while read code was executing.
    why use function calls to print each report instead of firing off subthreads? report prints only need to happen every 10 seconds, so execution "blocking" isn't as much of a concern with each print. still, using subthreads may result in closer to 10 second intervals than having 10 seconds between completion of print call and start of next print call (depends on how long it takes to compute each report print.)

    is there a cost to splitting things into threads, resource-wise?

    the classic concern with splitting things into threads is race-ish conditions. do my reads ever fail to update the cursor reliably in time for other reads/do I ever have two reads reading the same line by mistake? do my reset writes to requests.total or requests.routes ever fail because an update write is happening at the same time? for that matter, do I miss update writes between the report print and the reset call? should I implement mutexes/locks to prevent this possibility?

The current library I'm using is threading, but this only emulates the process of threading; operations do not truly run asynchronously. Does it make sense to switch to a library that truly does that? What ends up being the difference, in reality?

In the end, is it better to ensure absolute accuracy, and complicate the logic of the solution a lot as a result, or is it better to go with more straightforward/intuitive solution and have some inaccuracy in the output?

Probable improvements to code:
using the log formatting tool used in the webserver
using thread scheduling? instead of time.sleep
coming up with a more efficient way to store routes with status codes and counts/using list comprehensions

Still need to look into:
method for daemonizing script. do I only want to daemonize the threads, using thread.daemon = True? or do I want the whole script to be treated as a daemon, by placing a certain way in the system, or etc.?
"""

class MonitoringThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True <-- this daemonizes thread to run forever

    def run(self):
        start_time = time.time()
        prev = self.check_log()
        # while True:
        while time.time() - start_time < 30:
            line_count = self.check_log()
            if line_count != prev:
                thread = ParsingThread()
                thread.start()
            prev = line_count


    def check_log(self):
        return subprocess.check_output(["wc", "-l", access_log])

class ParsingThread(threading.Thread):
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
            subprocess.call(["echo", line])

        except(IndexError):
            # index error might arise if EOF is reached
            global logfile
            logfile.close()
            logfile = open(access_log, "r")
            self.parse_line()


class ReportingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True <-- this daemonizes thread to run forever

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
    def __init__(self):
        self.total = 0
        self.routes = {}

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
