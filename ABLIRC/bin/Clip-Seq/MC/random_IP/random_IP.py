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
import random
import rpy2.robjects as robjects



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
    p.add_option('-g', '--geneid', dest='geneid', action='store', type='string', help='geneid')
    p.add_option('-t', '--times', dest='times', default=100, action='store', type='int', help='random times')
    p.add_option('-l', '--genelen', dest='genelen', action='store', type='int', help='gene length')
    p.add_option('-o', '--outfile', dest='outfile', default='pvalue.txt', action='store', type='string', help='pvalue.txt')
    p.add_option('-r', '--reads', dest='reads', action='store', type='string', help='reads')
    p.add_option('-f', '--fdr', dest='fdr', action='store', type='float', help='fdr threshold', default=0.001)

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


##bonferroni
def fdr_BF(ps):
    corrected_ps = list(robjects.r['p.adjust'](robjects.FloatVector(ps), method='bonferroni'))
    return corrected_ps


def randomip(geneid, times, genelen, reads, fout):
    gene_strand = "+"
    gene_start = 1
    gene_end = genelen
    tags = reads.split(",")
    gene_iv = HTSeq.GenomicInterval("chr", gene_start - 1, gene_end, gene_strand)
    height = {}
    line = {}
    fdr = []
    p = []
    totalhit = 0

    for i in range(times):
        ga = HTSeq.GenomicArray(["chr"], stranded=True, typecode='i')
        for tag in tags:
            tag_len = int(tag)
            tag_start = int((genelen - tag_len) * random.random())
            if tag_start < 1:
                tag_start = 1
            tag_end = tag_start + tag_len - 1
            # print(tag_start)
            tagiv = HTSeq.GenomicInterval("chr", tag_start - 1, tag_end, gene_strand)
            ga[tagiv] += 1
        for iv, value in ga[gene_iv].steps():
            if value >= 1:
                totalhit += 1
                if value in height:
                    height[value] += 1
                else:
                    height[value] = 1
    fout.writelines("#########################\n")
    fout.writelines("Gene:" + geneid + "\n")
    for h in sorted(height.keys(), key=int):
        num = 0
        for h2 in sorted(height.keys(), key=int):
            if h2 >= h:
                num += height[h2]
        ratio = round(float(height[h]) / totalhit, 4)
        pvalue = round(float(num) / totalhit, 4)
        p.append(pvalue)
        line[h] = str(h) + "\t" + str(height[h]) + "\t" + str(ratio) + "\t" + str(pvalue)

    fdr = fdr_BF(p)

    x = 0
    min_h = len(height) + 1
    for h in sorted(height.keys(), key=int):
        fout.writelines(line[h] + "\t" + str(fdr[x]) + "\n")
        if fdr[x] < opt.fdr and h < min_h:
            min_h = h
        x += 1
    fout.writelines("FDR:" + str(opt.fdr) + "\t" + geneid + "\t" + str(min_h) + "\n")


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")

    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    randomip(opt.geneid, opt.times, opt.genelen, opt.reads, fout)

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




