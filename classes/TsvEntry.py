'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''

class TsvEntry(object):
    '''
    representing all properties of a tsv entry
    '''
    seqId = ""
    tax = ""
    alignmentStart = 0
    alignmentEnd = 0
    envelopeStart = 0
    envelopeEnd = 0
    hmmAcc = ""
    hmmName = ""
    hmmType = ""
    hmmStart = 0
    hmmEnd = 0
    hmmLength = 0
    bitScore = 0.0
    evalue = 0.0
    clan = ""
    
    def asList(self):
        aslist = []
        aslist.append(self.seqId)
        aslist.append(self.tax)
        aslist.append(self.alignmentStart)
        aslist.append(self.alignmentEnd)
        aslist.append(self.envelopeStart)
        aslist.append(self.envelopeEnd)
        aslist.append(self.hmmAcc)
        aslist.append(self.hmmName)
        aslist.append(self.hmmType)
        aslist.append(self.hmmStart)
        aslist.append(self.hmmEnd)
        aslist.append(self.hmmLength)
        aslist.append(self.bitScore)
        aslist.append(self.evalue)
        aslist.append(self.clan)
        return aslist
    
    def __repr__(self):
        return str(self.asList())
    
    def __init__(self, params):
        '''
        Constructor
        '''
        self.seqId = str(params[1])
        self.tax = str(params[2])
        self.alignmentStart = params[3]
        self.alignmentEnd = params[4]
        self.envelopeStart = params[5]
        self.envelopeEnd = params[6]
        self.hmmAcc = str(params[7])
        self.hmmName = str(params[8])
        self.hmmType = str(params[9])
        self.hmmStart = params[10]
        self.hmmEnd = params[11]
        self.hmmLength = params[12]
        self.bitScore = params[13]
        self.evalue = params[14]
        self.clan = str(params[15])