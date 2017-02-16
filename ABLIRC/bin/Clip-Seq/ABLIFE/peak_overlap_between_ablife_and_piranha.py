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
1.将实验组与对照组非overlap的peaks挑选出来
程序设计思路：
利用HTSeq模块的GenomicArrayOfSets来记录对照组的peaks，然后遍历实验组peaks，如果peak所在的interval
有对照组的peak部分存在，则跳过。
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
        '-e', '--exp', dest='exp', action='store',
        type='string', help='ablife peaks文件，头三列需分别是peak的：染色体，start，end')
    p.add_option(
        '-c', '--ctrl', dest='ctrl', action='store',
        type='string', help='piranha peaks文件，头三列需分别是peak的：染色体，start，end')
    p.add_option(
        '-o', '--outfile', dest='outfile', default='peak_overlap_between_ablife_and_piranha.txt', action='store',
        type='string', help='peak_overlap_between_ablife_and_piranha')
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

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'peak_overlap_between_ablife_and_piranha.txt':
    opt.outfile = sample + opt.outfile

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


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    logging.debug("Main procedure start...")

    gas = HTSeq.GenomicArrayOfSets( "auto", stranded=True )


    # #chr    start   end     name    tags    strand  pvalue
    # chr1    2392860 2392880 X       8       +       0.000238833
    title2 = getTitle(opt.ctrl)
    piranha_total_peaknum = 0
    for eachLine in open(opt.ctrl,'r'):
        line=eachLine.strip().split("\t")
        if eachLine.startswith("#"):
            continue
        peak_iv = HTSeq.GenomicInterval(line[0], int(line[1]) - 1, int(line[2]), line[5])
        gas[peak_iv]+=eachLine.strip()
        piranha_total_peaknum += 1

    w = open(opt.outfile,"w")
    


    title1 = getTitle(opt.exp)
    w.writelines("ablife"+title1+"\tpiranha"+title2+"\n")
    ablife_total_peaknum = 0
    for eachLine in open(opt.exp,'r'):
        line=eachLine.strip().split("\t")
        if eachLine.startswith("#"):
            continue
        ablife_total_peaknum += 1
        peak_iv = HTSeq.GenomicInterval(line[0], int(line[1]) - 1, int(line[2]), line[5])
        peak_len = int(line[2]) - int(line[1]) + 1
        flag = 0
        overlap_length = 0
        for iv, fs in gas[peak_iv].steps():
            if len(fs) >= 1:
                flag = 1
                overlap_length += iv.length
                for p in fs:
                    w.writelines(eachLine.strip()+"\t"+str(iv.length)+"\t"+p+'\n')
        # if flag == 0:
        #     print(eachLine.strip()+"\t"+str(peak_len))
        # else:
        #     print(eachLine.strip()+str(overlap_length)+'\n')

    w.close()

    tmp = os.popen('cut -f 11,12,13 '+opt.outfile+' | sort|uniq|wc -l').readlines()
    piranha_peaknum = int(tmp[0].strip()) - 1

    tmp = os.popen('cut -f 4 '+opt.outfile+' | sort|uniq|wc -l').readlines()
    ablife_peaknum = int(tmp[0].strip()) - 1

    ablife_overlap_percent = round(100 * float(ablife_peaknum) / ablife_total_peaknum, 2)
    piranha_overlap_percent = round(100 * float(piranha_peaknum) / piranha_total_peaknum, 2)

    print("ablife total peaks:"+str(ablife_total_peaknum))
    print("ablife overlap peaks:"+str(ablife_peaknum)+ "(" + str(ablife_overlap_percent) + "%)" )
    print("piranha total peaks:"+str(piranha_total_peaknum))
    print("piranha overlap peaks:"+str(piranha_peaknum)+ "(" + str(piranha_overlap_percent) + "%)" )




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
