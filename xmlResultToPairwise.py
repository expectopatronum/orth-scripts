'''
Created on May 20, 2013

@author: verenahaunschmid
'''

import sys
import getopt
import ConfigParser
import Helper

__doc__ = "usage: python xmlResultToPairwise.py -i <inputfile>\n" \

def main():
    inputfile = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "inputfile"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
        for o, a in opts:
            if o in("-i", "--inputfile"):
                inputfile = a
                
    if len(inputfile) > 0:
        handle = open(inputfile, "r")
        content = handle.read.lines("\n")
        handle.close()
        started = False
        for line in content:
            if not started and line.startswith("  <groups"):
                started = True
            if started:
                print "bla"
        
if __name__ == '__main__':
    main()