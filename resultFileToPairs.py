'''
Created on Apr 25, 2013

@author: verenahaunschmid
'''

import sys
import getopt

import Helper
from classes.GeneLevelProtein import GeneLevelProtein

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
       
    filename = "" 
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-f", "--file"):
            filename = a
    
    #===========================================================================
    # pairfile = ""
    # if filename.count(".") > 0:
    #    pairfile = "".join(filename.split(".")[:-1]) + ".pairs.txt"
    # else:
    #    pairfile = filename + ".pairs.txt"
    #===========================================================================
    
    pairfile = filename + ".pairs.txt"
        
    resultfiletopairs(filename, pairfile)

def resultfiletopairs(filename, outname):   
    print "init gene level proteins ..."    
    proteinsA, proteinsB, orthologs = GeneLevelProtein.initGeneLevelProteins(filename, None, None, False)

    print "pairwise orthology mappings ..."
    pairwise = Helper.pairwiseOrthologs(orthologs, proteinsA, proteinsB)      
    
    Helper.printPairsToFile(pairwise, outname)
            

if __name__ == '__main__':
    main()
