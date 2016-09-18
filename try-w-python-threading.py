#!/usr/bin/python

import threading
import subprocess
import time
import signal

"""
thoughts/concerns:
* when starting the web server and script at ~ the same time, my tool's current iteration reaches the end of file in 0.00025 secs and in 32 lines.
This means that in 10 seconds, theoretically my tool would read 1,280,000 lines.
Meanwhile, the web server only emits about 180 lines total in 10 seconds.
If I try to read the log files continuously, I end up with a race condition.
* Whenever my tool reaches EOF and opens file again to read, it starts from first line. This means that in cases where the current log file has not changed, many lines are re-read before reaching previous end point.
This tells me that I need to figure out a tracking mechanism for writes so that I only read whenever a line is written.
* in the previous iteration, I used EOF as an indicator that file was done being written to and to re-initiate line-by-line read of
current access.log. in reality EOF is agnostic and it's possible that my code reached the end of the file, while it was still being written to. so when line-by-line read repeats, it might start reading the same file over again at position 0.
* how to identify when file is still not done being written to?
* usually global variables are frowned upon, but I'm using one for @total_lines because it makes sense to me to edit the same variable inside the smaller function's scope.
* coordinating the create_report calls: should I use threading to spin off a "process" every 10 seconds  or stick to iterative logic?
* if I were to for some reason read the file concurrently, would the file marker be updated across calls?
* I use a recursive call to continue reading the current "access.log" if the end of one file is reached; but apparently this causes max recursion depth within 10 secs.
"""

class MonitoringThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True <-- this daemonizes thread to run forever

    def run(self):
        start_time = time.time()
        prev = self.check_log()
        # while True:
        while time.time() - start_time < 3:
            line_count = self.check_log()
            if line_count != prev:
                print "new line added"
                thread = ParsingThread()
                thread.start()
            prev = line_count


    def check_log(self):
        line_count = subprocess.check_output(["wc", "-l", access_log])
        return line_count

class ParsingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # do stuff here to parse a line
        global total_lines

        total_lines += 1
        print "total lines are", total_lines
        # line = logfile.readline()

class ReportingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # thread.deamon = True <-- this daemonizes thread to run forever

    def run(self):
        start_time = time.time()
        # while True:
        while time.time() - start_time < 3.25:
            time.sleep(1)
            self.print_report()

    def print_report(self):
        global total_lines

        print total_lines
        print "interval elapsed: total lines are", total_lines
        total_lines = 0

# Main
access_log = "logs/access.log"  # specify path of log to monitor here
logfile = open(access_log, "r")    # open access.log for reading
total_lines = 0

try:
    read_master = MonitoringThread()
    read_master.start()
    signal.pause()
except (KeyboardInterrupt, SystemExit):
    print '\n! Received keyboard interrupt; quitting read_master thread.\n'


report_master = ReportingThread()
report_master.start()
