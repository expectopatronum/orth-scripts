'''
Created on Apr 25, 2013

@author: verenahaunschmid
'''

import sys
import getopt
from collections import namedtuple
import Helper
import os

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:b:", ["help", "fileA", "fileB"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    fileA = ""
    fileB = ""
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-a", "--afile"):
            fileA = a
        elif o in ("-b", "--bfile"):
            fileB = a

    pairsA = Helper.readPairwise(fileA)
    pairsB = Helper.readPairwise(fileB)
    
    # union, intersection, difference (both directions)
    unionAB = Helper.union(pairsA, pairsB)
    intersectAB = Helper.intersect(pairsA, pairsB)
    differenceAB = Helper.difference(pairsA, pairsB)
    differenceBA = Helper.difference(pairsB, pairsA)
    
    print "A", len(pairsA)
    print "B", len(pairsB)
    print "union", len(unionAB)
    print "intersect", len(intersectAB)
    print "A \ B", len(differenceAB)
    print "B \ A", len(differenceBA)

    outcsv = "/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/Comparison/pairlistcomparisondata.csv"
    if not os.path.exists(outcsv):
        out = open(outcsv, "w")
        out.write(";".join(["fileA", "fileB", "pairsA", "pairsB", "union", "intersect", "A \ B", "B \ A"]))
        out.write("\n")
        out.close()
    out = open(outcsv, "a")
    line = ";".join([fileA, fileB, str(len(pairsA)), str(len(pairsB)), str(len(unionAB)), str(len(intersectAB)), str(len(differenceAB)), str(len(differenceBA))])
    out.write(line+"\n")
    out.close()
    
if __name__ == '__main__':
    main()
    
