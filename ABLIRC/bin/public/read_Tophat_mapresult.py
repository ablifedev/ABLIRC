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
from optparse import OptionParser,OptionGroup
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
from ablib.utils.tools import *


# if sys.version_info < (3, 0):
# print("Python Version error: please use phthon3")
#     sys.exit(-1)


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
        '-t', '--tophatdir', dest='tophatdir', default='./',action='store',
        type='string', help='tophat result dir,default is current dir', metavar="DIR")
    p.add_option(
        '-f', '--tophatsummary', dest='tophatsummary',default='align_summary.txt', action='store',
        type='string', help='tophat aling summary file,default is align_summary.txt', metavar="FILE")
    p.add_option(
        '-o', '--outfile', dest='outfile',default='map_result.txt', action='store',
        type='string', help='outfile file,default is map_result.txt', metavar="FILE")
    p.add_option(
        '-p', '--pairend', dest='pairend', default=False, action='store_true',
        help='pairend mapping? default is false')

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
    """获得完整的命令
    """
    rVal = ''
    for a in x:
        rVal += a + ' '
    return rVal



opt_parser, opt, args = configOpt()



if not os.path.isfile(opt.tophatdir+'/'+opt.tophatsummary):
    print('you don\'t have align_summary.txt ')
    exit()

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
                d["multiple_mapped_reads_count"] = 0
                continue
            d["multiple_mapped_reads_count"] = int(match.group(1))

    d["uniq_mapped_reads_count"] = d["total_mapped_reads_count"] - d["multiple_mapped_reads_count"]
    d["total_mapped_persent"] = round(100*float(d["total_mapped_reads_count"])/d["input_data_count"],2)
    d["uniq_mapped_persent"] = round(100*float(d["uniq_mapped_reads_count"])/d["total_mapped_reads_count"],2)
    d["multiple_mapped_persent"] = round(100*float(d["multiple_mapped_reads_count"])/d["total_mapped_reads_count"],2)

    report = ""
    report += "Total reads:"+str(d["input_data_count"])+"\n"
    report += "Total mapped:"+str(d["total_mapped_reads_count"])+"("+str(d["total_mapped_persent"])+"%)"+"\n"
    report += "Total Uniquely mapped:"+str(d["uniq_mapped_reads_count"])+"("+str(d["uniq_mapped_persent"])+"%)"+"\n"
    report += "Total Multiple mapped:"+str(d["multiple_mapped_reads_count"])+"("+str(d["multiple_mapped_persent"])+"%)"+"\n"

    return d,report


def readTophatMapResultPairend(resultdir, resultfile="align_summary.txt"):
# Left reads:
#           Input     :     10000
#            Mapped   :      9144 (91.4% of input)
#             of these:       426 ( 4.7%) have multiple alignments (14 have >20)
# Right reads:
#           Input     :     10000
#            Mapped   :      8728 (87.3% of input)
#             of these:       387 ( 4.4%) have multiple alignments (14 have >20)
# Unpaired reads:
#           Input     :    756649
#            Mapped   :    352351 (46.6% of input)
#             of these:     20191 ( 5.7%) have multiple alignments (136 have >20)
# 89.4% overall read mapping rate.
#
# Aligned pairs:      8304
#      of these:       280 ( 3.4%) have multiple alignments
#                       91 ( 1.1%) are discordant alignments
# 82.1% concordant pair alignment rate.
    if not os.path.isfile(resultdir+'/'+resultfile):
        print('you don\'t have ' + resultfile)
        return
    d = {}
    d["multiple_mapped_reads_count_unpaired"] = 0
    d["total_mapped_reads_count_unpaired"] = 0
    d["input_data_count_unpaired"] = 0
    linenum = 0
    flag = 0
    for line in open(resultdir+'/'+resultfile):
        linenum +=1
        line = line.strip()
        if line.startswith('Left reads:'):
            flag = 1
            d["multiple_mapped_reads_count_end1"] = 0
            continue
        elif line.startswith('Right reads:'):
            flag = 2
            d["multiple_mapped_reads_count_end2"] = 0
            continue
        elif line.startswith('Unpaired reads:'):
            flag = 3
            continue
        elif line.startswith('Aligned pairs:'):
            flag = 4
            d["multiple_aligned_pairs"] = 0
        if flag==1:
            match = re.match(r'\s*Input\s*:\s*(\d+)', line)
            if match:
                d["input_data_count_end1"] = int(match.group(1))
                continue
            match = re.match(r'\s*Mapped\s*:\s*(\d+)', line)
            if match:
                d["total_mapped_reads_count_end1"] = int(match.group(1))
                continue
            match = re.match(r'\s*of\s*these\s*:\s*(\d+)', line)
            if match:
                d["multiple_mapped_reads_count_end1"] = int(match.group(1))
                continue
        elif flag==2:
            match = re.match(r'\s*Input\s*:\s*(\d+)', line)
            if match:
                d["input_data_count_end2"] = int(match.group(1))
                continue
            match = re.match(r'\s*Mapped\s*:\s*(\d+)', line)
            if match:
                d["total_mapped_reads_count_end2"] = int(match.group(1))
                continue
            match = re.match(r'\s*of\s*these\s*:\s*(\d+)', line)
            if match:
                d["multiple_mapped_reads_count_end2"] = int(match.group(1))
                continue
        elif flag==3:
            match = re.match(r'\s*Input\s*:\s*(\d+)', line)
            if match:
                d["input_data_count_unpaired"] = int(match.group(1))
                continue
            match = re.match(r'\s*Mapped\s*:\s*(\d+)', line)
            if match:
                d["total_mapped_reads_count_unpaired"] = int(match.group(1))
                continue
            match = re.match(r'\s*of\s*these\s*:\s*(\d+)', line)
            if match:
                d["multiple_mapped_reads_count_unpaired"] = int(match.group(1))
                continue
        elif flag==4:
            match = re.match(r'\s*Aligned\s*pairs\s*:\s*(\d+)', line)
            if match:
                d["aligned_pairs"] = int(match.group(1))
                continue
            match = re.match(r'\s*of\s*these\s*:\s*(\d+).*multiple', line)
            if match:
                d["multiple_aligned_pairs"] = int(match.group(1))
                continue

    d["input_data_count"] = d["input_data_count_end1"] + d["input_data_count_end2"] + d["input_data_count_unpaired"]
    d["total_mapped_reads_count"] = d["total_mapped_reads_count_end1"] + d["total_mapped_reads_count_end2"] + d["total_mapped_reads_count_unpaired"]
    d["multiple_mapped_reads_count"] = d["multiple_mapped_reads_count_end1"] + d["multiple_mapped_reads_count_end2"] + d["multiple_mapped_reads_count_unpaired"]
    d["uniq_mapped_reads_count"] = d["total_mapped_reads_count"] - d["multiple_mapped_reads_count"]
    d["total_mapped_persent"] = round(100*float(d["total_mapped_reads_count"])/d["input_data_count"],2)
    d["uniq_mapped_persent"] = round(100*float(d["uniq_mapped_reads_count"])/d["total_mapped_reads_count"],2)
    d["multiple_mapped_persent"] = round(100*float(d["multiple_mapped_reads_count"])/d["total_mapped_reads_count"],2)

    d["uniq_concordant_pair"] = d["aligned_pairs"] - d["multiple_aligned_pairs"]
    d["uniq_concordant_pair_persent"] = round(100*float(d["uniq_concordant_pair"])/d["input_data_count_end1"],2)

    d["uniq_mapped_reads_count_end1"] = d["total_mapped_reads_count_end1"] - d["multiple_mapped_reads_count_end1"]
    d["total_mapped_persent_end1"] = round(100*float(d["total_mapped_reads_count_end1"])/d["input_data_count_end1"],2)
    d["uniq_mapped_persent_end1"] = round(100*float(d["uniq_mapped_reads_count_end1"])/d["total_mapped_reads_count_end1"],2)
    d["multiple_mapped_persent_end1"] = round(100*float(d["multiple_mapped_reads_count_end1"])/d["total_mapped_reads_count_end1"],2)

    d["uniq_mapped_reads_count_end2"] = d["total_mapped_reads_count_end2"] - d["multiple_mapped_reads_count_end2"]
    d["total_mapped_persent_end2"] = round(100*float(d["total_mapped_reads_count_end2"])/d["input_data_count_end2"],2)
    d["uniq_mapped_persent_end2"] = round(100*float(d["uniq_mapped_reads_count_end2"])/d["total_mapped_reads_count_end2"],2)
    d["multiple_mapped_persent_end2"] = round(100*float(d["multiple_mapped_reads_count_end2"])/d["total_mapped_reads_count_end2"],2)

    if d["input_data_count_unpaired"]>0:
        d["uniq_mapped_reads_count_unpaired"] = d["total_mapped_reads_count_unpaired"] - d["multiple_mapped_reads_count_unpaired"]
        d["total_mapped_persent_unpaired"] = round(100*float(d["total_mapped_reads_count_unpaired"])/d["input_data_count_unpaired"],2)
        d["uniq_mapped_persent_unpaired"] = round(100*float(d["uniq_mapped_reads_count_unpaired"])/d["total_mapped_reads_count_unpaired"],2)
        d["multiple_mapped_persent_unpaired"] = round(100*float(d["multiple_mapped_reads_count_unpaired"])/d["total_mapped_reads_count_unpaired"],2)

    report = ""
    report += "Total reads:"+str(d["input_data_count"])+"\n"
    report += "Total mapped:"+str(d["total_mapped_reads_count"])+"("+str(d["total_mapped_persent"])+"%)"+"\n"
    report += "Total Uniquely mapped:"+str(d["uniq_mapped_reads_count"])+"("+str(d["uniq_mapped_persent"])+"%)"+"\n"
    report += "Total Multiple mapped:"+str(d["multiple_mapped_reads_count"])+"("+str(d["multiple_mapped_persent"])+"%)"+"\n"

    report += "Total Pairs:"+str(d["input_data_count_end1"])+"\n"
    report += "Total Uniquely Concordant Pairs:"+str(d["uniq_concordant_pair"])+"("+str(d["uniq_concordant_pair_persent"])+"%)"+"\n"

    report += "End1 reads:"+str(d["input_data_count_end1"])+"\n"
    report += "End1 mapped:"+str(d["total_mapped_reads_count_end1"])+"("+str(d["total_mapped_persent_end1"])+"%)"+"\n"
    report += "End1 Uniquely mapped:"+str(d["uniq_mapped_reads_count_end1"])+"("+str(d["uniq_mapped_persent_end1"])+"%)"+"\n"
    report += "End1 Multiple mapped:"+str(d["multiple_mapped_reads_count_end1"])+"("+str(d["multiple_mapped_persent_end1"])+"%)"+"\n"
    report += "End2 reads:"+str(d["input_data_count_end2"])+"\n"
    report += "End2 mapped:"+str(d["total_mapped_reads_count_end2"])+"("+str(d["total_mapped_persent_end2"])+"%)"+"\n"
    report += "End2 Uniquely mapped:"+str(d["uniq_mapped_reads_count_end2"])+"("+str(d["uniq_mapped_persent_end2"])+"%)"+"\n"
    report += "End2 Multiple mapped:"+str(d["multiple_mapped_reads_count_end2"])+"("+str(d["multiple_mapped_persent_end2"])+"%)"+"\n"

    if d["input_data_count_unpaired"]>0:
        report += "Unpaired reads:"+str(d["input_data_count_unpaired"])+"\n"
        report += "Unpaired mapped:"+str(d["total_mapped_reads_count_unpaired"])+"("+str(d["total_mapped_persent_unpaired"])+"%)"+"\n"
        report += "Unpaired Uniquely mapped:"+str(d["uniq_mapped_reads_count_unpaired"])+"("+str(d["uniq_mapped_persent_unpaired"])+"%)"+"\n"
        report += "Unpaired Multiple mapped:"+str(d["multiple_mapped_reads_count_unpaired"])+"("+str(d["multiple_mapped_persent_unpaired"])+"%)"+"\n"




    return d,report

#-----------------------------------------------------------------------------------
### E
#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
def main():
    """this is test function"""
    os.chdir( opt.outDir )
    rdir = opt.tophatdir
    rfile = opt.tophatsummary
    if not opt.pairend:
        d,report = readTophatMapResult(rdir,rfile)
        # print(d)
        w = open(opt.outfile,"w")
        w.writelines(report)
    else:
        d,report = readTophatMapResultPairend(rdir,rfile)
        # print(d)
        w = open(opt.outfile,"w")
        w.writelines(report)
    # print(report)




if __name__ == '__main__':

    main()



    #-----------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------


