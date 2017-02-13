#!/usr/bin/env python

####################################################################################
### Copyright (C) 2015-2019 by ABLIFE
####################################################################################

####################################################################################
###
####################################################################################
# Date           Version       Author            ChangeLog
#
#
#
#####################################################################################

"""

"""

###
import re, os, sys, logging, time, datetime
from optparse import OptionParser, OptionGroup

# import subprocess
sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "./")
from ablib.utils.tools import *
from ablib.pipeline.pipeline_main import *


###
# if sys.version_info < (3, 0):
#     print("Python Version error: please use phthon3")
#     sys.exit(-1)

###
_version = 'v1.0'


# -----------------------------------------------------------------------------------
# --- S
# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-c] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option('-c', '--config', dest='configfile', action='store', type='string', help='config file', metavar="FILE")
    p.add_option('--showgenome', dest='showgenome', default=False, action='store_true', help='showgenome')
    p.add_option('--genomeid', dest='genomeid', default='all', action='store', type='string', help='genome id', metavar="STRING")
    p.add_option('-g', '--genomedb', dest='genomedb', default='/data0/Genome/genome_db.xls', action='store', type='string', help='genome db file', metavar="FILE")
    p.add_option('--makecmd', dest='makecmd', default=False, action='store_true', help='make cmd only')
    p.add_option('--runpostonly', dest='runpostonly', default=False, action='store_true', help='run post cmd only')
    ##preset options
    group = OptionGroup(p, "Preset options")
    group.add_option('-O', '--outDir', dest='outDir', default='./', action='store', type='string', help='output directory,default is ./', metavar="DIR")
    group.add_option('-L', '--logDir', dest='logDir', default='', action='store', type='string', help='log dir ,default is outDir/log')
    group.add_option('-P', '--logPrefix', dest='logPrefix', default='', action='store', type='string', help='log file prefix')
    group.add_option('-E', '--email', dest='email', default='none', action='store', type='string', help='email address, if you want get a email when this job is finished,default is no email', metavar="EMAIL")
    group.add_option('-Q', '--quiet', dest='quiet', default=False, action='store_true', help='do not print messages to stdout')
    group.add_option('-K', '--keepTemp', dest='keepTemp', default=True, action='store_false', help='keep temp dir')
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


##
opt_parser, opt, args = configOpt()

##
if not opt.configfile and not opt.showgenome:
    opt_parser.error('Option -c must be assigned.\n')

if opt.logDir == "":
    opt.logDir = opt.outDir + '/logs/'
# -----------------------------------------------------------------------------------
# --- E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------

###
scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = scriptPath + '/bin'  # absolute bin path
outPath = os.path.abspath(opt.outDir)  # absolute output path
os.mkdir(outPath) if not os.path.isdir(outPath) else None
tempPath = outPath + '/temp/'  # absolute bin path
os.mkdir(tempPath) if not os.path.isdir(tempPath) else None
resultPath = outPath + '/result/'
os.mkdir(resultPath) if not os.path.isdir(resultPath) else None
logPath = os.path.abspath(opt.logDir)
os.mkdir(logPath) if not os.path.isdir(logPath) else None


# srcpath = scriptPath if not opt.srcDir else os.path.abspath(opt.srcDir)


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
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

os.system('rm -rf ' + opt.outDir + '/log && ln -s ' + logFile + ' ' + opt.outDir + '/log')
# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
logging.debug('Program version: %s' % _version)
logging.debug('Start the program with [ python3 %s ]\n', listToString(sys.argv))
startTime = datetime.datetime.now()
logging.debug("Program start at %s" % startTime)


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def main():
    os.chdir(outPath)  #

    if opt.showgenome:
        g = Genome(opt.genomedb)
        g.showGenome(id=opt.genomeid)
        return None

    logging.info("Main procedure start...")

    ##
    configfile = os.path.abspath(opt.configfile)
    config = Config()
    config.readConfigFile(configfile)
    config.gc['src'] = scriptPath  #

    if os.path.exists(scriptPath + '/__VERSION__'):
        logging.info('Version:')
        ver = ''
        for line in open(scriptPath + '/__VERSION__'):
            line = line.strip()
            ver += line + ' '
        logging.info(ver)
    else:
        logging.info('Version: [dev]')

    if opt.makecmd:
        config.gc["make-cmd-only"] = True
    if to_bool(config.gc["make-cmd-only"]):
        logging.info("make-cmd-only modle")

    if opt.runpostonly:
        config.gc["run-post-only"] = True
    if to_bool(config.gc["run-post-only"]):
        logging.info("run-post-only modle")

    logging.info("Load config file successfully")

    for order in sorted(config.switchorder, key=int):
        fi = open('finished_modules.txt', "a")
        if len(config.switchorder[order]) == 0:
            continue
        runThem(config.switchorder[order], config, fi)
        fi.close()


if __name__ == '__main__':
    ###
    main()
# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
if not opt.keepTemp:
    os.system('rm -rf ' + tempPath)
    logging.debug("Temp folder is deleted..")
# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S Getting Total Run Time
# -----------------------------------------------------------------------------------
logging.debug("Program ended")
currentTime = datetime.datetime.now()
runningTime = (currentTime - startTime).seconds  # in seconds
logging.debug("Program start at %s" % startTime)
logging.debug("Program end at %s" % currentTime)
logging.debug("Program ran %.2d:%.2d:%.2d" % (runningTime / 3600, (runningTime % 3600) / 60, runningTime % 60))
# -----------------------------------------------------------------------------------
### S Getting Total Run Time
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
if opt.email != "none":
    run_cmd = listToString(sys.argv)
    sendEmail(opt.email, str(startTime), str(currentTime), run_cmd, outPath)
    logging.info("Email to %s" % opt.email)


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
