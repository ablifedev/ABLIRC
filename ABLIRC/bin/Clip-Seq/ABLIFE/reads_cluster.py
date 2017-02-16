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
程序功能说明：
1.clip-seq第一步：将有overlap的reads进行cluster
程序设计思路：
利用HTSeq包
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
        '-b', '--bed', dest='bed', action='store',
        type='string', help='bed file')
    p.add_option(
        '-o', '--outfile', dest='outfile', default='raw_peak_cluster.txt', action='store',
        type='string', help='raw_peak_cluster.txt')

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

    if len(sys.argv) == 1:
        p.print_help()
        sys.exit(1)

    opt, args = p.parse_args()
    return (p, opt, args)


def listToString(x):
    """获得完整的命令
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
os.mkdir(outPath) if not os.path.isdir(outPath) else None
logPath = os.path.abspath(opt.logDir)
os.mkdir(logPath) if not os.path.isdir(logPath) else None
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
logging.debug("计时器：Program start at %s" % startTime)


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


def reads_cluster(bedFile, fout):
    bedfile = HTSeq.BED_Reader(bedFile)


    bedga = HTSeq.GenomicArrayOfSets("auto", stranded=True)
    n = 0
    bed_dict = {}
    peak_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
    depth_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
    for r in bedfile:
        r.name = r.line
        # print(r.line)
        n += 1
        bed_dict[str(n)] = r
        bedga[r.iv] += str(n)
        peak_ga[r.iv] = 1
        depth_ga[r.iv] += 1
    print("done handle bedfile")
    m = 0  ## id count
    for iv, value in peak_ga.steps():
        if value == 1:
            m += 1
            id = iv.chrom + "_" + str(m)
            maxpos, maxdepth = max_pos_and_value_of_ga(depth_ga, iv)
            bfs = set()
            for biv, fs in bedga[iv].steps():
                bfs = bfs.union(fs)
            tags = len(bfs)

            fout.writelines(
                ">" + id + "\t" + iv.chrom + "\t" + str(iv.start) + "\t" + str(iv.end) + "\t" + str(tags) + "\t" + str(
                    maxdepth) + "\t" + str(maxpos) + "\t" + iv.strand + "\n")


            for n in bfs:
                bed = bed_dict[n]
                fout.writelines(bed.line+"\n")

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
    fout.writelines("#>id_in_chr\tchr\tstart\tend\ttags\tmaxheight\tsummit\tstrand\n")
    fout.writelines("#tag info\n")

    reads_cluster(opt.bed, fout)

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
logging.debug("计时器：Program start at %s" % startTime)
logging.debug("计时器：Program end at %s" % currentTime)
logging.debug("计时器：Program ran %.2d:%.2d:%.2d" % (runningTime / 3600, (runningTime % 3600) / 60, runningTime % 60))
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
if opt.email != "none":
    run_cmd = listToString(sys.argv)
    sendEmail(opt.email, str(startTime), str(currentTime), run_cmd, outPath)
    logging.info("发送邮件通知到 %s" % opt.email)


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def countProgram(programName, startT, runT, isTest):
    countProgramFile = open('/users/ablife/ablifepy/countProgram.txt', 'a')
    countProgramFile.write(
        programName + '\t' + str(os.getlogin()) + '\t' + str(startT) + '\t' + str(runT) + 's\t' + isTest + '\n')
    countProgramFile.close()


testStr = 'P'
if opt.isTest:
    testStr = 'T'
countProgram(sys.argv[0], startTime, runningTime, testStr)
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
