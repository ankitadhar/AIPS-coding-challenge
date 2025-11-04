# AIPS Coding Challenge

## Solution
The final solution contains 3 main python files: main.py, traffic_analysis.py, model.py

To execute run the `main.py` file.
You can provide the input file from command line as:
```
python3 main.py --inputfile data/test_data.txt
```

if --inputfile is provided then the file will processed in the program, 
else the default file at `data/data.txt` will be processed to generate output.

## The Task
An automated traffic counter sits by a road and counts the number of cars that go
past. Every half-hour the counter outputs the number of cars seen and resets the counter
to zero. You are part of a development team that has been asked to implement a system to
manage this data - the first task required is as follows:

Write a program that reads a file, where each line contains a timestamp (in yyyy-mm-
ddThh:mm:ss format, i.e. ISO 8601) for the beginning of a half-hour and the number of

cars seen that half hour. An example file is included on page 2. You can assume clean
input, as these files are machine-generated.
The program should output:
• The number of cars seen in total
• A sequence of lines where each line contains a date (in yyyy-mm-dd format) and the
number of cars seen on that day (eg. 2016-11-23 289) for all days listed in the input file.
• The top 3 half hours with most cars, in the same format as the input file
• The 1.5 hour period with least cars (i.e. 3 contiguous half hour records)

## Constraints
• The program can be written in Java, Scala or Python, and with any libraries you are
familiar with. You are encouraged to use modern versions of each language and make
use of their features.
• The program must be accompanied with reasonable levels of unit tests.
• The solution should be developed to professional standards, the code may be used and
extended by your teammates.
• The solution should be deliverable within a couple of hours - please do not spend
excessive amounts of time on this.
• Avoid over-engineering.

## Assessment
Your submission will be assessed on the following:
• Correctness of solution
• Readability and fluency of your code (including tests)
• Effectiveness of your tests
