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
read tophat2 result
"""

###
import re, os, sys, logging, time, datetime
from optparse import OptionParser,OptionGroup
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
from ablib.utils.tools import *

###
_version = 'v1.0'


# -----------------------------------------------------------------------------------
# --- S
# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-t] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option(
        '-t', '--tophatdir', dest='tophatdir', default='./',action='store',
        type='string', help='tophat result dir,default is current dir', metavar="DIR")
    p.add_option(
        '-f', '--tophatsummary', dest='tophatsummary',default='align_summary.txt', action='store',
        type='string', help='tophat aling summary file,default is align_summary.txt', metavar="FILE")
    p.add_option(
        '-o', '--outfile', dest='outfile',default='map_result.txt', action='store',
        type='string', help='outfile file,default is map_result.txt', metavar="FILE")

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
        type='string', help='email address, if you want get a email when this job is finished,default is no email', metavar="EMAIL")
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


##
opt_parser, opt, args = configOpt()


##
if not os.path.isfile(opt.tophatdir+'/'+opt.tophatsummary):
    print('you don\'t have align_summary.txt ')
    exit()

# -----------------------------------------------------------------------------------
# --- E
# -----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------
### S
#-----------------------------------------------------------------------------------
def readTophatMapResult(resultdir, resultfile="align_summary.txt"):
# Reads:
#           Input     :  32675031
#            Mapped   :  30323782 (92.8% of input)
#             of these:   1049740 ( 3.5%) have multiple alignments (299770 have >2)
# 92.8% overall read mapping rate.
    if not os.path.isfile(resultdir+'/'+resultfile):
        print('you don\'t have align_summary.txt ')
        return
    d = {}
    linenum = 0
    for line in open(resultdir+'/'+resultfile):
        linenum +=1
        line = line.strip()
        if linenum==1 and line.startswith('Reads:'):
            continue
        if linenum==2:
            match = re.match(r'\s*Input\s*:\s*(\d+)', line)
            if not match:
                continue
            d["input_data_count"] = int(match.group(1))
        if linenum==3:
            match = re.match(r'\s*Mapped\s*:\s*(\d+)', line)
            if not match:
                continue
            d["total_mapped_reads_count"] = int(match.group(1))
        if linenum==4:
            match = re.match(r'\s*of\s*these\s*:\s*(\d+)', line)
            if not match:
                continue
            d["multiple_mapped_reads_count"] = int(match.group(1))

    d["uniq_mapped_reads_count"] = d["total_mapped_reads_count"] - d["multiple_mapped_reads_count"]
    d["total_mapped_persent"] = round(100*float(d["total_mapped_reads_count"])/d["input_data_count"],2)
    d["uniq_mapped_persent"] = round(100*float(d["uniq_mapped_reads_count"])/d["total_mapped_reads_count"],2)
    d["multiple_mapped_persent"] = round(100*float(d["multiple_mapped_reads_count"])/d["total_mapped_reads_count"],2)

    report = ""
    report += "input_data_count:"+str(d["input_data_count"])+"\n"
    report += "total_mapped_reads_count:"+str(d["total_mapped_reads_count"])+"("+str(d["total_mapped_persent"])+"%)"+"\n"
    report += "uniq_mapped_reads_count:"+str(d["uniq_mapped_reads_count"])+"("+str(d["uniq_mapped_persent"])+"%)"+"\n"
    report += "multiple_mapped_reads_count:"+str(d["multiple_mapped_reads_count"])+"("+str(d["multiple_mapped_persent"])+"%)"+"\n"

    return d,report


#-----------------------------------------------------------------------------------
### E
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
### S
#-----------------------------------------------------------------------------------
def main():
    """this is test function"""
    os.chdir( opt.outDir )
    rdir = opt.tophatdir
    rfile = opt.tophatsummary
    d,report = readTophatMapResult(rdir,rfile)
    # print(d)
    w = open(opt.outfile,"w")
    w.writelines(report)
    # print(report)




if __name__ == '__main__':
    main()



    #-----------------------------------------------------------------------------------
    ### E
    #-----------------------------------------------------------------------------------