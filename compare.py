import sys
import getopt
import Helper
from Helper import OrthologPair
#from classes import GeneLevelProtein
#from classes import DomainLevelProtein
from classes.GeneLevelProtein import GeneLevelProtein
from classes.DomainLevelProtein import DomainLevelProtein
import ConfigParser
import os

__doc__ = "usage: python compare.py -f <filename> -d <filename> -a <taxid organism 1> -b <taxid organism 2> -o <outputfilename> -w\n" \
    "f: result file of a gene level inparanoid run of pattern Output.<OrganismA>-<OrganismB>\n"  \
    "d: result file of a domain level inparanoid run of pattern Output.<OrganismA>-<OrganismB>\n" \
    "a, b: taxids for organisms A and B\n" \
    "o: path where compare results should be saved.\n" \
    "w: optional if id lists should be written"

rcp = ConfigParser.RawConfigParser()
rcp.read("orthology.cfg")

#OrthologPair = namedtuple("OrthologPair", ["first", "second"])

def mapDomainOrthologsToProteins(pairwiseDomains, domainsA, domainsB):
    
    def isMapped(mapping, pair):
        for entry in mapping:
            if pair.first == entry.first or pair.second == entry.second:
                return True
        return False 

    pairwiseFull = {}
    mapped = {}
    for pair in pairwiseDomains:
        if pairwiseDomains[pair] not in mapped:
            mapped[pairwiseDomains[pair]] = {}
        orthpair = OrthologPair(first=domainsA[pair.first.header].accession, second=domainsB[pair.second.header].accession)
        if orthpair not in mapped[pairwiseDomains[pair]]:
            mapped[pairwiseDomains[pair]][orthpair] = []
        if orthpair not in pairwiseFull:
            pairwiseFull[orthpair] = 1
            mapped[pairwiseDomains[pair]][orthpair].append(pair)
        elif not isMapped(mapped[pairwiseDomains[pair]][orthpair], pair):
            pairwiseFull[orthpair] += 1
            mapped[pairwiseDomains[pair]][orthpair].append(pair)
    return pairwiseFull

def findProteinsWhereAllDomainsInferOrthology(pairsFull, pairsDomains):
    allDomainsInfer = []
    notAll = []
    notAny = []
    for pair in pairsFull:
        if pair in pairsDomains:
            if pairsFull[pair] == pairsDomains[pair]:
                allDomainsInfer.append(pair)
            elif pairsFull[pair] > pairsDomains[pair]:
                notAll.append(pair)
            elif pairsFull[pair] < pairsDomains[pair]:
                print "Take a closer look at", pair, "in findProteinsWereAllDomainsInferOrthology(pairsFull, pairsDomains)"
        else:
            notAny.append(pair)
    return allDomainsInfer, notAll, notAny
            
# add length condition  
def findProteinsOrthologyOnlyByDomains(proteinsA, proteinsB, pairsDomains, pairsFull, taxidA, taxidB, cutoff):
    only = []
    other = [] #other contains accession ids of proteins that have no orthology but at least one domain of them has
 
    tsvA = Helper.initTsvForOrganism(taxidA)
    tsvB = Helper.initTsvForOrganism(taxidB)

    for pair in pairsDomains:
        if pair not in pairsFull:
            amount = min(len(tsvA[pair.first]), len(tsvB[pair.second]))
            if pairsDomains[pair] >= amount:
                only.append(pair)
            other.append(pair)
            
    return only
    #  for pair in pairsDomains:     

def addMinimumDomainCountToFullOrthologs(pairwise):    
    pairwiseCount = {}
    notTheSameA = []
    notTheSameB = []
    theSame = []
    for pair in pairwise:
        accPair = OrthologPair(first = pair.first.accession, second = pair.second.accession)
        if len(pair.first.domains) == len(pair.second.domains):
            theSame.append(len(pair.first.domains))
        else:
            notTheSameA.append(len(pair.first.domains))
            notTheSameB.append(len(pair.second.domains))
        pairwiseCount[accPair] = min(len(pair.first.domains), len(pair.second.domains))
    print len(theSame), "sequence pairs have the same amount of domains with a mean of", Helper.mean(theSame), "and a median of", Helper.median(theSame)
    print len(notTheSameA), "sequence pairs do not have the same amount of domains with a mean of", Helper.mean(notTheSameA), "/", Helper.mean(notTheSameB), "and a median of", Helper.median(notTheSameA), "/" , Helper.median(notTheSameB)
    return pairwiseCount
    
def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwf:d:o:a:b:", ["help", "write","ffile", "dfile", "ofile", "taxidA", "taxidB"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    
    fullfile = ''
    domainfile = ''
    outname = ''
    outputfile = ''
    tsvA = ''
    tsvB = ''
    taxA = ''
    taxB = ''
    write = False
    resultpath = ''

    ok = True    
    for opt, arg in opts:
        if opt in ("-f", "--ffile"):
            fullfile = rcp.get("Filepaths", "resultpath") + arg
        elif opt in ("-d", "--dfile"):
            domainfile = rcp.get("Filepaths", "resultpath") + arg
        elif opt in ("-o", "--ofile"):
            outname = arg
            outputfile = rcp.get("Filepaths", "comparisonpath") + arg + "/Comparison" + arg
            resultpath = rcp.get("Filepaths", "comparisonpath") + outname + "/"
            os.system("mkdir " + resultpath)
        elif opt in ("-a", "--taxidA"):
            tsvA = rcp.get("Filepaths", "tsvpath") + arg + ".tsv"
            taxA = arg
        elif opt in ("-b", "--taxidB"):
            tsvB = rcp.get("Filepaths", "tsvpath") + arg + ".tsv"
            taxB = arg
        elif opt in ("-w", "--write"):
            write = True
        else:
            ok = False
         
    if ok:
        
        if not write:
            "Option -w was not set."
               
        cutoff = rcp.getint("Options","domainlengthcutoff")

        #intialising
        proteinsA, proteinsB, orthologs, shortA, shortB = GeneLevelProtein.initGeneLevelProteins(fullfile, tsvA, tsvB, True)               
        domainsA, domainsB, orthologsD = DomainLevelProtein.initDomainLevelProteins(domainfile)
        
        #calc pairwise ortholog mappings
        print "pairwise orthology mappings ..."
        pairwise = Helper.pairwiseOrthologs(orthologs, proteinsA, proteinsB)
        print "pairwise domain orthology  mappings ..."
        pairwiseDomains = Helper.pairwiseOrthologs(orthologsD, domainsA, domainsB)
        
        #analysing stuff
        print "mapping domains to proteins ..."
        mapping = mapDomainOrthologsToProteins(pairwiseDomains, domainsA, domainsB)
        print "add counters to full sequence orthologs ..."
        counters = addMinimumDomainCountToFullOrthologs(pairwise)
        print "find proteins where all / not all / not any domains infer orthology ..."
        allDomains, notAll, notAny = findProteinsWhereAllDomainsInferOrthology(counters, mapping)
        print "find protein orthology only by domains ..."
        onlyByDomains = findProteinsOrthologyOnlyByDomains(proteinsA, proteinsB, mapping, counters, taxA, taxB, cutoff)
        
        print "start filtering ..."
        # run length filter
        filteredOnlyByDomains = Helper.filterDomainOrthologyByLength(onlyByDomains, taxA, taxB, 0.5)
        #filteredNotAny = Helper.filterDomainOrthologyByLength(notAny, taxA, taxB)
        filteredSome = Helper.filterDomainOrthologyByLength(notAll, taxA, taxB, 0.5)
        filteredAllDomains = Helper.filterDomainOrthologyByLength(allDomains, taxA, taxB, 0.5)
        
        filteredOnlyByDomains30 = Helper.filterDomainOrthologyByLength(onlyByDomains, taxA, taxB, 0.3)
        filteredSome30 = Helper.filterDomainOrthologyByLength(notAll, taxA, taxB, 0.3)
        filteredAllDomains30 = Helper.filterDomainOrthologyByLength(allDomains, taxA, taxB, 0.3)
        
        # print information
        outhandle = open(outputfile, 'w')
        #length = rcp.getfloat("Options", "mincombdomainlength") * 100  
        
        fullCount = len(counters)
        domainCount = len(mapping)
        
        outhandle.write("Basic information:\n")    
        outhandle.write(str(shortA) + " domains from organism A were shorter than " + str(cutoff) + "\n")
        outhandle.write(str(shortB) + " domains from organism B were shorter than " + str(cutoff) + "\n")
        outhandle.write(str(fullCount) + " ortholog pairs in the full sequence orthology set\n")
        outhandle.write(str(domainCount) + " ortholog pairs in the domain orthology set\n\n")
        
        def percentage(pairs):
            return str(float(len(pairs))/float(fullCount) * 100)
        
        outhandle.write("\nOrthology support information:\n")
        outhandle.write("50 / 30 % filter cutoff\n")
        outhandle.write(str(len(allDomains)) + " ortholog pairs that are also supported by all their domains - " + percentage(allDomains) + "%\n")
        outhandle.write(str(len(filteredAllDomains30)) + " when filtered (30) - "+ percentage(filteredAllDomains30) +"%\n")
        outhandle.write(str(len(filteredAllDomains)) + " when filtered (50) - " + percentage(filteredAllDomains) + "%\n")
        
        outhandle.write(str(len(notAll)) + " ortholog pairs that are not supported by all their domains - "+ percentage(notAll) +"%\n")
        outhandle.write(str(len(filteredSome30)) + " when filtered (30) - " + percentage(filteredSome30) + "%\n")
        outhandle.write(str(len(filteredSome)) + " when filtered (50)" + percentage(filteredSome) +"%\n")
        assert len(counters) - len(allDomains) - len(notAll) == len(notAny)
        outhandle.write(str(len(notAny)) + " ortholog pairs that were not supported by any domains - " + percentage(notAny) + "%\n")
        #outhandle.write(str(len(filteredNotAny)) + " when filtered\n")
        outhandle.write(str(len(onlyByDomains)) + " ortholog pairs that are supported by all their constituent domains but not by the full sequence - " + percentage(onlyByDomains) +"%\n")
        outhandle.write(str(len(filteredOnlyByDomains30)) + " when filtered (30) \n")
        outhandle.write(str(len(filteredOnlyByDomains)) + " when filtered (50) \n")
        outhandle.close()

        if write:
            # writing orthology groups to different files
            Helper.printPairsToFile(counters, resultpath+"FullSequencesOrthologs"+outname)
            Helper.printPairsToFile(pairwiseDomains, resultpath+"PairwiseDomains"+outname)
            Helper.printPairsToFile(mapping, resultpath+"DomainsMappedToProteins"+outname)
            
            Helper.printPairsToFile(allDomains, resultpath+"AllDomains"+outname)
            Helper.printPairsToFile(onlyByDomains, resultpath+"OnlyByDomains"+outname)
            Helper.printPairsToFile(notAny, resultpath+"NotAnyDomains"+outname)
            Helper.printPairsToFile(notAll, resultpath+"NotAllDomains"+outname)
            
            # filtered stuff
            
            Helper.printPairsToFile(filteredOnlyByDomains, resultpath+"FilteredOnlyByDomains"+outname)
            Helper.printPairsToFile(filteredAllDomains, resultpath+"FilteredAllDomains"+outname)
            Helper.printPairsToFile(filteredSome, resultpath+"FilteredNotAllDomains"+outname)
            Helper.printPairsToFile(filteredOnlyByDomains30, resultpath+"FilteredOnlyByDomains30"+outname)
            Helper.printPairsToFile(filteredAllDomains30, resultpath+"FilteredAllDomains30"+outname)
            Helper.printPairsToFile(filteredSome30, resultpath+"FilteredNotAllDomains30"+outname)

    else:
        print opts
        print __doc__
        sys.exit(0)

if __name__ == "__main__":
    main()
