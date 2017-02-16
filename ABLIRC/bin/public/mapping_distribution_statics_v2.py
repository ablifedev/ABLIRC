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
#####################################################################################

"""
程序功能说明：
1.计算gene表达量
2.randCheck_gene
3.randCheck_mRNA
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
import signal
from matplotlib import pyplot

sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../")
# print(sys.path)

from ablib.utils.tools import *

_version = 'v0.1'

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def configOpt():
    """Init for option
    """
    usage = 'Usage: %prog [-f] [other option] [-h]'
    p = OptionParser(usage)
    ##basic options
    p.add_option('-g', '--gff', dest='gff', action='store', type='string', help='gff file,do not have to provide it if db is exited')
    p.add_option('-d', '--db', dest='db', default='gffdb', action='store', type='string', help='the gff database file to create or use')
    p.add_option('-b', '--bamorbed', dest='bamorbed', action='store', type='string', help='bam or bed file, Important: the bamfile\'s suffix must be ".bam"')
    p.add_option('-o', '--outfile', dest='outfile', default='Mapping_distribution.txt', action='store', type='string', help='gene expression file')
    p.add_option('-n', '--samplename', dest='samplename', default='', action='store', type='string', help='sample name,default is ""')
    p.add_option('-m', '--mapinfo', dest='mapinfo', default='', action='store', type='string', help='output which region peak is located on')
    p.add_option('-u', '--unstrand', dest='unstrand', default=False, action='store_true', help='unstrand library,antisense will not be considered.')

    group = OptionGroup(p, "Preset options")
    ##preset options
    group.add_option('-O', '--outDir', dest='outDir', default='./', action='store', type='string', help='output directory', metavar="DIR")
    group.add_option('-L', '--logDir', dest='logDir', default='', action='store', type='string', help='log dir ,default is same as outDir')
    group.add_option('-P', '--logPrefix', dest='logPrefix', default='', action='store', type='string', help='log file prefix')
    group.add_option('-E', '--email', dest='email', default='none', action='store', type='string', help='email address, if you want get a email when this job is finished,default is no email', metavar="EMAIL")
    group.add_option('-Q', '--quiet', dest='quiet', default=False, action='store_true', help='do not print messages to stdout')
    group.add_option('-K', '--keepTemp', dest='keepTemp', default=False, action='store_true', help='keep temp dir')
    group.add_option('-T', '--test', dest='isTest', default=False, action='store_true', help='run this program for test')
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

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'Mapping_distribution.txt':
    opt.outfile = sample + opt.outfile


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
# def invert_strand(iv):
#     """
#     :param iv: HTSeq.GenomicInterval object
#     :return: HTSeq.GenomicInterval - strand is reversed
#     """
#     iv2 = iv.copy()
#     if iv2.strand == "+":
#         iv2.strand = "-"
#     elif iv2.strand == "-":
#         iv2.strand = "+"
#     else:
#         raise ValueError, "Illegal strand"
#     return iv2

def getTotalBase(iv, coverage):
    totalbases = 0
    for iv2, value2 in coverage[iv].steps():
        if value2 > 0:
            totalbases += value2 * iv2.length
    return totalbases


# @profile
def readChrwithBam(chr, reads):
    print(chr)
    reads_dict = {}
    anti_dict = {}

    db = gffutils.FeatureDB(opt.db)
    bamfile = HTSeq.BAM_Reader(opt.bamorbed)

    usedreads = {}
    forward_end = 0

    i = 0
    ## mapping statics
    genes = ('gene','lincRNA_gene','miRNA_gene','mt_gene','processed_pseudogene','pseudogene','rRNA_gene','snoRNA_gene','snRNA_gene')
    trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
    exons = ('three_prime_UTR', 'five_prime_UTR', 'CDS', 'exon')
    for gene in db.features_of_type(genes, seqid=chr, order_by='start'):
        # print(gene)
        ## gene info
        # if not gene.seqid == chr:
        #     continue
        gene_id = gene.id
        gene_strand = gene.strand
        gene_start = gene.start
        gene_end = gene.end

        # if gene_start-forward_end>2500000:
        #     usedreads.clear()
        forward_end = gene_end



        reads_dict[gene_id] = {}
        for e in exons:
            reads_dict[gene_id][e] = 0
        reads_dict[gene_id]['intron'] = 0
        reads_dict[gene_id]['sense'] = 0
        reads_dict[gene_id]['antisense'] = 0
        reads_dict[gene_id]['noncoding_exon'] = 0
        # gene_iv = HTSeq.GenomicInterval(chr, gene.start - 1, gene.end, gene.strand)
        # for r in bamfile[gene_iv]:
        #     r_name = r.read.name
        #     if not r.aligned:
        #         continue
        #
        #     if not opt.unstrand:
        #         if r.iv.strand == gene_strand:
        #             if usedreads.has_key(r_name):
        #                 if anti_dict.has_key(r_name):
        #                     gid = anti_dict[r_name]
        #                     reads_dict[gid]['antisense'] -= 1
        #                     anti_dict.pop(r_name)
        #                     usedreads.pop(r_name)
        #                 else:
        #                     continue
        #             reads_dict[gene_id]['sense'] += 1
        #         else:
        #             if usedreads.has_key(r_name):
        #                 continue
        #             reads_dict[gene_id]['antisense'] += 1
        #             anti_dict[r_name] = gene_id
        #             usedreads[r_name] = ""
        #     else:
        #         if usedreads.has_key(r_name):
        #             continue
        #         reads_dict[gene_id]['sense'] += 1


        for isoform in db.children(gene_id, level=1):
            gas = HTSeq.GenomicArrayOfSets([chr], stranded=False)
            isoform_iv = HTSeq.GenomicInterval(chr, isoform.start - 1, isoform.end, isoform.strand)
            for gu in db.children(isoform.id, level=1, featuretype=exons):
                gu_type = gu.featuretype
                gu_start = gu.start
                gu_end = gu.end
                gu_strand = gu.strand
                gu_iv = HTSeq.GenomicInterval(chr, gu_start - 1, gu_end, gu_strand)
                gas[gu_iv] += gu_type

            for r in bamfile[isoform_iv]:
                r_name = r.read.name
                if not r.aligned:
                    continue


                if not opt.unstrand:
                    if r.iv.strand == gene_strand:
                        if usedreads.has_key(r_name):
                            if anti_dict.has_key(r_name):
                                gid = anti_dict[r_name]
                                reads_dict[gid]['antisense'] -= 1
                                anti_dict.pop(r_name)
                                usedreads.pop(r_name)
                            else:
                                continue
                        reads_dict[gene_id]['sense'] += 1
                    else:
                        if usedreads.has_key(r_name):
                            continue
                        reads_dict[gene_id]['antisense'] += 1
                        anti_dict[r_name] = gene_id
                        usedreads[r_name] = ""
                else:
                    if usedreads.has_key(r_name):
                        continue
                    reads_dict[gene_id]['sense'] += 1

                if usedreads.has_key(r_name):
                    continue
                else:
                    usedreads[r.read.name] = ""

                r_len = len(r.read)
                iv_seq = (co.ref_iv for co in r.cigar if co.type == "M" and co.size > 0)

                for iv in iv_seq:
                    # print(iv)
                    for iv2, fs in gas[iv].steps():
                        iv_len = iv2.length
                        if len(fs) == 0:
                            reads_dict[gene_id]['intron'] += float(iv_len) / r_len
                        elif len(fs) == 1 and list(fs)[0] == "exon":
                            reads_dict[gene_id]['noncoding_exon'] += float(iv_len) / r_len
                        elif len(fs) >= 1 and "CDS" in list(fs):
                            reads_dict[gene_id]['CDS'] += float(iv_len) / r_len
                        elif len(fs) >= 1:
                            for s in list(fs):
                                if s == "exon":
                                    continue
                                else:
                                    reads_dict[gene_id][s] += float(iv_len) / r_len
        i += 1
        if i > 0 and i % 1000 == 0:
            sys.stderr.write("%s : %d gene processed.\n" % (chr, i))
            # if i==400:
            #     break

    reads[chr] = reads_dict.copy()
    del reads_dict
    logging.info("done %s" % chr)


def readChrwithBed(chr, reads, peaks):
    print(chr)
    reads_dict = {}
    peaks_dict = {}
    anti_dict = {}
    genes = ('gene','lincRNA_gene','miRNA_gene','mt_gene','processed_pseudogene','pseudogene','rRNA_gene','snoRNA_gene','snRNA_gene')
    trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
    exons = ('three_prime_UTR', 'five_prime_UTR', 'CDS', 'exon')

    db = gffutils.FeatureDB(opt.db)
    bedfile = HTSeq.BED_Reader(opt.bamorbed)


    bedga = HTSeq.GenomicArrayOfSets([chr], stranded=False)
    n = 0
    bed_dict = {}
    for r in bedfile:
        if r.iv.chrom != chr:
            continue
        # if r.name == "--":
        #     r.name = r.iv.chrom + "\t" + str(r.iv.start) + "\t" + str(
        #         r.iv.end) + "\t" + r.name + "\t" + str(r.score) + "\t" + r.iv.strand
        # r.name = r.iv.chrom + "\t" + str(r.iv.start) + "\t" + str(
        #     r.iv.end) + "\t" + r.name + "\t" + str(r.score) + "\t" + r.iv.strand
        r.name = r.line
        # print(r.line)
        n += 1
        bed_dict[str(n)] = r
        bedga[r.iv] += str(n)
        peaks_dict[r.name] = {}
        for e in exons:
            peaks_dict[r.name][e] = 0
        peaks_dict[r.name]['intron'] = 0
        peaks_dict[r.name]['sense'] = 0
        peaks_dict[r.name]['antisense'] = 0
        peaks_dict[r.name]['noncoding_exon'] = 0
        peaks_dict[r.name]['gene'] = "--"

    usedreads = {}
    forward_end = 0

    i = 0
    for gene in db.features_of_type(genes, seqid=chr, order_by='start'):
        # print(gene)
        ## gene info
        # if not gene.seqid == chr:
        #     continue
        gene_id = gene.id
        gene_strand = gene.strand
        gene_start = gene.start
        gene_end = gene.end

        # if gene_start-forward_end>2500000:
        #     usedreads.clear()
        forward_end = gene_end

        ## mapping statics


        reads_dict[gene_id] = {}
        for e in exons:
            reads_dict[gene_id][e] = 0
        reads_dict[gene_id]['intron'] = 0
        reads_dict[gene_id]['sense'] = 0
        reads_dict[gene_id]['antisense'] = 0
        reads_dict[gene_id]['noncoding_exon'] = 0
        gene_iv = HTSeq.GenomicInterval(chr, gene.start - 1, gene.end, gene.strand)

        bfs = set()
        for biv, fs in bedga[gene_iv].steps():
            bfs = bfs.union(fs)



        # for n in bfs:
        #     bed = bed_dict[n]
        #     bedname = bed.name
        #     bediv = bed.iv
        #     if not opt.unstrand:
        #         if bediv.strand == gene_strand:
        #             if usedreads.has_key(bedname):
        #                 if anti_dict.has_key(bedname):
        #                     gid = anti_dict[bedname]
        #                     reads_dict[gid]['antisense'] -= 1
        #                     peaks_dict[bedname]['antisense'] = 0
        #                     anti_dict.pop(bedname)
        #                     usedreads.pop(bedname)
        #                 else:
        #                     continue
        #             peaks_dict[bedname]['gene'] = gene_id
        #             reads_dict[gene_id]['sense'] += 1
        #         else:
        #             if usedreads.has_key(bedname):
        #                 continue
        #             reads_dict[gene_id]['antisense'] += 1
        #             peaks_dict[bedname]['antisense'] = 1
        #             anti_dict[bedname] = gene_id
        #             peaks_dict[bedname]['gene'] = gene_id
        #             usedreads[bedname] = ""
        #     else:
        #         if usedreads.has_key(bedname):
        #             continue
        #         peaks_dict[bedname]['gene'] = gene_id
        #         reads_dict[gene_id]['sense'] += 1


        for isoform in db.children(gene_id, level=1):
            gas = HTSeq.GenomicArrayOfSets([chr], stranded=False)
            isoform_iv = HTSeq.GenomicInterval(chr, isoform.start - 1, isoform.end, isoform.strand)
            for gu in db.children(isoform.id, level=1, featuretype=exons):
                gu_type = gu.featuretype
                gu_start = gu.start
                gu_end = gu.end
                gu_strand = gu.strand
                gu_iv = HTSeq.GenomicInterval(chr, gu_start - 1, gu_end, gu_strand)
                gas[gu_iv] += gu_type


            bfs = set()
            for biv, fs in bedga[isoform_iv].steps():
                bfs = bfs.union(fs)



            for n in bfs:
                bed = bed_dict[n]
                bedname = bed.name
                bediv = bed.iv

                if not opt.unstrand:
                    if bediv.strand == gene_strand:
                        if usedreads.has_key(bedname):
                            if anti_dict.has_key(bedname):
                                gid = anti_dict[bedname]
                                reads_dict[gid]['antisense'] -= 1
                                peaks_dict[bedname]['antisense'] = 0
                                anti_dict.pop(bedname)
                                usedreads.pop(bedname)
                            else:
                                continue
                        peaks_dict[bedname]['gene'] = gene_id
                        reads_dict[gene_id]['sense'] += 1
                    else:
                        if usedreads.has_key(bedname):
                            continue
                        reads_dict[gene_id]['antisense'] += 1
                        peaks_dict[bedname]['antisense'] = 1
                        anti_dict[bedname] = gene_id
                        peaks_dict[bedname]['gene'] = gene_id
                        usedreads[bedname] = ""
                else:
                    if usedreads.has_key(bedname):
                        continue
                    peaks_dict[bedname]['gene'] = gene_id
                    reads_dict[gene_id]['sense'] += 1

                if usedreads.has_key(bedname):
                    continue
                else:
                    usedreads[bedname] = ""
                r_len = bediv.length

                for iv, fs in gas[bediv].steps():
                    iv_len = iv.length
                    if len(fs) == 0:
                        reads_dict[gene_id]['intron'] += float(iv_len) / r_len
                        peaks_dict[bedname]['intron'] += float(iv_len) / r_len
                    elif len(fs) == 1 and list(fs)[0] == "exon":
                        reads_dict[gene_id]['noncoding_exon'] += float(iv_len) / r_len
                        peaks_dict[bedname]['noncoding_exon'] += float(iv_len) / r_len
                    elif len(fs) >= 1 and "CDS" in list(fs):
                        reads_dict[gene_id]['CDS'] += float(iv_len) / r_len
                        peaks_dict[bedname]['CDS'] += float(iv_len) / r_len
                    elif len(fs) >= 1:
                        for s in list(fs):
                            if s == "exon":
                                continue
                            else:
                                reads_dict[gene_id][s] += float(iv_len) / r_len
                                peaks_dict[bedname][s] += float(iv_len) / r_len
        i += 1
        if i > 0 and i % 1000 == 0:
            sys.stderr.write("%s : %d gene processed.\n" % (chr, i))
            # if i==400:
            #     break

    reads[chr] = reads_dict.copy()
    peaks[chr] = peaks_dict.copy()
    del reads_dict
    del peaks_dict
    logging.info("done %s" % chr)


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

    TMR = 0
    bedtitle = ""
    if intype == "bam":
        if not os.path.isfile(opt.bamorbed + '.bai'):
            os.system("samtools index " + opt.bamorbed)
        TMR = getBamReadsNumber(opt.bamorbed)
        print(TMR)
    else:
        bedtitle = getTitle(opt.bamorbed)
        for line in open(opt.bamorbed):
            if line.startswith("#") or line.startswith("track") or line.startswith("\n"):
                continue
            TMR += 1
        print(TMR)


    Watcher()
    pool = multiprocessing.Pool(processes=15)
    server = multiprocessing.Manager()
    reads = server.dict()
    peaks = server.dict()

    if intype == "bam":
        chr_dict = readBamHeader(opt.bamorbed)
        for chr in db.seqids():
            if not chr in chr_dict:
                continue
            # print(chr)
            reads[chr] = {}
            # runjobs(readChrwithBam,arglist,10)
            pool.apply_async(readChrwithBam, args=(chr, reads))

            # pool.apply_async(func, (chr,))
    else:
        for chr in db.seqids():
            # print(chr)
            reads[chr] = {}
            pool.apply_async(readChrwithBed, args=(chr, reads, peaks))
    pool.close()
    pool.join()

    d = dict(reads).copy()
    p = dict(peaks).copy()
    server.shutdown()
    types = ('three_prime_UTR', 'five_prime_UTR', 'CDS', 'noncoding_exon', 'intron')
    ori = ('sense', 'antisense')
    total_dict = {}
    for k in types:
        total_dict[k] = 0
    for k in ori:
        total_dict[k] = 0
    total_dict["intergenic"] = 0

    for chr in d:
        # print(chr)
        for gene in d[chr]:
            # print(gene)
            for t in types:
                total_dict[t] += d[chr][gene][t]
            for o in ori:
                total_dict[o] += d[chr][gene][o]

    print(total_dict["sense"])
    # total_dict["intergenic"] = TMR - total_dict["sense"] - total_dict["antisense"]
    total_dict["intergenic"] = TMR - total_dict["three_prime_UTR"] - total_dict["five_prime_UTR"] - total_dict["CDS"] - total_dict["noncoding_exon"] - total_dict["intron"] - total_dict["antisense"]
    if total_dict["intergenic"] < 0:
        total_dict["intergenic"] = 0

    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    fout.writelines("+Type\tReads\n")
    for k, v in total_dict.items():
        if k == "sense":
            continue
        if opt.unstrand and k == "antisense":
            continue
        fout.writelines("%s\t%s\n" % (k, int(v)))


    fout.close()
    cmd = "cd " + outPath + "&& Rscript " + scriptPath + "/../plot/Bar_single_Mapping_distribution.r -f " + opt.outfile + " -t " + sample + "Mapping_distribution -n " + sample + "Mapping_distribution -o ./ \n"
    os.system(cmd)


    if opt.mapinfo != "":
        w = open(opt.mapinfo, 'w')
        w.writelines(bedtitle + "\tregionInfo\tGeneID\n")
        for chr in p:
            for peak in p[chr]:
                w.writelines(peak + "\t")
                pflag = 0
                for t in types:
                    if p[chr][peak][t] > 0:
                        w.writelines(t + ":" + str(round(p[chr][peak][t], 2)) + ";")
                        pflag = 1
                if p[chr][peak]["antisense"] > 0:
                    # w.writelines("antisense:" + str(round(p[chr][peak]["antisense"], 2)) + ";")
                    w.writelines("antisense;")
                    pflag = 1
                if pflag == 0:
                    w.writelines("intergenic;")
                w.writelines("\t" + p[chr][peak]['gene'] + "\n")
        w.close()


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



