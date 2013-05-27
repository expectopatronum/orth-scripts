'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''
import sys
import getopt
import ConfigParser
import Helper
import operator
import os

__doc__ = "usage: python statsAboutFullSequnceList.py -i <idlist> -m <mode> -o <outpath> [-a <comparefileA> -b <comparefileB>]\n" \
    "i: list of accession ids\n" \
    "m: 1|2 (how many columns)" \
    "o: path to save clan infos" \
    "a, b: optional compare file to add percentages. cannot be used with mode 1."

rcp = ConfigParser.RawConfigParser()
rcp.read("orthology.cfg")

def doStatistics(idlist, outputcsv):
        seqlengths = Helper.getSequenceLengthsForAccessionsIds(idlist)
        tsvs = Helper.getTsvEntriesForIdList(idlist)
        
        domainCount = 0
        domainCountCutoff = 0
        domainCover = {}
        clanCount = {}
        
        cutoff = rcp.getint("Options", "domainlengthcutoff")
        
        lengths = []
        
        for seq in seqlengths:
            lengths.append(seqlengths[seq])
            domainlength = 0
            for domain in tsvs[seq]:
                domainlength = (domain.alignmentEnd - domain.alignmentStart)
                domainCount += 1
                if domainlength >= cutoff:
                    domainCountCutoff += 1
                if domain.clan not in clanCount:
                    clanCount[domain.clan] = 0
                clanCount[domain.clan] += 1
            domainCover[seq] = float(domainlength) / float(seqlengths[seq])

        if not os.path.exists(outputcsv):
            out = open(outputcsv, "w")
            out.write(";".join(["taxid", "lengthsum", "meanlength", "medianlength", "domaincount", "domaincountcutoff", "meanclans", "medianclans", "meancover", "mediancover"]))
            out.write("\n")
        
        meanClan = Helper.mean(list(clanCount.values()))
        medianClan = Helper.median(list(clanCount.values()))
        
        meanCover = Helper.mean(list(domainCover.values()))
        medianCover = Helper.median(list(domainCover.values()))
        
        lengthSum = str(sum(lengths))
        meanLength = str(Helper.mean(lengths))
        medianLength = str(Helper.median(lengths)) 
        
        out = open(outputcsv, "a")
        out.write(";".join([str(tsvs[tsvs.keys()[0]][0].tax), lengthSum, meanLength, medianLength, str(domainCount), str(domainCountCutoff), str(meanClan), str(medianClan), str(meanCover), str(medianCover)]))
        out.write("\n")
        
        print "lengthSum", lengthSum
        print "mean length", meanLength
        print "median length", medianLength
        print "domain count", domainCount
        print "domain count considering cutoff (", cutoff, ")", domainCountCutoff
        print "mean clans", meanClan
        print "median clans", medianClan
        print "mean coverage", meanCover
        print "median coverage", medianCover
        
        return clanCount

def read(handle):
    idlist = []
    for line in handle.readlines():
        idlist.append(line.split('\n')[0])       
    handle.close()
    return idlist
    
def readWithMode1(filename, output):
    idlist = read(filename)
    sortedClansA = doStatistics(idlist, output)
    return sortedClansA
    
def readWithMode2(handle, output):
    idlist1 = []
    idlist2 = []
    for line in handle.readlines():
        splitted = line.split('\n')[0].split()
        idlist1.append(splitted[0])
        idlist2.append(splitted[1])
    sortedClansA = doStatistics(idlist1, output)
    sortedClansB = doStatistics(idlist2, output)
    return sortedClansA, sortedClansB

def compare(source, organism):
    perc = {}
    for entry in organism:
        perc[entry] = float(organism[entry]) / float(source[entry]) * 100
    return perc

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:m:a:b:", ["help", "input", "output", "mode", "comparisona", "comparisonb"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    inputfile = ""
    outputfile = ""
    mode = ""
    compfileA = ""
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-i", "--input"):
            inputfile = a
            outputfile = "/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/orphanstats.csv"
        elif o in ("-o", "--output"):
            outputfile = a
        elif o in ("-m", "--mode"):
            mode = a
        elif o in ("-a", "--comparisona"):
            compfileA = a
        elif o in ("-b", "--comparisonb"):
            compfileB = a
    
    if len(inputfile) > 0 and mode in ("1", "2"):
        handle = open(inputfile, "r")
        unsortedClans = None
        unsortedClansA = []
        unsortedClansB = []
        
        if (mode == "1"):
            unsortedClans = readWithMode1(handle, outputfile)
            sortedClans = sorted(unsortedClans.iteritems(), key=operator.itemgetter(1))
            sortedClans.reverse()
            #===================================================================
            # outhandle = open(outputfile, "w")
            # for clan in sortedClans:
            #    outhandle.write(clan[0] + " " + str(clan[1]) + "\n")
            # outhandle.close()
            #===================================================================
        elif (mode == "2"):
            unsortedClansA, unsortedClansB = readWithMode2(handle)
            sortedClansA = sorted(unsortedClansA.iteritems(), key=operator.itemgetter(1))
            sortedClansA.reverse()
            sortedClansB = sorted(unsortedClansB.iteritems(), key=operator.itemgetter(1))
            sortedClansB.reverse()
            #===================================================================
            # percentagesA = {}
            # percentagesB = {}
            # if len(compfileA) > 0 and len(compfileB) > 0:
            #    sourceA = readWithMode1(compfileA)
            #    sourceB = readWithMode1(compfileB)
            #    percentagesA = compare(sourceA, unsortedClansA)
            #    percentagesB = compare(sourceB, unsortedClansB)
            #===================================================================
            
            #outhandle = open(outputfile, "w")

            #bc = ("off","on")[c.page=="blog"]
            #bc = 'on' if c.page=='blog' else 'off'
            #===================================================================
            # for clan in sortedClansA:
            #    outhandle.write(clan[0] + " " + str(clan[1]) + (" " + str(percentagesA[clan[0]])+"\n" if clan[0] in percentagesA else '\n'))
            # outhandle.write("#\n")
            # for clan in sortedClansB:
            #    outhandle.write(clan[0] + " " + str(clan[1]) + (" " + str(percentagesB[clan[0]])+"\n" if clan[0] in percentagesB else '\n'))
            # outhandle.close()
            #===================================================================
        
        handle.close()
    else:
        print __doc__
        sys.exit(2)

if __name__ == '__main__':
    main()