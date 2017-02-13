#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

####################################################################################
### Copyright (C) 2015-2019 by ABLIFE 
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog

#
#
#
#
#####################################################################################

"""
      ：
1.clip-seq   ：  overlap reads  cluster
      ：
  HTSeq
"""


import re, os, sys, logging, time, datetime
from optparse import OptionParser, OptionGroup

reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess
import threading
from ablib.utils.tools import *
import gffutils
import HTSeq
import numpy
import multiprocessing
from matplotlib import pyplot



if sys.version_info < (2, 7):
    print("Python Version error: please use phthon2.7")
    sys.exit(-1)


_version = 'v0.1'


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-f] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option('-g', '--gff', dest='gff', action='store', type='string', help='gff file,do not have to provide it if db is exited')
    p.add_option('-d', '--db', dest='db', default='gffdb', action='store', type='string', help='the gff database file to create or use')
    p.add_option('-b', '--bed', dest='bed', action='store', type='string', help='bed file')
    p.add_option('-o', '--outfile', dest='outfile', default='raw_peak_cluster.txt', action='store', type='string', help='raw_peak_cluster.txt')
    p.add_option('-a', '--anti', dest='anti', default=False, action='store_true', help='pick gene antisense reads')


    group = OptionGroup(p, "Preset options")
    ##preset options
    group.add_option('-O', '--outDir', dest='outDir', default='./', action='store', type='string', help='output directory', metavar="DIR")
    group.add_option('-L', '--logDir', dest='logDir', default='', action='store', type='string', help='log dir ,default is same as outDir')
    group.add_option('-P', '--logPrefix', dest='logPrefix', default='', action='store', type='string', help='log file prefix')
    group.add_option('-E', '--email', dest='email', default='none', action='store', type='string', help='email address, if you want get a email when this job is finished,default is no email', metavar="EMAIL")
    group.add_option('-Q', '--quiet', dest='quiet', default=False, action='store_true', help='do not print messages to stdout')
    group.add_option('-K', '--keepTemp', dest='keepTemp', default=False, action='store_true', help='keep temp dir')
    group.add_option('-T', '--test', dest='isTest', default=False, action='store_true', help='run this program for test')
    p.add_option_group(group)

    if len(sys.argv) == 1:
        p.print_help()
        sys.exit(1)

    opt, args = p.parse_args()
    return (p, opt, args)


def listToString(x):
    """
    """
    rVal = ''
    for a in x:
        rVal += a + ' '
    return rVal



opt_parser, opt, args = configOpt()


if opt.logDir == "":
    opt.logDir = opt.outDir + '/log/'

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = scriptPath + '/bin'  # absolute bin path
outPath = os.path.abspath(opt.outDir)  # absolute output path
os.system("mkdir -p " + outPath)
logPath = os.path.abspath(opt.logDir)
os.system("mkdir -p " + logPath)
tempPath = outPath + '/temp/'  # absolute bin path
# os.mkdir(tempPath) if not os.path.isdir(tempPath) else None
resultPath = outPath + '/result/'


# os.mkdir(resultPath) if not os.path.isdir(resultPath) else None



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def initLogging(logFilename):
    """Init for logging
    """
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s : %(levelname)s] %(message)s', datefmt='%y-%m-%d %H:%M', filename=logFilename, filemode='w')
    if not opt.quiet:
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('[%(asctime)s : %(levelname)s] %(message)s', datefmt='%y-%m-%d %H:%M')
        # tell the handler to use this format
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


dt = datetime.datetime.now()
logFile = logPath + '/' + opt.logPrefix + 'log.' + str(dt.strftime('%Y%m%d.%H%M%S.%f')) + '.txt'
initLogging(logFile)
logging.debug(sys.modules[__name__].__doc__)
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
logging.debug('Program version: %s' % _version)
logging.debug('Start the program with [%s]\n', listToString(sys.argv))
startTime = datetime.datetime.now()
logging.debug("   ：Program start at %s" % startTime)


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def max_pos_and_value_of_ga(ga, iv):
    pos = iv.start
    max = 0
    for iv2, value2 in ga[iv].steps():
        if value2 > max:
            max = value2
            pos = iv2.start
    return pos, max


def reads_cluster(bedFile, fout, db):
    bedfile = HTSeq.BED_Reader(bedFile)


    bedga = HTSeq.GenomicArrayOfSets("auto", stranded=True)
    n = 0
    bed_dict = {}


    for r in bedfile:
        # print(r.score)
        r.name = r.line
        # print(r.line)
        n += 1
        bed_dict[str(n)] = r
        bedga[r.iv] += str(n)
        # peak_ga[r.iv] = 1
        # depth_ga[r.iv] += 1
    print("done handle bedfile")

    for gene in db.features_of_type('gene'):
        gene_iv = HTSeq.GenomicInterval(gene.seqid, gene.start - 1, gene.end, gene.strand)
        anti_strand = "+"
        if gene.strand == "+":
            anti_strand = "-"
        if opt.anti:
            gene_iv = HTSeq.GenomicInterval(gene.seqid, gene.start - 1, gene.end, anti_strand)
        bfs = set()
        for biv, fs in bedga[gene_iv].steps():
            bfs = bfs.union(fs)
        tags = len(bfs)
        if tags == 0:
            continue
        fout.writelines("Gene:\t" + str(gene.start + 1) + "\t" + str(gene.end) + "\t" + gene.id + "\t" + gene.strand + "\t" + gene.seqid + "\n")
        for n in bfs:
            bed = bed_dict[n]
            fout.writelines(bed.line + "\n")


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")

    if not os.path.isfile(opt.bed):
        print(opt.bed + 'is not exit,please check your file')
        sys.exit(1)

    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    fout.writelines("#Gene:\tstart\tend\tgeneid\tstrand\tchr\n")
    fout.writelines("#tag info\n")

    if opt.gff:
        db = gffutils.create_db(opt.gff, opt.db, merge_strategy="create_unique", verbose=False, force=True)

    db = gffutils.FeatureDB(opt.db)

    reads_cluster(opt.bed, fout, db)

    fout.close()


if __name__ == '__main__':

    main()
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
# if not opt.keepTemp:
# os.system('rm -rf ' + tempPath)
#     logging.debug("Temp folder is deleted..")
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
logging.debug("Program ended")
currentTime = datetime.datetime.now()
runningTime = (currentTime - startTime).seconds  # in seconds
logging.debug("   ：Program start at %s" % startTime)
logging.debug("   ：Program end at %s" % currentTime)
logging.debug("   ：Program ran %.2d:%.2d:%.2d" % (runningTime / 3600, (runningTime % 3600) / 60, runningTime % 60))
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
if opt.email != "none":
    run_cmd = listToString(sys.argv)
    sendEmail(opt.email, str(startTime), str(currentTime), run_cmd, outPath)
    logging.info("        %s" % opt.email)


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------




