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
    p.add_option('-p', '--peakfile', dest='peakfile', action='store', type='string', help='peakfile')
    p.add_option('-d', '--dis', dest='dis', default=50, action='store', type='int', help='distance')
    p.add_option('-o', '--outfile', dest='outfile', default='cluster.txt', action='store', type='string', help='cluster.txt')
    p.add_option('-r', '--clusterprefix', dest='clusterprefix', default='cluster_', action='store', type='string', help='clusterprefix')
    p.add_option('-a', '--anti', dest='anti', default=False, action='store_true', help='antisense')

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
def store_bed_iv(peakfile):
    bedga = HTSeq.GenomicArrayOfSets("auto", stranded=True)
    n = 0
    bed_dict = {}
    for eachline in open(peakfile):
        line = eachline.strip().split("\t")
        if eachline.startswith(">"):
            bed_iv = HTSeq.GenomicInterval(line[1], int(line[2]) - 1, int(line[3]), line[5])
            n += 1
            bed_dict[str(n)] = (bed_iv, int(line[4]))
            bedga[bed_iv] += str(n)
    return bedga, bed_dict


def get_bed_set_in_iv(bedga, bed_dict, iv=None):
    iset = list()
    bfs = set()
    # print(iv)
    # print(bedga)
    if iv:
        for biv, fs in bedga[iv].steps():
            bfs = bfs.union(fs)
    else:
        for biv, fs in bedga.steps():
            bfs = bfs.union(fs)
    for n in bfs:
        bed = bed_dict[n]
        iset.append(bed)
    return iset


def clusterpeak(peakfile, dis, fout):
    # Gene:	825139	859446	ENSG00000228794.8	+   chr1
    # >chr1_1	chr1	855563	855566	3	+
    # >chr1_2	chr1	858721	858727	3	+
    bedga, bed_dict = store_bed_iv(peakfile)
    id = [0]

    for eachline in open(peakfile):
        line = eachline.strip().split("\t")
        if eachline.startswith("Gene:"):
            fout.writelines(eachline)
            iv_set = ()
            blank_iv = set()
            depth_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
            cluster = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
            cov_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')

            gene_iv = HTSeq.GenomicInterval(line[5], int(line[1]) - 1, int(line[2]), line[4])
            anti_strand = "+"
            if line[4] == "+":
                anti_strand = "-"
            if opt.anti:
                gene_iv = HTSeq.GenomicInterval(line[5], int(line[1]) - 1, int(line[2]), anti_strand)

            iv_set = get_bed_set_in_iv(bedga, bed_dict, gene_iv)
            for iv in iv_set:
                depth_ga[iv[0]] += iv[1]
                cov_ga[iv[0]] = 1
            cluster_iv(gene_iv, blank_iv, dis, cluster, cov_ga)
            print_cluster(fout, cluster, depth_ga, id)


def print_cluster(fout, cluster, depth_ga, id):
    fout.writelines("#chr\tcluster_start\tcluster_end\tclusterid\tlength\tstrand\tmaxposition\tmax_depth\ttotal_bases\n")
    # fout.writelines("#>chr\tposition\tstrand\tdepth\n")
    for iv, value in cluster.steps():
        length = iv.length
        if value > 0:
            id[0] += 1
            clusterid = opt.clusterprefix + str(id[0])
            tc = ""
            maxposition = 0
            max_depth = 0
            sum_depth = 0
            sum_tpm = 0
            for iv2, value2 in depth_ga[iv].steps():
                if value2 > 0:
                    for i in range(iv2.start, iv2.end):
                        tc += ">" + iv2.chrom + "\t" + str(i + 1) + "\t" + iv2.strand + "\t" + str(value2) + "\n"
                        sum_depth += value2
                        if value2 > max_depth:
                            max_depth = value2
                            maxposition = i + 1
            fout.writelines(">" + clusterid + "\t" + iv.chrom + "\t" + str(iv.start + 1) + "\t" + str(iv.end) + "\t" + str(length) + "\t" + iv.strand + "\t" + str(maxposition) + "\t" + str(max_depth) + "\t" + str(sum_depth) + "\n")
            # fout.writelines(tc)


def cluster_iv(geneiv, blank_iv, cluster_dis, cluster, cov_ga):
    forward_iv_p = None
    forward_iv_n = None
    for iv, value in cov_ga[geneiv].steps():
        if value == 0:
            blank_len = iv.length
            if blank_len > cluster_dis and iv.strand == "+":
                blank_iv.add(iv)
                if not forward_iv_p:
                    forward_iv_p = iv
                    continue
                elif iv.chrom != forward_iv_p.chrom:
                    forward_iv_p = iv
                    continue
                else:
                    cluster_start = forward_iv_p.end
                    cluster_end = iv.start
                    cluster_iv = HTSeq.GenomicInterval(iv.chrom, cluster_start, cluster_end, "+")
                    cluster[cluster_iv] = 1
                    forward_iv_p = iv
            if blank_len > cluster_dis and iv.strand == "-":
                blank_iv.add(iv)
                if not forward_iv_n:
                    forward_iv_n = iv
                    continue
                elif iv.chrom != forward_iv_n.chrom:
                    forward_iv_n = iv
                    continue
                else:
                    cluster_start = forward_iv_n.end
                    cluster_end = iv.start
                    cluster_iv = HTSeq.GenomicInterval(iv.chrom, cluster_start, cluster_end, "-")
                    cluster[cluster_iv] = 2
                    forward_iv_n = iv


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")

    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    clusterpeak(opt.peakfile, opt.dis, fout)

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



