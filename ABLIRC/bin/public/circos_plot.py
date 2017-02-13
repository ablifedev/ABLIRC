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

"""


import re, os, sys, logging, time, datetime
from optparse import OptionParser, OptionGroup
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
from ablib.utils.tools import *


# if sys.version_info < (3, 0):
# print("Python Version error: please use phthon3")
#     sys.exit(-1)


_version = 'v1.0'

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = "/".join(scriptPath.split("/")[0:-2])  # absolute bin path
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-t] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option('-c', '--coveragelist', dest='coveragelist', action='store', type='string', help='coverage file list of each sample', metavar="FILE")
    p.add_option('-n', '--namelist', dest='namelist', action='store', type='string', help='name list of each sample')
    p.add_option('-l', '--chrlen', dest='chrlen', action='store', type='string', help='chromosome length file', metavar="FILE")
    p.add_option('-m', '--minchrlen', dest='minchrlen', action='store', default=1000000, type='int', help='min chromosome length to plot,default is 1000000', metavar="INT")
    p.add_option('-g', '--gff', dest='gff', action='store', type='string', help='gff file', metavar="FILE")
    p.add_option('-u', '--chromosomesunits', dest='chromosomesunits', default=1, action='store', type='int', help='        ，   100000，          5000 ，              5000')
    p.add_option('-o', '--outfile', dest='outfile', default='reads_density_of_whole_genome_circos.png', action='store', type='string', help='output file', metavar="FILE")
    p.add_option('-d', '--circosconf', dest='circosconf', default='/users/ablife/RNA-Seq/Pipeline/Basic_Analysis_Pipeline/v2.0/circos_config/', action='store', type='string', help='circos conf template dir', metavar="DIR")

    group = OptionGroup(p, "Preset options")
    ##preset options
    group.add_option('-O', '--outDir', dest='outDir', default='./', action='store', type='string', help='output directory', metavar="DIR")
    group.add_option('-T', '--test', dest='isTest', default=False, action='store_true', help='run this program for test')
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


total_chr_len = 0
for eachLine in open(opt.chrlen):
    line = eachLine.strip().split('\t')
    if int(line[1]) >= opt.minchrlen:
        total_chr_len += int(line[1])

if opt.chromosomesunits == 1:
    opt.chromosomesunits = int(total_chr_len / 1000)

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = scriptPath + '/bin'  # absolute bin path
outPath = os.path.abspath(opt.outDir)  # absolute output path
os.mkdir(outPath) if not os.path.isdir(outPath) else None


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def make_karyotype_file(chrlen_file, chrset):
    file = 'karyotype.txt'
    w = open(file, 'w')
    flag = 0
    temp_chr = ''
    for eachline in open(chrlen_file, 'r'):
        line = eachline.strip().split('\t')
        if int(line[1]) < opt.minchrlen:
            continue
        if flag == 0:
            temp_chr = line[0]
            flag = 1
        # Chr1  30427617  ----chrlen file
        # chr - Chr1 Chr1 0 30427617 white    -----karyotype file
        chrset.add(line[0])
        w.writelines('chr - ' + line[0] + ' ' + line[0] + ' 0 ' + line[1] + ' white\n')
    w.close()
    return file, temp_chr


def make_gene_file(gff, chrset):
    file = 'gene.txt'
    w = open(file, 'w')
    for eachline in open(gff, 'r'):
        if eachline.startswith('#'):
            continue
        if eachline.startswith('\n'):
            continue
        line = eachline.strip().split('\t')
        if line[0] not in chrset:
            continue
        if line[2] == "gene":
            w.writelines(line[0] + '\t' + line[3] + '\t' + line[4] + '\n')
    w.close()
    return file


def make_circos_conf(karyotype_file, gene_file, chr):
    file = 'circos.conf'
    w = open(file, 'w')
    temp = """<<include colors_fonts_patterns.conf>>
<<include ideogram.conf>>
<<include ticks.conf>>
<<include etc/housekeeping.conf>>

<image>
dir   = .

png   = yes

# radius of inscribed circle in image
radius         = 3000p

# by default angle=0 is at 3 o'clock position
angle_offset      = -90

auto_alpha_colors = yes
auto_alpha_steps  = 5

"""
    w.writelines(temp)
    w.writelines('file  = ' + opt.outfile + '\n</image>\n')
    w.writelines('karyotype   = ' + karyotype_file + '\n')
    w.writelines('chromosomes_units = ' + str(opt.chromosomesunits) + '\n')

    temp = """
### Gene

<highlights>

z          = 0
fill_color = blue
<highlight>
"""
    w.writelines(temp)
    w.writelines('file       = ' + gene_file + '\n')

    temp = """r0         = 0.97r
r1         = 0.97r + 70p
</highlight>

</highlights>


### Reads density

<plots>

type      = line
thickness = 2

# samples
"""
    w.writelines(temp)

    coverage_files = opt.coveragelist.split(',')
    names = opt.namelist.split(',')
    n = len(coverage_files)
    width = round(0.6 / n - 0.01, 3)
    s = 0.3

    maxcov = 0

    for j in range(n):
        clist = []
        for eachLine in open(coverage_files[j]):
            line = eachLine.strip().split('\t')
            if float(line[3]) > 0:
                clist.append(float(line[3]))
        clist.sort()
        clist_n = len(clist)
        if clist[int(clist_n * 0.999)] * 1.2 > maxcov:
            maxcov = clist[int(clist_n * 0.999)] * 1.2

    print(maxcov)
    covper2 = maxcov * 0.2
    print(covper2)
    covper6 = maxcov * 0.6
    print(covper6)

    for i in range(n):
        r0 = s
        r1 = s + width
        w.writelines('<plot>\nfile    = ' + coverage_files[i] + '\nr0      = ' + str(r0) + 'r\nr1      = ' + str(r1) + 'r\n')
        temp = """max_gap = 1u
color   = black
min     = 0
max     = """ + str(maxcov) + """
thickness = 1
fill_color = black_a4
<axes>
<axis>
color     = lgreen
thickness = 2
position  = """ + str(covper6) + """
</axis>
<axis>
color     = lred
thickness = 2
position  = """ + str(covper2) + """
</axis>
</axes>
</plot>
"""
        w.writelines(temp)

        label = names[i] + '_label.txt'
        o = open(label, 'w')
        o.writelines(chr + '\t1\t1000000\t' + names[i] + '\n')
        o.close()
        # r0 = s + width
        # r1 = s + width
        s = r1 + 0.01

        w.writelines('<plot>\ntype=text\nfile    = ' + label + '\nr0      = ' + str(r1 - 0.03) + 'r\nr1      = ' + str(r1) + 'r + 700p\n')
        temp = """z = 50
color=red
label_size=60p
label_parallel=yes
label_font=condensed
padding=0p
rpadding=0p
</plot>
"""
        w.writelines(temp)
    w.writelines('</plots>\n')
    w.close()

    return file


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def main():
    """this is test function"""
    os.chdir(opt.outDir)
    cmd = '\cp ' + opt.circosconf + '/*.conf .'
    os.system(cmd)
    chrset = set()
    karyotype_file, chr = make_karyotype_file(opt.chrlen, chrset)
    gene_file = make_gene_file(opt.gff, chrset)
    circos_conf = make_circos_conf(karyotype_file, gene_file, chr)

    cmd = binPath + '/public/software/source_tar/circos/circos-0.67-7/bin/circos -conf ' + circos_conf
    os.system(cmd)


if __name__ == '__main__':

    main()



    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
