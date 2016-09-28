# 4) By using this cron log: https://s3.amazonaws.com/holbertonintranet/files/sandbox/cron
# Please provide the list of all cron commands with the delay ("The cron task 'Holberton' is executed each 50 seconds")

import fileinput
import datetime

def add_job(job, timestamp):
    global jobs
    if job not in jobs:
        jobs[job] = []
    jobs[job].append(timestamp)

def parse_timestamp(timestamp):
    struct_time = datetime.datetime.strptime(timestamp, "%b %d %H:%M:%S")
    # return time.mktime(struct_time)
    return struct_time

# MAIN
jobs = {}

for entry in fileinput.input():
    entry = entry.split('(root)')
    if len(entry) == 1:
        print entry
    else:
        timestamp = entry[0].split(' ip')[0]
        add_job(entry[1], timestamp)

for job in jobs:
    interval = parse_timestamp(jobs[job][1]) - parse_timestamp(jobs[job][0])
    print job[:-1], interval
    print ""
