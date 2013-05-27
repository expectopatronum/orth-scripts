'''
Created on May 6, 2013

@author: verenahaunschmid
'''
import getopt
import sys
import Helper
import statsAboutFullSequenceList as stats

__doc__ = "usage: python recaptureStats.py -f <full> -d <domain> -a <taxA> -b <taxB>\n" \
"f: pairwise orthologs from full sequence run\n" \
"d: pairwise orthologs from domain run\n" \
"a: id list organism A\n" \
"b: id list organism B"

def main():
    try:
        
        opts, args = getopt.getopt(sys.argv[1:], "hf:d:a:b:", ["help", "full", "domain", "taxA", "taxB"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    fullfile = ""
    domainfile = ""
    taxA = ""
    taxB = ""
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in("-f", "--full"):
            fullfile = a
        elif o in ("-d", "--domain"):
            domainfile = a
        elif o in ("-a", "--taxA"):
            taxA = a
        elif o in ("-b", "--taxB"):
            taxB = a
    
    fullPairs = Helper.readPairwise(fullfile)
    domainPairs = Helper.readPairwise(domainfile)
    organismA = Helper.readList(taxA)
    organismB = Helper.readList(taxB)
    
    orphansA = organismA
    orphansB = organismB
    
    for pair in fullPairs:
        if pair.first in orphansA:
            orphansA.remove(pair.first)
        if pair.second in orphansB:
            orphansB.remove(pair.second)
    
    for pair in domainPairs:
        if pair.first in orphansA:
            orphansA.remove(pair.first)
        if pair.second in orphansB:
            orphansB.remove(pair.second)
    
    filepath = "/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/"
    
    orgAname = taxA.split(".")[0].split("/")[-1]
    orgBname = taxB.split(".")[0].split("/")[-1]
    
    outputcsv = filepath + "orphanstats.csv"
    stats.doStatistics(orphansA, outputcsv)
    stats.doStatistics(orphansB, outputcsv)

    outputA = filepath+"Orphans/Orphans"+orgAname+"From"+orgAname+orgBname+"Run.txt"
    outputB = filepath+"Orphans/Orphans"+orgBname+"From"+orgAname+orgBname+"Run.txt"
    
    Helper.writeListToFile(orphansA, outputA)
    Helper.writeListToFile(orphansB, outputB)
    
if __name__ == '__main__':
    main()