import sys
import getopt
import ConfigParser
import sqlite3
import Helper

__doc__ = "usage: python extractSequences.py -o <organismname>" \
    "\nchange parameters in orthology.cfg if needed"

rcp = ConfigParser.SafeConfigParser()
rcp.read("orthology.cfg")

fastafile = rcp.get("Filepaths", "databases") + rcp.get("Data", "fullsequencesdb")
proteome = rcp.get("Filepaths", "proteomepath")
idlistpath=rcp.get("Filepaths", "idlistpath")
outpath = rcp.get("Filepaths", "retrievedfullpath")

protEnding = rcp.get("Fileendings", "idlistsuffix")
outEnding = rcp.get("Fileendings", "retrievedsequenceout")

outputfile = ""
inputfile = ""

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:", ["help", "organism"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-o", "--organism"):
            end = rcp.get("Fileendings", "idlistsuffix")
            inputfile = idlistpath+a+end
            outputfile = outpath+a+"Full"+".fasta"

    listin = open(inputfile, 'r')
    idlist = []
    for line in listin.readlines():
        idlist.append(line.split()[0])
    listin.close()

    result = Helper.extractFromDb(idlist)
    outhandle = open(outputfile, 'w')
    for key in result:
        #changed this after mouse, human and drome 0, 20, 30 and 45 were extracted, before that key was the header
        #blastall has problems with ' symbols
        outhandle.write('>' + Helper.retrieveAccessionNumber(key) + '\n' + result[key] + '\n')
    outhandle.close()
        
if __name__ == "__main__":
    main()
