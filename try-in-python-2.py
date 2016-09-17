#!/usr/bin/python

import time

"""
thoughts/concerns:
* when starting the web server and script at ~ the same time, my tool's current iteration reaches the end of file in 0.00025 secs and in 32 lines.
This means that in 10 seconds, theoretically my tool would read 1,280,000 lines.
Meanwhile, the web server only emits about 180 lines total in 10 seconds.
If I try to read the log files continuously, I end up with a race condition.
* Whenever my tool reaches EOF and opens file again to read, it starts from first line. This means that in cases where the current log file has not changed, many lines are re-read before reaching previous end point.
* in the previous iteration, I used EOF as an indicator that file was done being written to and to re-initiate line-by-line read of
current access.log. in reality EOF is agnostic and it's possible that my code reached the end of the file, while it was still being written to. so when line-by-line read repeats, it might start reading the same file over again at position 0.
* how to identify when file is still not done being written to?
* usually global variables are frowned upon, but I'm using one for @total_lines because it makes sense to me to edit the same variable inside the smaller function's scope.
* coordinating the create_report calls: should I use threading to spin off a "process" every 10 seconds  or stick to iterative logic?
* if I were to for some reason read the file concurrently, would the file marker be updated across calls?
* I use a recursive call to continue reading the current "access.log" if the end of one file is reached; but apparently this causes max recursion depth within 10 secs.
"""

def create_report():
    start_time = time.time()
    loop_timeout = time.time() + 0.1 # set loop timeout to 10s from now
    total_lines = 0

    # parse access.log till loop_timeout
    total_lines = parse_log(start_time, total_lines, loop_timeout)
    print("parsed log")

    # create report
    report_file = "report"
    with open(report_file, "w") as file:
        file.write(str(total_lines))

    print("finished")

def parse_log(start_time, total_lines, loop_timeout):
    loop_ctr = 0
    #while time.time() < loop_timeout:
    while loop_ctr < 3:
        with open("logs/access.log", "r") as file:
            for line in file:
                print line
                print time.time()
                print loop_timeout
                if time.time() > loop_timeout:
                    return total_lines
                total_lines += 1
                print("read a line total is", total_lines)
            # if end of file is reached within loop_timeout, recall parse_log
            print("reached end of file")
            print (time.time() - start_time), "seconds elapsed"
            print (loop_timeout - time.time()), "seconds to go before timeout"
        loop_ctr += 1
            # parse_log(total_lines, loop_timeout)

def add_to_report(string):
    with open("report", "a") as file:
        file.write('\n')
        file.write(string)

create_report()
