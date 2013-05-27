'''
Created on Mar 21, 2013

@author: verenahaunschmid
'''
class BasicOrthologyGroup(object):
    inparalogsA = {}
    inparalogsB = {}
    
    def __init__(self):
        self.inparalogsA = []
        self.inparalogsB = []    
        
    def __eq__(self, other):
        return set(self.inparalogsA) == set(other.inparalogsA) and set(self.inparalogsB) == set(other.inparalogsB)
    
    @staticmethod
    def mergeTwoGroups(group1, group2):
        o = BasicOrthologyGroup()
        for a in group1.inparalogsA:
            if a not in o.inparalogsA:
                o.inparalogsA.append(a)
        for b in group1.inparalogsB:
            if b not in o.inparalogsB:
                o.inparalogsB.append(b)
        for a in group2.inparalogsA:
            if a not in o.inparalogsA:
                o.inparalogsA.append(a)
        for b in group2.inparalogsB:
            if b not in o.inparalogsB:
                o.inparalogsB.append(b)
        return o
    
    @staticmethod
    def buildGroupsFromPairs(pairs):
        proteinGroup = {}
        groups = []
        for pair in pairs:
            #merge groups
            if pair.first not in proteinGroup and pair.second not in proteinGroup:
                o = BasicOrthologyGroup()
                o.inparalogsA.append(pair.first)
                o.inparalogsB.append(pair.second)
                proteinGroup[pair.first] = o
                proteinGroup[pair.second] = o
                groups.append(o)
            elif pair.first in proteinGroup and pair.second not in proteinGroup:
                proteinGroup[pair.first].inparalogsB.append(pair.second)
                proteinGroup[pair.second] = proteinGroup[pair.first]
            elif pair.second in proteinGroup and pair.first not in proteinGroup:
                proteinGroup[pair.second].inparalogsA.append(pair.first)
                proteinGroup[pair.first] = proteinGroup[pair.second]
            elif pair.first in proteinGroup and pair.second in proteinGroup:
                if not proteinGroup[pair.first] == proteinGroup[pair.second]:
                    o = BasicOrthologyGroup.mergeTwoGroups(proteinGroup[pair.first], proteinGroup[pair.second])
                    if proteinGroup[pair.first] in groups:
                        groups.remove(proteinGroup[pair.first])
                    if proteinGroup[pair.second] in groups:
                        groups.remove(proteinGroup[pair.second])
                    for a in o.inparalogsA:
                        proteinGroup[a] = o
                    for b in o.inparalogsB:
                        proteinGroup[b] = o
                    groups.append(o)
            else:
                print "something weird happened"
                    
        return groups
