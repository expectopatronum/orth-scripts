'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''

from Protein import Protein
import OrthologyGroup
import Helper
import ConfigParser

class GeneLevelProtein(Protein):
    domains = []
    
    def __init__(self):
        self.domains = []
        self.accession = ""
        self.orthologGroup = None
    
    def __repr__(self):
        result = ""
        for d in self.domains:
            result += d[2] + "[" + str(d[0]) + " " + str(d[1]) + "] "
        return "Protein " + self.accession + "belongs to ortholog group " + self.orthologGroup.rank + "\n" \
            "Domains: \n" + result

    def __str__(self):
        return self.accession
    
    @staticmethod
    def initGeneLevelProteins(filename, tsvfileA, tsvfileB, useDomains):
        proteinsA = {}
        proteinsB = {}
        orthologGroups = {}
        groupsStarted = False
        
        rcp = ConfigParser.RawConfigParser()
        rcp.read("orthology.cfg")
        cutoff = rcp.getint("Options", "domainlengthcutoff")
        
        if useDomains:
            domainsA, shortA = Helper.getDomainsFromTsv(tsvfileA, cutoff)        
            domainsB, shortB = Helper.getDomainsFromTsv(tsvfileB, cutoff)
        handle = open(filename, 'r')
        ort = None

        lineStarts = ['Group', 'Score', 'Boots', '_____']
        for line in handle.readlines():
            if groupsStarted:           
                if line[0:5] not in lineStarts:
                    hasA = not line.startswith(' ')
                    temp = []
                    splittedLine = line.split()
                    temp = ort.getBasicProteins(splittedLine)
                    
                    if hasA:
                        temp[0].__class__ = GeneLevelProtein
                        proteinsA[temp[0].accession] = temp[0]
                        if useDomains:
                            temp[0].domains = domainsA[temp[0].accession]
                        score = float(splittedLine[1].split('%')[0])
                        ort.inparalogsA[temp[0].accession] = score
                        
                    if not hasA or len(temp) > 1:
                        temp[-1].__class__ = GeneLevelProtein
                        proteinsB[temp[-1].accession] = temp[-1]
                        if useDomains:
                            temp[-1].domains = domainsB[temp[-1].accession]
                        score = float(splittedLine[-1].split('%')[0])
                        ort.inparalogsB[temp[-1].accession] = score
                
                elif line.startswith('Group'):
                    ort = OrthologyGroup.getBasicOrthologyGroup(line, True, orthologGroups)
                
                elif line.startswith('Bootstrap'):
                    ort.addSeeds(line)
                        
            else:
                if line.startswith('_'):
                    groupsStarted = True
        
        pairsCount = 0
        for g in orthologGroups:
            pairsCount += len(orthologGroups[g].inparalogsA) * len(orthologGroups[g].inparalogsB)
        
        print pairsCount, "should be the amount of pairs"
        print len(orthologGroups), "ortholog groups read from the file"  
        handle.close()
        if useDomains:
            return proteinsA, proteinsB, orthologGroups, shortA, shortB
        else:
            return proteinsA, proteinsB, orthologGroups