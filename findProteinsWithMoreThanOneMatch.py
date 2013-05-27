
handle = open("/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/Archive/ResultsForHumanDromeDomainsCurrent/sqltable.HumanDomainLevel.fasta-DrosophilaDomainLevel.fasta",'r')
mapping = {}
for line in handle.readlines():
    acc = line.split()[4].split('|')[1]
    if acc not in mapping:
        mapping[acc]=[]
    else:
        mapping[acc].append(line.split()[4])
        
for key in mapping:
    if len(mapping[key]) > 1:
        print mapping[key]