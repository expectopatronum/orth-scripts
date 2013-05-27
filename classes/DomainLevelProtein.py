'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''

from Protein import Protein
import OrthologyGroup
import Helper

class DomainLevelProtein(Protein):
    domain = ""
    header = ""
    #protein = None
    start = 0
    end = 0
    
    def __init__(self):
        self.accession = ""
        self.orthologGroup = None
        self.header = ""
        self.domain = ""
        #self.protein = None
        self.start = 0
        self.end = 0
    
    def __repr__(self):
        return "Domain " + self.domain + " from " + self.accession + "[" + str(self.start) + " " + str(self.end) + "]"
    
    def __str__(self):
        return self.header
    
    @staticmethod
    def initDomainLevelProteins(domainfile):
        handle = open(domainfile, 'r')
        proteinsA = {}
        proteinsB = {}
        orthologGroups = {}
        groupsStarted = False
        ort = None
        lineStarts = ['Group', 'Score', 'Boots', '_____']
        #header, protein, start, end
        for line in handle.readlines():
            if groupsStarted:
                if line[0:5] not in lineStarts:
                    hasA = not line.startswith(' ')                
                    splittedLine = line.split()
                    temp = ort.getBasicProteins(splittedLine)
                    
                    for p in temp:
                        p.__class__ = DomainLevelProtein
                    
                    if hasA:
                        splittedHeader = Helper.retrieveDomainHeaderInformation(splittedLine[0])
                        temp[0].domain = splittedHeader[1]
                        temp[0].start = int(splittedHeader[2])
                        temp[0].end = int(splittedHeader[3])
                        temp[0].header = splittedLine[0]

                        proteinsA[temp[0].header] = temp[0]
                        score = float(splittedLine[1].split('%')[0])
                        ort.inparalogsA[temp[0].header] = score
                        
                    if not hasA or len(temp) > 1:
                        splittedHeader = Helper.retrieveDomainHeaderInformation(splittedLine[-2])
                        temp[-1].domain = splittedHeader[1]
                        temp[-1].start = int(splittedHeader[2])
                        temp[-1].end = int(splittedHeader[3])
                        temp[-1].header = splittedLine[-2]
                        
                        proteinsB[temp[-1].header] = temp[-1]
                        score = float(splittedLine[-1].split('%')[0])
                        ort.inparalogsB[temp[-1].header] = score
                
                elif line.startswith('Group'):
                    ort = OrthologyGroup.getBasicOrthologyGroup(line, False, orthologGroups)
                
                elif line.startswith('Bootstrap'):
                    ort.addSeeds(line)
                  
            else:
                if line.startswith('_'):
                    groupsStarted = True
            
        handle.close()
        return proteinsA, proteinsB, orthologGroups
