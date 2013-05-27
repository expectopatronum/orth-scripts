import sqlite3
import sys
import getopt
from Bio import SeqIO
import Helper
import ConfigParser

__doc__ = "usage: python fastaToSqliteDb.py [-f fasta]" \
"\n paths can be changed in orthology.cfg"

rcp = ConfigParser.SafeConfigParser()
rcp.read("orthology.cfg")

DBPATH = rcp.get("Filepaths", "databases") + rcp.get("Data","fullsequencesdb")
#FASTAPATH = rcp.get("Filepaths", "fastapath") + rcp.get("Data", "fullsequencesfasta")

def init(c):
    c.execute('''create table fasta_storage (id int, fasta text, description text, title text)''')

def writetodb(c, pid, pfasta, description, ptitle):
    c.execute("insert into fasta_storage values(?, ?, ?, ?)" , (pid, str(pfasta), description, ptitle))

def filetodb(c, filehandle):
    i =  c.execute("select count(*) from fasta_storage").fetchone()[0]
    for record in SeqIO.parse(filehandle, "fasta"):
        i = i + 1
        seqid = Helper.retrieveAccessionNumber(record.id)     
        writetodb(c, i, record.seq, record.description, seqid)

def main():   
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hif:", ["help", "init", "fasta"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    
    conv = True
    FASTAPATH = rcp.get("Filepaths", "fastapath")
    fasta = False
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
            
            # process arguments
        if o in ("-i", "--init"):
            init(c)
            print "Database was initialised."
            sys.exit(0)
        elif o in ("-f", "--fasta"):
            FASTAPATH =  a #currently use complete path
            fasta = True
        else:
            print "invalid option detected:", o
            conv = False

    if conv:
        if not fasta:
            FASTAPATH += rcp.get("Data", "fullsequencesfasta")
        handle = open(FASTAPATH, 'r')
        filetodb(c, handle)
        
        conn.commit()
        c.close()
    else:
        c.close()

if __name__ == "__main__":
    main()
