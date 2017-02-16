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
程序功能说明：
1.统计reads or peaks 相对于TTS,TSS,STARTCODON,STOPCODON的分布
程序设计思路：
利用gffutils和HTSeq包进行统计
"""


import re, os, sys, logging, time, datetime
from optparse import OptionParser, OptionGroup

reload(sys)
sys.setdefaultencoding('utf-8')

import subprocess
import threading
import gffutils
import HTSeq
import numpy
import multiprocessing
from matplotlib import pyplot

sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../../")
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
    usage = 'Usage: %prog [option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option(
        '-g', '--gff', dest='gff', action='store',
        type='string', help='gff file,do not have to provide it if db is exited')
    p.add_option(
        '-d', '--db', dest='db', default='gffdb', action='store',
        type='string', help='the gff database file to create or use')
    p.add_option(
        '-b', '--bamorbed', dest='bamorbed', action='store',
        type='string', help='bam or bed file, Important: the bamfile\'s suffix must be ".bam"')
    p.add_option(
        '-w', '--halfwinwidth', dest='halfwinwidth', default=1000, action='store',
        type='int', help='halfwinwidth,default is 1000')
    p.add_option(
        '-p', '--postype', dest='postype', action='store',
        type='string', help='gene position type:tss,tts,startcodon,stopcodon,intronstart,intronend')
    p.add_option(
        '-o', '--outfile', dest='outfile', default="distance2xxx_reads_density.txt", action='store',
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

if not opt.postype:
    opt_parser.error('Option -p must be assigned.\n')

if opt.logDir == "":
    opt.logDir = opt.outDir + '/log/'

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'distance2xxx_reads_density.txt':
    opt.outfile = sample + 'distance2' + opt.postype + '_reads_density.txt'



intype = "bam"
match = re.search(r'\.bam$', opt.bamorbed)
if not match:
    intype = "bed"

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = "/".join(scriptPath.split("/")[0:-2])  # absolute bin path
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
    print("Main procedure start...")



    if opt.gff:
        db = gffutils.create_db(opt.gff, opt.db, merge_strategy="create_unique", verbose=False, force=True)

    db = gffutils.FeatureDB(opt.db)


    Watcher()
    pool = multiprocessing.Pool(processes=15)
    server = multiprocessing.Manager()
    dis = server.dict()

    for chr in db.seqids():
        # if chr != "chr1":
        #     continue
        if intype == "bam":
            chr_dict = readBamHeader(opt.bamorbed)
            if not chr in chr_dict:
                continue
        # print(chr)
        dis[chr] = [0 for x in range(2 * opt.halfwinwidth)]
        pool.apply_async(distributionToOnePointByChr,
                         args=(chr, opt.bamorbed, opt.db, opt.outfile, opt.postype, opt.halfwinwidth, dis))
    pool.close()
    pool.join()

    d = dict(dis).copy()
    server.shutdown()

    profile = numpy.zeros(2 * opt.halfwinwidth, dtype='i')
    for chr in sorted(d.keys()):
        wincvg = numpy.fromiter(d[chr], dtype='i', count=2 * opt.halfwinwidth)
        profile += wincvg
    # pyplot.plot( numpy.arange( -opt.halfwinwidth, opt.halfwinwidth ), profile )
    # pyplot.show()

    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    fout.writelines(
        "+distance\tdensity\n")

    n = 0
    for i in range(-opt.halfwinwidth, opt.halfwinwidth):
        fout.writelines(str(i) + '\t' + str(profile[n]) + '\n')
        n += 1
    fout.close()

    cmd = "cd " + outPath + "&& R --slave < " + binPath + "/plot/Line_single_ggplot2.r --args " + opt.outfile + " " + sample + 'distance2' + opt.postype + '_reads_density ./ \n'
    os.system(cmd)








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



