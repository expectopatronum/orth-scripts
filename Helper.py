import re
from classes import TsvEntry
import ConfigParser
import sqlite3
from collections import namedtuple

rcp = ConfigParser.RawConfigParser()
rcp.read("orthology.cfg")

OrthologPair = namedtuple("OrthologPair", ["first", "second"])

def retrieveAccessionNumber(idLine): #idLine looks like tr|Q9VCN5|Q9VCN5_DROME or Q197F8.1
    acc = idLine
    if not idLine.startswith("SP"): #dirty hack for spombe
        acc = idLine.split('.')[0]
    if '|' in acc:
        if not acc.split('|')[1].startswith("PF"):
            acc = acc.split('|')[1]
        else:
            acc = acc.split('|')[0]
    return acc

def retrieveDomainHeaderInformation(headerline):
    splittedLine = headerline.split('|')
    acc = ""
    start = ""
    end = ""
    domain = ""
    
    for entry in splittedLine:
        if entry.startswith("PF"):
            domain = entry
        elif entry.startswith("start:"):
            start = int(entry.split(":")[1])
        elif entry.startswith("end:"):
            end = int(entry.split(":")[1])
        else:
            match = re.match("[A-Z][0-9][A-Z0-9]{3}[0-9]((-([0-9]+)))", entry)
            if match != None:
                print entry
                acc = entry
    
    header = []
    header.append(acc)
    header.append(domain)
    header.append(start)
    header.append(end)
    assert len(header[:]) > 0
    return header
        
def mean(values):
    return float(sum(values))/float(len(values))

def median(values):
    values.sort()
    if len(values) % 2 == 1:
        return values[int(len(values) / 2)]
    else:
        return (values[int(len(values) / 2)] + values[int(len(values) / 2 + 1)]) / 2
    
def getRankAndScore(line):
    splittedLine = line.split('.')
    rank = splittedLine[0].split('#')[1]
    score = int(splittedLine[1].split()[2])
    return rank, score

def extractFromDb(ids):
    database = rcp.get("Filepaths", "databases") + rcp.get("Data", "fullsequencesdb")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    idlists = []
    for i in range(0, len(ids), 999):
        idlists.append(ids[i:i+999])
   
    mapping = {}
    for i in range(0, len(idlists)):
        #was "selected description, fasta ..." before, but i don't know why, changed it due to problems
        sql = "select title, fasta from fasta_storage where title in ({ids})".format(ids=','.join(['?']*len(idlists[i])))
        result = c.execute(sql, idlists[i])
        for row in result:
            mapping[row[0]] = row[1]
    return mapping

def getSequenceLengthsForAccessionsIds(ids):
    database = rcp.get("Filepaths", "databases") + rcp.get("Data", "fullsequencesdb")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    idlists = []
    mapping = {}
    
    for i in range(0, len(ids), 999):
        idlists.append(ids[i:i+999])

    for i in range(0, len(idlists)):
        sql = "select title, length(fasta) from fasta_storage where title in ({ids})".format(ids=','.join(['?']*len(idlists[i])))
        result = c.execute(sql, idlists[i])
        for row in result:
            mapping[row[0]] = row[1]
    return mapping

def initTsvForOrganism(taxid):
    database = rcp.get("Filepaths", "databases") + rcp.get("Data", "domaindb")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    organismdomains = {}
    cutoff = rcp.getint("Options", "domainlengthcutoff")
    result = c.execute("select * from tsv_storage where tax=:tax and (hmmType='Domain' or hmmType='Family') and alEnd - alStart>=:cutoff", 
    #result = c.execute("select * from tsv_storage where tax=:tax and alEnd-alStart >= :cutoff", # in case hmmType doesn't matter
                       {"tax":taxid, "cutoff":cutoff}).fetchall()
    
    for row in result:
        t = TsvEntry(row)
        if str(t.seqId) not in organismdomains:
            organismdomains[str(t.seqId)] = [] 
        organismdomains[str(t.seqId)].append(t)
        
    c.close()
    return organismdomains

def getTsvEntriesForIdList(ids):
    database = rcp.get("Filepaths", "databases") + rcp.get("Data", "domaindb")
    conn = sqlite3.connect(database)
    c = conn.cursor()
    
    idlists = []
    for i in range(0, len(ids), 999):
        idlists.append(ids[i:i+999])
    
    mapping = {}
    for i in range(0, len(idlists)):
        sql = "select * from tsv_storage where seqId in ({ids})".format(ids=','.join(['?']*len(idlists[i])))
        result = c.execute(sql, idlists[i])

        for row in result:
            t = TsvEntry(row)
            if t.seqId not in mapping:
                mapping[t.seqId] = []
            mapping[t.seqId].append(t)
    return mapping      

def getDomainsFromTsv(tsvfile, cutoff):
    
    domains = {}
    tsvIn = open(tsvfile, 'r')
    short = 0
    for line in tsvIn.readlines():
        if not line.startswith('#') and not line.startswith(">"):
            splittedLine = line.split()
            if len(splittedLine) > 1 and splittedLine[7] in ('Domain', 'Family'): # or True?
                accession = retrieveAccessionNumber(splittedLine[0]) 
                start = splittedLine[1] # using alignment start and end
                end = splittedLine[2] # envelope start and end would be indeces 3 and 4
                if int(end) - int(start) >= cutoff:
                    if accession not in domains:
                        domains[accession] = []
                    domains[accession].append([int(start), int(end), splittedLine[5]])
                else:
                    short += 1
                    # example: domains["C3U398"] = [[304, 358],[229, 283]]
                    # sequence with id C3U398 has 2 domains at above mentioned positions
    #print short, "were too short"
    return domains, short    

def removeDuplicates(sequence):
    # not order preserving - source: http://www.peterbe.com/plog/uniqifiers-benchmark
    ordset = {}
    map(ordset.__setitem__, sequence, [])
    return ordset.keys()

def pairwiseOrthologs(orthologs, proteinsA, proteinsB):       
    pairwise = {}   
    for o in orthologs:
        for a in orthologs[o].inparalogsA:
            for b in orthologs[o].inparalogsB:
                pair = OrthologPair(first=proteinsA[a], second=proteinsB[b])
                pairwise[pair] = orthologs[o]
    return pairwise

def filterDomainOrthologyByLength(domainpairs, taxA, taxB, length):

    #length = rcp.getfloat("Options", "mincombdomainlength")
    domainsA = initTsvForOrganism(taxA)
    domainsB = initTsvForOrganism(taxB)
    
    def addedDomainLength(domains):
        length = 0
        for d in domains:
            length += d.alignmentEnd - d.alignmentStart
        return length
        
    proteins = []
    for pair in domainpairs:
        proteins.append(pair.first)
        proteins.append(pair.second)
    protLengths = getSequenceLengthsForAccessionsIds(proteins)
    
    filteredPairs = []
    for pair in domainpairs:
        domA = addedDomainLength(domainsA[pair.first])
        domB = addedDomainLength(domainsB[pair.second])
        if domA >= protLengths[pair.second] * length and domB >= protLengths[pair.first] * length:
            filteredPairs.append(pair)
    return filteredPairs

def readPairwise(filename):
    handle = open(filename, "r")   
    pairs = []
    for line in handle.readlines():
        splitted = line.split("\n")[0].split()
        pairs.append(OrthologPair(first=splitted[0], second=splitted[1]))       
    return pairs

# source for unique, intersect and union http://www.saltycrane.com/blog/2008/01/how-to-find-intersection-and-union-of/
def unique(a):
    """ return the list with duplicate elements removed """
    return list(set(a))

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def difference(a, b):
    return list(set(a) - set(b))

def printPairsToFile(pairs, filename):
    out = open(filename, "w")
    for pair in pairs:
            out.write(str(pair.first) + '\t' + str(pair.second) + "\n")
    out.close()
    
def readHeaderFromResult(filename):
    HeaderInfo = namedtuple("HeaderInfo", ["proteinsA", "proteinsB", "homologsAB", "homologsBA", "matchesAA", "matchesBB", "orthologGroups", "inparalogsA", "inparalogsB"])
    handle = open(filename, "r")
    temp = []
    for line in handle.readlines():
        if line.startswith("Grey"):
            break
        if not line.startswith('#'):
            temp.append(int(line.split()[0]))
    handle.close()
    h = HeaderInfo(proteinsA = temp[0], proteinsB = temp[1], homologsAB = temp[2], homologsBA = temp[3], matchesAA = temp[4], 
                   matchesBB = temp[5], orthologGroups = temp[6], inparalogsA = temp[7], inparalogsB = temp[8])
    return h
        
def computeDistancesFromHeader(header):
    dAB = (header.proteinsA - header.inparalogsA) / header.proteinsA * 100
    dBA = (header.proteinsB - header.inparalogsB) / header.proteinsB * 100
    return [dAB, dBA] 


def writeListToFile(idList, outpath):
    outFile = open(outpath, 'w')
    for ac in idList:
        outFile.write("%s\n" % ac)
    outFile.close()
    
def readList(filename):
    handle = open(filename,"r")
    lines = handle.read().split("\n")
    handle.close()
    return lines

def makePairName(org1, org2, prefix, delim):
    concatname = prefix
    if org1 < org2:
        concatname += org1 + delim + org2
    else:
        concatname += org2 + delim + org1
    return concatname

        