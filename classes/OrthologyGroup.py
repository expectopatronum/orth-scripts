'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''
import Helper
from Protein import Protein
from BasicOrthologyGroup import BasicOrthologyGroup
  
class OrthologyGroup(BasicOrthologyGroup):
    rank = ""
    seedsA = []
    seedsB = []
    isGeneLevel = True # False indicates DomainLevel
    score = 0

    def __init__(self):
        self.rank = ""
        self.seedsA = []
        self.seedsB = []
        self.inparalogsA = {}
        self.inparalogsB = {}
        self.isGeneLevel = True
        self.score = 0
        
    def __repr__(self):
        info = ""
        if self.isGeneLevel:
            info = "(genelevel"
        else:
            info = "(domainlevel"
        return "Ortholog " + info + self.rank + ", score " + str(self.score) + ")" + " with " + str(len(self.seedsA)) + " / " + str(len(self.seedsB)) + \
            " seeds and " + str(len(self.inparalogsA)) + " / " + str(len(self.inparalogsB)) + " inparalogs in organism A/B"
        
    def addSeeds(self, line):
        acc = Helper.retrieveAccessionNumber(line.split()[3])
        if acc in self.inparalogsA:
            self.seedsA.append(acc)
        elif acc in self.inparalogsB:
            self.seedsB.append(acc)
            
    def getBasicProteins(self, splittedLine):
        temp = []
        for i in range(0, len(splittedLine), 2):
            p = Protein()
            acc = Helper.retrieveAccessionNumber(splittedLine[i])
            p.accession = acc
            p.orthologGroup = self
            temp.append(p)
        return temp
                    
def getBasicOrthologyGroup(line, geneLevel, orthologGroups):
    ort = OrthologyGroup()
    rank, score = Helper.getRankAndScore(line)
    ort.score = score
    ort.isGeneLevel = geneLevel
    orthologGroups[rank] = ort
    return ort
