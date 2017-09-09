#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This is the conductor script for the psychology experiments.

Usage:


It creates a file called experiments_inprogress.txt if its not already there, that is a list of what experiments are going to be run. After an experiment has been performed, it saves this in a file called experiments_completed.txt with a timestamp.

"""

import time
import numpy as np
import os
import sys

NR_SUBJECTS = 100

IN_PROGRESS_FILE = "./experiments_inprogress.txt"
COMPLETED_FILE = "./experiments_completed.txt"

COMMAND_A = "~/hansonrobotics/private_ws/scripts/robot.sh lai --autobody --stt --layout --tracker realsense >> log"
COMMAND_B = "~/hansonrobotics/private_ws/scripts/robot.sh sophia6 --autobody --stt --layout --tracker realsense >> log"
COMMAND_STOP = "~/hansonrobotics/private_ws/scripts/stop.sh && ~/hansonrobotics/opencog/loving-ai/stop.sh >> log"

try:
    fobj = open(IN_PROGRESS_FILE)
    runs = np.genfromtxt(IN_PROGRESS_FILE, delimiter="\n")
except:
    print("No experiment in progress. Creating the file specifying the mapping.")
    runs = []
    while len(runs)<NR_SUBJECTS:
        if np.random.rand() > 0.5:
            runs.append(1)
            runs.append(0)
        else:
            runs.append(0)
            runs.append(1)
    np.savetxt(IN_PROGRESS_FILE, runs, delimiter="\n")

runs = runs

participant_nr = int(sys.argv[1])

raw_input("Press Enter to launch experiment for participant %d or CTRL-C to quit..." % participant_nr)

current_experiment = runs[participant_nr+1]

print("Conducting Experiment...")

### CONDUCT THE EXPERIMENT
if current_experiment:
    #print(COMMAND_A)
    os.system(COMMAND_A)
else:
    #print(COMMAND_B)
    os.system(COMMAND_B)

raw_input("Press Enter to complete experiment...")

#print(COMMAND_STOP)
os.system(COMMAND_STOP)
os.system(COMMAND_STOP)

try:
    f=open(COMPLETED_FILE, "a+")
    f.write("Conducted participant %d, experiment %d on %s\n" % (participant_nr, current_experiment, time.strftime("%c")))
    f.close()
except:
    print("Read Write error. Check if you have permissions here.")
