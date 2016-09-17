#!/bin/bash
line=0

while read line
do
    echo "$line" > summary
done < "$input"

# problems:
# not aware of a way to write a function in bash, so file has to be passed
# as input;
# this while loop has to be called inside another while loop that keeps going
# for 10 seconds, as long as there's another line in the file (the problem of
# making sure all lines in each log file gets read)
# then this double while loop things has to be called again with the NEW file
# as the input.
