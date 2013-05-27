'''
Created on Apr 23, 2013

@author: verenahaunschmid
'''

import sys
import getopt
from collections import namedtuple

OrthologPair = namedtuple("OrthologPair", ["first", "second"]) #remove if Helper is used

__doc__ = "usage: python mapIdsToUniprot -m <mapping file> -f <file containing ids> [-p if pairwise>]"

def readMappingFile(filename):
    idmap = {}
    handle = open(filename, "r")
    
    for line in handle.readlines():
        splitted = line.split("\n")[0].split()
        pid = splitted[2]
        if pid.startswith("yli:"):
            pid = pid[4:]
        idmap[pid] = splitted[0]
    
    handle.close()
    return idmap

def readPairs(filename): #remove if Helper is used
    pairs = []
    handle=open(filename, "r")
    for line in handle.readlines():
        splitted = line.split("\n")[0].split()
        pairs.append(OrthologPair(first=splitted[0], second=splitted[1]))
    handle.close()
    return pairs

def readIds(filename):
    ids = []
    handle = open(filename, "r")
    for line in handle.readlines():
        ids.append(line.split("\n")[0])
    handle.close()
    return ids

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:f:p", ["help", "mapping", "file", "pairwise"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    filename = ""
    mapping = ""
    pairwise = False
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-f", "--file"):
            filename = a
        elif o in ("-m", "--mapping"):
            mapping = a
        elif o in ("-p", "--pairwise"):
            pairwise=True
    
    
    fileA = readMappingFile(mapping)    
    
    if pairwise:
        ids = readPairs(filename)
        mapped = []
        for pair in ids:
            mapA = pair.first
            mapB = pair.second
            if pair.first in fileA:
                mapA = fileA[pair.first]
            if pair.second in fileA:
                mapB = fileA[pair.second]
            
            mapped.append(OrthologPair(first=mapA, second=mapB)) 

            if pair.first not in fileA and pair.second not in fileA:
                print "both", pair.first, pair.second
            elif pair.first not in fileA:
                print "1", pair.first, pair.second
            elif pair.second not in fileA:
                print "2", pair.first, pair.second
        
        # yli: fuer YALI

        outname = ""
        if filename.count(".") > 0:
            outname = "".join(filename.split(".")[:-1]) + ".map.txt"
        else:
            outname = filename + ".map.txt"
        out = open(outname, "w")

        for pair in mapped:
            out.write(pair.first + "\t" +  pair.second + "\n")
    else:
        ids = readIds(filename)
        mapped=[]
        for acc in ids:
            if acc in fileA:
                mapped.append(fileA[acc])
        print len(mapped), "/", len(ids)
        for acc in mapped:
            print acc
        
        
if __name__ == '__main__':
    main()