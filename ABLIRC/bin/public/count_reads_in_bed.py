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
#####################################################################################

"""
      ：
1.  gene
2.randCheck_gene
3.randCheck_mRNA
      ：
  gffutils HTSeq
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
    p.add_option(
        '-i', '--bed', dest='bed', action='store',
        type='string', help='bed file')
    p.add_option(
        '-b', '--bam', dest='bam', action='store',
        type='string', help='bam file')
    p.add_option(
        '-o', '--outfile', dest='outfile', default='expression_profile.txt', action='store',
        type='string', help='gene expression file')
    p.add_option(
        '-n', '--samplename', dest='samplename', default='', action='store',
        type='string', help='sample name,default is ""')

    group = OptionGroup(p, "Preset options")
    ##preset options
    group.add_option(
        '-O', '--outDir', dest='outDir', default='./', action='store',
        type='string', help='output directory', metavar="DIR")
    group.add_option(
        '-L', '--logDir', dest='logDir', default='', action='store',
        type='string', help='log dir ,default is same as outDir')
    group.add_option(
        '-P', '--logPrefix', dest='logPrefix', default='', action='store',
        type='string', help='log file prefix')
    group.add_option(
        '-E', '--email', dest='email', default='none', action='store',
        type='string', help='email address, if you want get a email when this job is finished,default is no email',
        metavar="EMAIL")
    group.add_option(
        '-Q', '--quiet', dest='quiet', default=False, action='store_true',
        help='do not print messages to stdout')
    group.add_option(
        '-K', '--keepTemp', dest='keepTemp', default=False, action='store_true',
        help='keep temp dir')
    group.add_option(
        '-T', '--test', dest='isTest', default=False, action='store_true',
        help='run this program for test')
    p.add_option_group(group)

    if len( sys.argv ) == 1:
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

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'reads_in_bed.txt':
    opt.outfile = sample + opt.outfile

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = scriptPath + '/bin'  # absolute bin path
outPath = os.path.abspath(opt.outDir)  # absolute output path
# os.mkdir(outPath) if not os.path.isdir(outPath) else None
os.system('mkdir -p ' + outPath)
logPath = os.path.abspath(opt.logDir)
# os.mkdir(logPath) if not os.path.isdir(logPath) else None
os.system('mkdir -p ' + logPath)
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
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s : %(levelname)s] %(message)s',
        datefmt='%y-%m-%d %H:%M',
        filename=logFilename,
        filemode='w')
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
def invert_strand(iv):
    """
    :param iv: HTSeq.GenomicInterval object
    :return: HTSeq.GenomicInterval - strand is reversed
    """
    iv2 = iv.copy()
    if iv2.strand == "+":
        iv2.strand = "-"
    elif iv2.strand == "-":
        iv2.strand = "+"
    else:
        print("strand must be + or -")
    return iv2


def getTotalBase(iv, coverage):
    totalbases = 0
    for iv2, value2 in coverage[iv].steps():
        if value2 > 0:
            totalbases += value2 * iv2.length
    return totalbases


def readChr(chr, reads, bed):
    print(chr)
    reads_dict = {}

    bamfile = HTSeq.BAM_Reader(opt.bam)


    for eachLine in open(bed):
        line = eachLine.strip().split()
        if line[0] != chr:
            continue
        gene_iv = HTSeq.GenomicInterval(chr, int(line[1]), int(line[2])+1, ".")
        key = eachLine.strip()
        i = 0
        for r in bamfile[gene_iv]:
            if not r.aligned:
                continue
            i += 1
        reads_dict[key]=i

    reads[chr] = reads_dict.copy()
    del reads_dict
    logging.info("done %s" % chr)


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")




    if not os.path.isfile(opt.bam + '.bai'):
        os.system("samtools index " + opt.bam)


    Watcher()
    pool = multiprocessing.Pool(processes=15)
    server = multiprocessing.Manager()
    reads = server.dict()
    # reads = {}

    chr_dict = readBamHeader(opt.bam)
    for chr in chr_dict:
        print("this is "+chr)
        reads[chr] = {}
        # readChr(chr, reads, opt.bed)
        pool.apply_async(readChr,args=(chr, reads, opt.bed))
    pool.close()
    pool.join()
    # reads["chr1"]={}
    # readChr("chr1",reads["chr1"])
    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    # fout.writelines(
    #     "#Gene\tChro\tStrand\tStart\tEnd\tLength\tExonLen\tIntroLen\tDepth\tCoverage\tRPKM\tTotalReads\tSenseReads\tAntisenseReads\tGeneType\n")

    d = dict(reads).copy()
    server.shutdown()

    for chr in sorted(d.keys()):
        for key in d[chr]:
            fout.writelines(key + "\t" + str(d[chr][key]) + "\n")

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




