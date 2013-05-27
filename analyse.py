import sys
import getopt
import Helper
import ConfigParser

__doc__ = "usage: python analyse.py -i <inputfilename> -o <outputfilename>\n" \
    "i: name of an InParanoid result file of pattern Output.<OrganismA>-<OrganismB>\n"  \
    "o: path where anlysis results should be saved."

rcp = ConfigParser.RawConfigParser()
rcp.read("orthology.cfg")

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "ifile", "ofile"])
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

    inputfile = ''
    outputfile = ''

    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile =  rcp.get("Filepaths", "resultpath") + arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        else:
            ok = False
        ok = True

    if ok:

        handle = open(inputfile, 'r')
        header = True
        scores = []
        output = ""
        inparalogsPerGroupA = {}
        inparalogsPerGroupB = {}
        rank = ""
        for line in handle.readlines():
            if header and not line.startswith('_'):
                output += line
            elif header and line.startswith('_'):
                header = False
            elif not header:
                if line.startswith('Group'):
                    rank, score = Helper.getRankAndScore(line)
                    inparalogsPerGroupA[rank] = 0
                    inparalogsPerGroupB[rank] = 0
                    scores.append(score)
                elif not line.startswith('Score') and not line.startswith('Bootstrap') and not line.startswith('_'):
                    if (line.startswith(' ')): # in this case there is an entry for B but not A
                        inparalogsPerGroupB[rank] += 1
                    else:
                        if len(line.split()) > 2:
                            inparalogsPerGroupB[rank] += 1
                        inparalogsPerGroupA[rank] += 1
        
        handle.close()
        
        sumA = 0
        for key in inparalogsPerGroupA:
            sumA += inparalogsPerGroupA[key]
            
        sumB = 0
        for key in inparalogsPerGroupB:
            sumB += inparalogsPerGroupB[key]
        
        out = open(outputfile, 'w')
        out.write("Score summary\n")
        out.write(output)
        out.write("Mean " + str(Helper.mean(scores)) + '\n')
        out.write("Median " + str(Helper.median(scores)) + '\n')
        out.write("Max " + str(max(scores)) + '\n')
        out.write("Len " + str(len(scores)) + '\n\n')
        
        out.write("Organism A\n")
        out.write("Inparalgos " + str(sumA) + '\n')
        out.write("Inparalogs per group " + str(float(sumA)/float(len(inparalogsPerGroupA))) + '\n')
        out.write("Organism B\n")
        out.write("Inparalogs " + str(sumB) + '\n')
        out.write("Inparalogs per group " + str(float(sumB)/float(len(inparalogsPerGroupB))) + '\n')
        out.close()

    else:
        print __doc__
        sys.exit(0)


if __name__ == "__main__":
    main()
