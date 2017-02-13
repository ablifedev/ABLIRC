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
1.   peak summits          TSS   ，       （   10000）。
2.         peak
3.
"""


import re, os, sys, logging, time, datetime

from optparse import OptionParser, OptionGroup

reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess
import threading

sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../../../")
import gffutils
import numpy
import multiprocessing
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
        '-g', '--gff', dest='gff', action='store',
        type='string', help='gff file,do not have to provide it if db is exited')
    p.add_option(
        '-d', '--db', dest='db', default='gffdb', action='store',
        type='string', help='the gff database file to create or use')
    p.add_option(
        '-c', '--tc', dest='tc', action='store',
        type='string', help='tc file')
    p.add_option(
        '-w', '--halfwinwidth', dest='halfwinwidth', default=10000, action='store',
        type='int', help='bam file')
    p.add_option(
        '-o', '--outfile', dest='outfile', default="aroundtts.txt", action='store',
        type='string', help='aroundtts.txt')
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

if not opt.tc:
    opt_parser.error('Option -c must be assigned.\n')

if opt.logDir == "":
    opt.logDir = opt.outDir + '/log/'

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'aroundtts.txt':
    opt.outfile = sample + 'aroundtts.txt'

stat_file = sample + 'aroundtts.txt'

opt.tc = os.path.abspath(opt.tc)
opt.db = os.path.abspath(opt.db)




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


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    print("Main procedure start...")

    os.chdir(outPath)

    opt.outfile = os.path.basename(opt.outfile)
    os.system('mkdir -p ' + opt.outfile + '.tmpdir')
    os.chdir(opt.outfile + '.tmpdir')

    if opt.gff:
        db = gffutils.create_db(opt.gff, opt.db, merge_strategy="create_unique", verbose=False,
                                force=True)

    db = gffutils.FeatureDB(opt.db)

    Watcher()
    pool = multiprocessing.Pool(processes=15)

    for chr in db.seqids():
        pool.apply_async(iv_distribution_around_gene_bychr,
                         args=(chr, opt.tc, opt.db, "tts", opt.halfwinwidth))
    pool.close()
    pool.join()

    os.system("cat _ivaround_gene_* > ../" + opt.outfile + ".tmp && rm -rf _ivaround_gene_*")

    os.chdir(outPath)

    tc = {}
    for eachLine in open(opt.tc, 'r'):
        line = eachLine.strip().split('\t')
        key = line[0] + "\t" + line[1] + "\t" + line[2] + "\t" + line[5]
        value = line[3] + "\t" + line[4]
        tc[key] = value

    with open(opt.outfile, 'w') as o:
        o.writelines(
            "#chr\tisoform_s\tisoform_e\tstrand\tisoform_id\tgene_id\tpac_s\tpac_e\tpac_id\tpac_tpm\tpac_len\tdistance2tts\n")
        for eachLine in open(opt.outfile + '.tmp', 'r'):
            if eachLine.startswith('\n'):
                continue
            line = eachLine.strip().split('\t')
            key = line[0] + "\t" + line[6] + "\t" + line[7] + "\t" + line[3]
            value = tc[key]
            o.writelines(
                line[0] + "\t" + line[1] + "\t" + line[2] + "\t" + line[3] + "\t" + line[4] + "\t" + line[5] + "\t" +
                line[6] + "\t" + line[7] + "\t" + value + "\t" + str(int(line[7]) - int(line[6]) + 1) + "\t" + line[
                    8] + "\n")

    os.system('rm -rf ' + opt.outfile + ".tmp*")







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




