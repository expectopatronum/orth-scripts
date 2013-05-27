import sys
import getopt
import ConfigParser
import Helper

__doc__ = "usage: python createListOfIdentifiers.py -t <taxid> -o <organismname>\n" \

rcp = ConfigParser.SafeConfigParser()
rcp.read("orthology.cfg")

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:t:", ["help", "organism", "taxid"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)

    inputfile = ''
    outputfile = ''

    ok = True
    for opt, arg in opts:
        if opt in ("-t", "--taxid"):
            inputfile = arg
        elif opt in ("-o", "--organism"):
            outputfile = arg
        else:
            ok = False   

    if ok:
        idList = []
        
        inputpath = rcp.get("Filepaths", "tsvpath")
        outpath = rcp.get("Filepaths", "idlistpath")
        suffix = rcp.get("Fileendings", "idlistsuffix")
        inFile = open(inputpath+inputfile+".tsv", 'r')
        cutoff = rcp.getint("Options", "domainlengthcutoff")
        for line in inFile.readlines():
            
            if not line.startswith("#") and not line.startswith("<"):
                splittedLine = line.split()
                if len(splittedLine) > 1:
                    accession = Helper.retrieveAccessionNumber(splittedLine[0]) # if error occurs, maybe tsv file has a header
                    start = int(splittedLine[1])
                    end = int(splittedLine[2])
                    hmmtype = splittedLine[7] # hmm type
                    if accession not in idList and hmmtype in ("Domain", "Family") and end - start >= cutoff:
                        idList.append(accession)
        inFile.close()
        outFile = open(outpath+outputfile+str(cutoff)+suffix, 'w')
        for ac in idList:
            outFile.write("%s\n" % ac)
        outFile.close()
                
    else:
        print __doc__
        sys.exit(0)


if __name__ == "__main__":
    main()
