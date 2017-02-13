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
1.  annovar txt
2.
"""


import re, os, sys, logging, time, datetime

from optparse import OptionParser, OptionGroup

reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess
import threading
import gffutils
import numpy
import HTSeq
import multiprocessing
import pysam
from matplotlib import pyplot
from ablib.utils.tools import *
from ablib.utils.distribution import *



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
        '-g', '--gff_file', dest='gff_file', action='store',
        type='string', help='gff file')
    p.add_option(
        '-f','--fasta_file',dest='fasta_file',action = 'store',
        type = 'string',help = 'fasta file')
    p.add_option(
        '-r','--region',dest='region',action='store',
        type = 'string',help ='the region needed for extract')
    p.add_option(
        '-o', '--outfile', dest='outfile', action='store',
        type='string', help='insection_distribution.txt')


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
        type='string',
        help='email address, if you want get a email when this job is finished,default is no email',
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
    """
    """
    rVal = ''
    for a in x:
        rVal += a + ' '
    return rVal



opt_parser, opt, args = configOpt()

if opt.logDir == "":
    opt.logDir = opt.outDir + '/log/'

# sample = ""
if opt.samplename != "":
    sample = opt.samplename

# if opt.outfile == 'distance2tss_peaks.txt':
#     opt.outfile = sample + '_distance2tss_peaks.txt'
#




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
        formatter = logging.Formatter('[%(asctime)s : %(levelname)s] %(message)s',
                                      datefmt='%y-%m-%d %H:%M')
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

def get_gff(chr,Region):
    db = gffutils.FeatureDB(opt.db)

    for region in db.features_of_type(opt.region, seqid=chr, order_by='start'):
        Region[chr].append(str(region.start) + '\t' + str(region.end))

def get_fasta(infile,chr):
    flag = 0
    for eachLine in open(infile):
        if eachLine.startswith(chr):
            flag = 1
            continue
        if flag == 1 and !eachLine.starswith(">"):


def Filter_ts_tv(outfile,data):
    """
    To calculate the SNV of
    """

    ts = 0
    tv = 0
    novel_ts = 0
    novel_tv = 0

    for s in data:
        line = s.split("\t")
        if(s.startswith("Chr")):
            index_dbsnp = line.index(opt.dbsnp)
        Cytosine = ["C","T"]
        Guanie = ["G","A"]
        if (line[3] in Cytosine) and (line[4] in Cytosine):
            ts += 1
            if line[index_dbsnp]==".":
                novel_ts += 1
            # if line[10] == ".":
            #     novel_ts += 1
        elif (line[3] in Guanie) and (line[4] in Guanie):
            ts += 1
            if line[index_dbsnp] == ".":
                novel_ts += 1
            # if line[10] == ".":
            #     novel_ts +=1
        else:
            tv += 1
            if line[index_dbsnp] == ".":
                novel_tv += 1
            # if line[10] == ".":
            #     novel_tv += 1
    with open(outfile,'w') as OUT:
        OUT.writelines("Sample\tnovel_ts\tnovel_ts/tv\tnovel_tv\tts\tts/tv\ttv\n")
        novel_pro = '{:.2f}'.format(novel_ts/float(novel_tv))
        pro = '{:.2f}'.format(ts/float(tv))
        OUT.writelines(sample + "\t" + str(novel_ts) + "\t" + str(novel_pro) + "\t" + str(novel_tv) + "\t" + str(ts) + "\t" + str(pro) + "\t" + str(tv) + "\n")

# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")
    INDEL_data = []
    SNV_data = []
    get_Data(opt.file,INDEL_data,SNV_data)

    snp_region_file1 = sample + '_SNP_Region.txt'
    Filter_Region(snp_region_file1,SNV_data)

    indel_region_file1 = sample + '_InDel_Region.txt'
    Filter_Region(indel_region_file1,INDEL_data)

    snp_type_file1 = sample + '_SNP_Type.txt'
    Filter_Type(snp_type_file1,"SNP",SNV_data)

    indel_type_file1 = sample + '_InDel_Type.txt'
    Filter_Type(indel_type_file1,"InDel",INDEL_data)

    snp_genotype_file = sample + '_SNP_GenoType.txt'
    Filter_Genotype(snp_genotype_file,SNV_data)

    indel_genotype_file = sample + '_InDel_GenoType.txt'
    Filter_Genotype(indel_genotype_file,SNV_data)

    snp_ts_tv_file = sample + '_SNP_TS_TV.txt'
    Filter_ts_tv(snp_ts_tv_file,SNV_data)


if __name__ == '__main__':

    main()
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
if not opt.keepTemp:
    os.system('rm -rf ' + tempPath)
    logging.debug("Temp folder is deleted..")
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
logging.debug("Program ended")
currentTime = datetime.datetime.now()
runningTime = (currentTime - startTime).seconds  # in seconds
logging.debug("   ：Program start at %s" % startTime)
logging.debug("   ：Program end at %s" % currentTime)
logging.debug("   ：Program ran %.2d:%.2d:%.2d" % (
runningTime / 3600, (runningTime % 3600) / 60, runningTime % 60))
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



# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def countProgram(programName, startT, runT, isTest):
    countProgramFile = open('/users/ablife/ablifepy/countProgram.txt', 'a')
    countProgramFile.write(
        programName + '\t' + str(os.getlogin()) + '\t' + str(startT) + '\t' + str(
            runT) + 's\t' + isTest + '\n')
    countProgramFile.close()


testStr = 'P'
if opt.isTest:
    testStr = 'T'
countProgram(sys.argv[0], startTime, runningTime, testStr)
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
