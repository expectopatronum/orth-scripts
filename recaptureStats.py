'''
Created on Apr 29, 2013

@author: verenahaunschmid
'''

import sys
import getopt
import Helper
import os
from classes.BasicOrthologyGroup import BasicOrthologyGroup
import resultFileToPairs

__doc__ = "usage: python recaptureStats.py -f <resultfile> -a <taxid A> -b <taxid B>\n"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:a:b:", ["help", "file", "taxA", "taxB"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    filename = ""
    taxA = ""
    taxB = ""
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-f", "--file"):
            filename = a
        elif o in ("-a", "--taxA"):
            taxA = a
        elif o in ("-b", "--taxB"):
            taxB = a

    #===========================================================================
    # pairfile = ""
    # if filename.count(".") > 0:
    #    pairfile = "".join(filename.split(".")[:-1]) + ".pairs.txt"
    # else:
    #    pairfile = filename + ".pairs.txt"
    #===========================================================================
    
    pairfile = filename + ".pairs.txt"
    resultFileToPairs.resultfiletopairs(filename, pairfile)
    
    header = Helper.readHeaderFromResult(filename)

    dAB = float(header.proteinsA - header.inparalogsA) / float(header.proteinsA) * 100.0
    dBA = float(header.proteinsB - header.inparalogsB) / float(header.proteinsB) * 100.0
    
    print "distance AB", dAB
    print "distance BA", dBA


    domainsA = Helper.initTsvForOrganism(taxA)
    domainsB = Helper.initTsvForOrganism(taxB)
    pairs = Helper.readPairwise(pairfile)
    
    print len(pairs), "pairs"
    print len(Helper.unique(pairs)), "unique pairs"
    groups = BasicOrthologyGroup.buildGroupsFromPairs(pairs)
    print len(groups), "groups"
    canrecapture = []
    
    canrecapgroups = []
    cannotrecapgroups = []
    
    countsA = []
    lengthsA = []
    countsB = []
    lengthsB = []
    for group in groups:
        can = True
        cA = 0
        cB = 0
        for a in group.inparalogsA:
            if a not in domainsA:
                cA += 1
                can = False
        for b in group.inparalogsB:
            if b not in domainsB:
                cB += 1
                can = False
        countsA.append(cA)
        lengthsA.append(len(group.inparalogsA))
        countsB.append(cB)
        lengthsB.append(len(group.inparalogsB))
        if can:
            canrecapgroups.append(group)
        else:
            cannotrecapgroups.append(group)
    
    print sum(lengthsA), "inparalogs A"
    print sum(lengthsB), "inparalogs B"
    
    for pair in pairs:
        if pair.first in domainsA and pair.second in domainsB:
            canrecapture.append(pair)
    
    #===========================================================================
    # outname = ""
    # if filename.count(".") > 0:
    #    outname = "".join(filename.split(".")[:-1]) + ".recapturable.txt"
    # else:
    #    outname = filename + ".recapturable.txt"
    #===========================================================================
    outname = filename + ".recapturable.txt"
    
    countMissingA = 0
    countMissingB = 0
    for i in range(len(countsA)):
        if countsA[i] > 0:
            countMissingA += 1
        if countsB[i] > 0:
            countMissingB += 1 
                       
    inpA = []
    inpB = []
    for g in groups:
        for a in g.inparalogsA:
            assert (a not in inpA)
            inpA.append(a)
        for b in g.inparalogsB:
            assert(b not in inpB)
            inpB.append(b)
    
    notrecapgroups = len(groups)-len(canrecapgroups)
    
    recapable = str(len(canrecapture))
    missing = str(len(pairs)-len(canrecapture))
    meanA = str(Helper.mean(countsA))
    meanB = str(Helper.mean(countsB))
    recapgroups = str(len(canrecapgroups))
    modMeanA = "0"
    modMeanB = "0"
    if countMissingA > 0:
        modMeanA = str(float(sum(countsA))/float(countMissingA))
    if countMissingB > 0:    
        modMeanB = str(float(sum(countsB))/float(countMissingB))
    
    outcsv = "/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/recapturestats.csv"
    if not os.path.exists(outcsv):
        out = open(outcsv, "w")
        out.write(";".join(["taxA", "taxB", "dAB", "dBA", "pairs", "groups", "inparalogs_A", "inparalogs_B", "recappairs", "recapgroups", "avg_missing_A", "avg_missing_B", "missing_A", "missing_B", "mod_mean_A", "mod_mean_B"]))
        out.write("\n")
        out.close()
    out = open(outcsv, "a")
    line = ";".join([taxA, taxB, str(dAB), str(dBA), str(len(pairs)), str(len(groups)), str(sum(lengthsA)), str(sum(lengthsB)), recapable, recapgroups, meanA, meanB, str(countMissingA), str(countMissingB), modMeanA, modMeanB])
    out.write(line+"\n")
    out.close()
    
    Helper.printPairsToFile(pairs, outname)
    print recapable, "can be recaptured and", missing, "can't"
    print recapgroups, "groups can be recaptured and", notrecapgroups, "can't"
    print "on average", meanA, "A inparalogs are missing from a group"
    print "on average", meanB, "B inparalogs are missing from a group"
    print notrecapgroups, "groups can not be recaptured"
    print countMissingA, "groups miss at least one inparalog from organism A, on average", modMeanA
    print countMissingB, "groups miss at least one inparalog from organism B, on average", modMeanB

    
    #outnot = open("/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/InParanoid/AversusB/recap/notrecap.txt", "w")
        
    outnot = open(filename + ".notrecap.txt", "w")
    for group in cannotrecapgroups:
        outnot.write("-------\n")
        outnot.write("Inparalogs A:\n")
        for a in group.inparalogsA:
            outnot.write(a + "\n")
        outnot.write("InparalogsB:\n")
        for b in group.inparalogsB:
            outnot.write(b + "\n")
    
if __name__ == '__main__':
    main()