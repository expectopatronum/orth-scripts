def parse(filename):
    left=[]
    right=[]
    file=open(filename,'r')
    for line in file.readlines():
         splitted=line.split("\n")[0].split()
         left.append(splitted[0])
         right.append(splitted[1])

    out = open(filename+"Swapped","w")
    for l, r in zip(left, right):
         out.write(r + "\t" + l + "\n")

    out.close()
    file.close()

#parse("/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/Comparison/HumanDrome30/DomainsMappedToProteinsHumanDrome30")
parse("/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/BasedOnInparanoidData/Results/HumanDromeFull/Output.Human30Full.fasta-Drosophila30Full.pairs")

