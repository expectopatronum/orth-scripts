'''
Created on Mar 25, 2013

@author: verenahaunschmid
'''

import sys
import getopt
import Helper
from Helper import OrthologPair
from classes import DomainLevelProtein
from classes.DomainLevelProtein import DomainLevelProtein
from collections import namedtuple
import ConfigParser

DomainInfo = namedtuple('DomainInfo', ['accession', 'start', 'end'])

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:d:o:a:b:", ["help", "ffile", "dfile", "ofile", "taxidA", "taxidB"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    rcp = ConfigParser.RawConfigParser()
    rcp.read("orthology.cfg")
    
    resultpath = rcp.get("Filepaths", "resultpath")
    taxA = ""
    taxB = ""
    inputfile = ""
    outputname = ""
    dfile = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-a", "--taxidA"):
            taxA = a            
        elif o in ("-b", "--taxidB"):
            taxB = a           
        elif o in ("-f", "--ffile"):
            inputfile = resultpath + a
        elif o in ("-o", "--ofile"):
            outputname = a
        elif o in ("-d", "--dfile"):
            dfile = resultpath + a
        else:
            print "Didn't expect", o, a
            print __doc__
            sys.exit(2)
            
    tsvA = Helper.initTsvForOrganism(taxA)
    tsvB = Helper.initTsvForOrganism(taxB)
    
    allDomains = []
    countA = 0
    countB = 0
    handle = open(inputfile, "r")
    for line in handle.readlines():
        splitted = line.split()
        for entry in tsvA[splitted[0]]:
            d = DomainInfo(accession=entry.seqId, start=entry.alignmentStart, end=entry.alignmentEnd)
            if d not in allDomains:
                allDomains.append(d)
                countA += 1
        for entry in tsvB[splitted[1]]:
            d = DomainInfo(accession=entry.seqId, start=entry.alignmentStart, end=entry.alignmentEnd)
            if d not in allDomains:
                allDomains.append(d)
                countB += 1
    handle.close()
    
    domainsA, domainsB, orthologsD = DomainLevelProtein.initDomainLevelProteins(dfile)
    pairwiseDomains = Helper.pairwiseOrthologs(orthologsD, domainsA, domainsB)

    supportedDomains = []
    for pair in pairwiseDomains:
        d1 = DomainInfo(accession = pair.first.accession, start=pair.first.start, end=pair.first.end)
        d2 = DomainInfo(accession = pair.second.accession, start=pair.second.start, end=pair.second.end)
        
        if d1 in allDomains and d1 not in supportedDomains:
            supportedDomains.append(d1)
        if d2 in allDomains and d2 not in supportedDomains:
            supportedDomains.append(d2)

    #list_a = [n for n in list_a if n not in list_b]

    notSupportedDomains = [item for item in allDomains if item not in supportedDomains]
    
    print "A, B", countA, countB
    print "all domains", len(allDomains)
    print "supporting pairs", len(supportedDomains)
    print "not supporting pairs", len(notSupportedDomains)
    
    suppLength = 0
    outSupported = open(resultpath + outputname + "Supported.txt", "w")
    for domain in supportedDomains:
        outSupported.write(domain.accession + " " + str(domain.start) + " " + str(domain.end) + "\n")
        suppLength += (int(domain.end) - int(domain.start))
    outSupported.close()
    print "mean length of supporting domains:", float(suppLength) / float(len(supportedDomains))
    
    
    # why are start and end not ints?
    notSuppLength = 0
    outNotSupp = open(resultpath + outputname + "NotSupported.txt", "w")
    for domain in notSupportedDomains:
        outNotSupp.write(domain.accession + " " + str(domain.start) + " " + str(domain.end) + "\n")
        notSuppLength += (int(domain.end) - int(domain.start))
    outNotSupp.close()
    print "mean length of not supporting domains:", float(notSuppLength) / float(len(notSupportedDomains))

if __name__ == '__main__':
    main()