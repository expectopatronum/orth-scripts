import sqlite3
import sys
import getopt
from Bio import SeqIO
import ConfigParser
import Helper

__doc__ = "usage: python addTsvToDb -t <taxid> \n t: taxid of the organism to be added"

rcp = ConfigParser.SafeConfigParser()
rcp.read("orthology.cfg")

dbpath = rcp.get("Filepaths", "databases") + rcp.get("Data","domaindb")
tsvpath = rcp.get("Filepaths", "tsvpath")

def init(c):
    c.execute('''create table tsv_storage (id int, seqid text, tax text, alStart int, alEnd int, envStart int, envEnd int, hmmAcc text,
    hmmName text, hmmType text, hmmStart int, hmmEnd int, hmmLength int, bitScore float, evalue float, clan text)''')

def writetodb(c, pid, seqid, tax, alstart, alend, envstart, envend, hmmacc, name, hmmtype, hmmstart, hmmend, hmmlength, bit, e, clan, length):
    c.execute("insert into tsv_storage values({vals})".format(vals=','.join(['?']*17)) ,
               (pid, seqid, tax, int(alstart), int(alend), int(envstart), int(envend), hmmacc, name, hmmtype, 
                int(hmmstart), int(hmmend), int(hmmlength), float(bit), float(e), clan, length))

def filetodb(c, filehandle, tax):
    fileAsList = []
    accessions = []
    for line in filehandle.readlines():
        if not line.startswith("#") and not line.startswith("<"): # header usually starts with <         
            split = line.split("\n")[0].split()
            if len(split) == 0:
                continue
            acc = Helper.retrieveAccessionNumber(split[0])
            fileAsList.append([acc, split[1], split[2], split[3], split[4], split[5], split[6], split[7], split[8], split[9], 
                               split[10], split[11], split[12], split[14]])
            accessions.append(acc)
            
    lengths = Helper.getSequenceLengthsForAccessionsIds(accessions)
    i =  c.execute("select count(*) from tsv_storage").fetchone()[0]
    for split in fileAsList:
        writetodb(c, i, split[0], tax, split[1], split[2], split[3], split[4], split[5], split[6], split[7], split[8], split[9],
                  split[10], split[11], split[12], split[13], int(lengths[split[0]]))
        i = i+1

def main():   
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hit:", ["help", "init", "taxid"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    
    conv = True
    taxid = ""
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
            
            # process arguments
        if o in ("-i", "--init"):
            init(c)
            c.close()
            print "Database was initialised."
            sys.exit(0)
        if o in ("-t", "taxid"):
            taxid = a
        else:
            print "invalid option detected:", o
            conv = False

    if conv and len(taxid)>0:
        handle = open(tsvpath+taxid+".tsv", 'r')
        #handle=open(taxid, "r")
        #taxid = taxid.split(".")[0].split("/")[-1]
        filetodb(c, handle, taxid)
        print "File written."
        conn.commit()
        c.close()
    else:
        c.close()

if __name__ == "__main__":
    main()