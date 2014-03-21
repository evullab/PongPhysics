# Functions for parsing input

from __future__ import division

import sys

# inputConfig: Takes a file path and returns a dictionary associating config terms and values
# 

def inputConfig(filenm):
    cfile = open(filenm, 'r')
    cfig = {}
    for line in cfile:
        prt = line.partition(':')
        arg = prt[2].strip()
        if prt[1]=='':
            print("Error: Bad definition line: " + line)
            continue
        elif arg.isdigit():
            assoc = int(arg)
        else:
            if (arg.upper()=='T')|(arg.upper()=='TR')|(arg.upper()=='TRU')|(arg.upper()=='TRUE'):
                assoc = True
            elif (arg.upper()=='F')|(arg.upper()=='FA')|(arg.upper()=='FAL')|(arg.upper()=='FALS')|(arg.upper()=='FALSE'):
                assoc = False
            else:
                assoc = arg
        cfig[prt[0]]=assoc
    cfile.close()
    return (cfig)
