import sqlite3
import sys
import getopt
from Bio import SeqIO
import ConfigParser
import os

__docs__ = "usage: python addBenchmarkDataToDb.py"

rcp = ConfigParser.SafeConfigParser()
rcp.read("orthology.cfg")

DBPATH = rcp.get("Filepaths", "databases") + "benchmark.db"
inpath = "/Users/verenahaunschmid/Documents/FH/semester06/Praktikum/OrthologyBenchmarkService/SupportingInformation/"
FASTALIST = ["Dataset_S4", "Dataset_S5", "Dataset_S6"]

def init(c):
    c.execute('''create table fasta_storage (id int, fasta text, organism text, title text)''')

def writetodb(c, pid, pfasta, organism, ptitle):
    c.execute("insert into fasta_storage values(?, ?, ?, ?)" , (pid, str(pfasta), organism, ptitle))

def filetodb(c, filehandle):
    i =  c.execute("select count(*) from fasta_storage").fetchone()[0]
    for record in SeqIO.parse(filehandle, "fasta"):
        i = i + 1    
        writetodb(c, i, record.seq, record.description[0:5], record.description)

def main():   
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi", ["help", "init"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    
    conv = True
    
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
            
            # process arguments
        if o in ("-i", "--init"):
            init(c)
            print "Database was initialised."
            sys.exit(0)
        else:
            print "invalid option detected:", o
            conv = False

    if conv:
        temp = open(inpath+"temp.txt", "w")
        for filename in FASTALIST:
            handle = open(inpath + filename, "r")
            for line in handle.readlines():
                temp.write(line)
            handle.close()
        
        handle = open(temp, 'r')
        filetodb(c, handle)
        handle.close()
        
        #os.remove(temp)
        conn.commit()
        c.close()
    else:
        c.close()

if __name__ == "__main__":
    main()
