import sys
import getopt
from Bio import SeqIO
import Helper
import ConfigParser

__doc__ = "usage: python getDomainSequencesForProteome.py -p <proteomefile> -t <tsvfilename> -o <outputfilename>\n" \
"p: fasta file containing full sequences\n" \
"t: file containing region information. called tsv when extracted from Pfam.\n" \
"o: path to where the output should be saved"

rcp = ConfigParser.RawConfigParser()
rcp.read("orthology.cfg")

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:t:o:", ["help", "proteomefile", "tsvfile", "ofile"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
    # process arguments
    ok = len(opts) == 3

    tsvfile = ''
    outputfile = ''
    proteomefile = ''

    ok = True
    for opt, arg in opts:
        if opt in ("-t", "--tsvfile"):
            tsvfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--proteomefile"):
            proteomefile = arg
        else:
            ok = False
    if ok:
        
        tsvpath = rcp.get("Filepaths", "tsvpath")
        outpath = rcp.get("Filepaths", "retrieveddomainspath")
        cutoff = rcp.getint("Options", "domainlengthcutoff")
        idlistpath = rcp.get("Filepaths", "idlistpath")
        idlistsuffix = rcp.get("Fileendings", "idlistsuffix")
        domains, short = Helper.getDomainsFromTsv(tsvpath+tsvfile, cutoff)
        output = getDomainsForSequences(domains, idlistpath+proteomefile + idlistsuffix)
        outFile = open(outpath+outputfile, 'w')
        outFile.write(str(output))
        outFile.close()              
    else:
        print __doc__
        sys.exit(0)

def getDomainsForSequences(domains, proteomefile):   
    handle = open(proteomefile, "rU")
    result = ''
    accessions = []
    for record in handle.readlines():
        accessions.append(record.split('\n')[0])

    sequences = Helper.extractFromDb(accessions)
    
    for accession in accessions:
        seq = sequences[accession]
        if accession in domains:
            for position in domains[accession]:
                start = position[0]
                end = position[1]
                subseq = seq[start-1:end]
                if len(subseq) > 0:
                    header = ">" + accession + "|" + position[2] + "|start:" + str(start) + "|end:" + str(end) + '\n'
                    result = result + header + subseq + '\n'
                else:
                    print accession, "was shorter than the location of a domain", len(seq), "[", start, end, "]"
        else:
            print accession, "does not have assigned domains"
               
    handle.close()
    return result

if __name__ == "__main__":
    main()