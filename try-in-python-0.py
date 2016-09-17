#!/usr/bin/python

import time

"""
thoughts/concerns:
* this iteration assumes that reading a whole file can get interrupted by the loop timeout; in actuality reading 140 lines gets done in less than a second. on the other hand, if create_report is continuously reading files, one after another, it's possible that the timeout will still interrupt a read process. it's also likely that create_report will read things faster they're written to.
* usually global variables are frowned upon, but I wanted to use one for @total_lines because it makes sense to me to edit the same variable inside the smaller function's scope.
* coordinating the create_report calls: should I use threading to spin off a "process" every 10 seconds  or stick to iterative logic?
* if I were to for some reason read the file concurrently, would the file marker be updated across calls?
* I use a recursive call to continue reading the current "access.log" if the end of one file is reached; but apparently this causes max recursion depth within 10 secs.
"""

def create_report():
    total_lines = 0
    loop_timeout = time.time() + 1 # set loop timeout to 10s from now

    # parse access.log till loop_timeout
    total_lines = parse_log(total_lines, loop_timeout)
    print("parsed log")

    # create report
    report_file = "report"
    with open(report_file, "w") as file:
        file.write(str(total_lines))

    print("finished")

def parse_log(total_lines, loop_timeout):
    with open("logs/access.log", "r") as file:
        for line in file:
            print time.time()
            print loop_timeout
            if time.time() > loop_timeout:
                return total_lines
            total_lines += 1
            print("read a line total is", total_lines)
        # if end of file is reached within loop_timeout, recall parse_log
        # print("reached end of file")
        # parse_log(total_lines, loop_timeout)

create_report()
