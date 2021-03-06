#!/usr/bin/env python3
# coding: utf-8

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
汇总有用的工具函数
"""


import re, os, sys, logging, time, datetime
from optparse import OptionParser, OptionGroup
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../")
from ablib.utils.tools import *


# if sys.version_info < (3, 0):
# print("Python Version error: please use phthon3")
# sys.exit(-1)


_version = 'v1.0'


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-t] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option(
        '-i', '--infile', dest='infile', action='store',
        type='string', help='input file', metavar="FIEL")
    p.add_option(
        '-n', '--column_number', dest='column_number', default=0, action='store',
        type='int', help='column number to cumulative', metavar="INT")
    p.add_option(
        '-o', '--outfile', dest='outfile', default='Cumulative.txt', action='store',
        type='string', help='outfile file,default is Cumulative.txt', metavar="FILE")
    p.add_option(
        '-k', '--keyname', dest='keyname', default="ratio", action='store',
        type='string', help='key name')

    group = OptionGroup(p, "Preset options")
    ##preset options
    group.add_option(
        '-O', '--outDir', dest='outDir', default='./', action='store',
        type='string', help='output directory', metavar="DIR")
    group.add_option(
        '-l', '--logPrefix', dest='logPrefix', default='', action='store',
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



# if not os.path.isfile(opt.tophatdir+'/'+opt.tophatsummary):
#     print('you don\'t have align_summary.txt ')
#     exit()

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
### S
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
### E
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
def main():
    """this is test function"""
    os.chdir(opt.outDir)

    getCumulativeDataFromFile(opt.infile, opt.column_number, opt.outfile, keyname=opt.keyname)


if __name__ == '__main__':

    main()



    #-----------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------