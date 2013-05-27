import os
import sys
import getopt
import ConfigParser

__doc__ = "usage: python prepareOrganism.py -o <organismname> -t <taxid>\n" \
    "o: the name of the organism to be prepared.\n"  \
    "t: taxid of the organism."

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

    ok = len(opts) == 2

    organism = ''
    taxid = ''

    ok = True
    for opt, arg in opts:
        if opt in ("-o", "--organism"):
            organism = arg
        elif opt in ("-t", "--taxid"):
            taxid = arg
        else:
            ok = False

    if ok:
        cutoff = rcp.get("Options", "domainlengthcutoff")
        os.system("python createListOfIdentifiers.py -t " + taxid + " -o "+organism)
        print "created list of identifiers"
        os.system("python extractSequences.py -o " + organism + cutoff)
        print "extracted sequences"
        os.system("python getDomainSequencesForProteome.py -p " + organism + cutoff + " -t " + taxid+".tsv" + " -o " + organism + cutoff + "Domains.fasta")
        print "got domains sequences"              
    else:
        print __doc__
        sys.exit(0)

if __name__ == "__main__":
    main()
