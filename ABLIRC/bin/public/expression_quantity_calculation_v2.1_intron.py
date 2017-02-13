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
      ：
1.  gene
2.randCheck_gene
3.randCheck_mRNA
      ：
  gffutils HTSeq
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
        '-g', '--gff', dest='gff', action='store',
        type='string', help='gff file,do not have to provide it if db is exited')
    p.add_option(
        '-d', '--db', dest='db', default='gffdb', action='store',
        type='string', help='the gff database file to create or use')
    p.add_option(
        '-b', '--bam', dest='bam', action='store',
        type='string', help='bam file')
    p.add_option(
        '-o', '--outfile', dest='outfile', default='expression_profile.txt', action='store',
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

    if len( sys.argv ) == 1:
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


opt_parser, opt, args = configOpt()



if opt.logDir == "":
    opt.logDir = opt.outDir + '/log/'

sample = ""
if opt.samplename != "":
    sample = opt.samplename + '_'

if opt.outfile == 'expression_profile.txt':
    opt.outfile = sample + opt.outfile

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

scriptPath = os.path.abspath(os.path.dirname(__file__))  # absolute script path
binPath = "/".join(scriptPath.split("/")[0:-1])  # absolute bin path
outPath = os.path.abspath(opt.outDir)  # absolute output path
# os.mkdir(outPath) if not os.path.isdir(outPath) else None
os.system('mkdir -p ' + outPath)
logPath = os.path.abspath(opt.logDir)
# os.mkdir(logPath) if not os.path.isdir(logPath) else None
os.system('mkdir -p ' + logPath)
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
def invert_strand(iv):
    """
    :param iv: HTSeq.GenomicInterval object
    :return: HTSeq.GenomicInterval - strand is reversed
    """
    iv2 = iv.copy()
    if iv2.strand == "+":
        iv2.strand = "-"
    elif iv2.strand == "-":
        iv2.strand = "+"
    else:
        print("strand must be + or -")
    return iv2


def getTotalBase(iv, coverage):
    totalbases = 0
    for iv2, value2 in coverage[iv].steps():
        if value2 > 0:
            totalbases += value2 * iv2.length
    return totalbases


def readChr(chr, reads, check, TMR):
    print(chr)
    reads_dict = {}
    check_dict = {}
    check_dict["randCheck_gene"] = [0 for x in range(100)]
    check_dict["randCheck_mRNA"] = [0 for x in range(100)]
    base_dict = {}

    db = gffutils.FeatureDB(opt.db)
    bamfile = HTSeq.BAM_Reader(opt.bam)

    # bamPath = os.path.abspath(os.path.dirname(opt.bam))  # absolute bamPath



    usedreads = {}
    forward_end = 0

    i = 0
    trans = (
        'mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA',
        'transcript')
    for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
        # print(gene)
        ## gene info
        gene_id = gene.id
        # print(gene_id)
        gene_strand = gene.strand
        gene_start = gene.start
        gene_end = gene.end
        # if gene_start - forward_end > 500:
        #     usedreads.clear()
        forward_end = gene_end
        # gene_name = gene.attributes['gene_name'] if isset(gene.attributes['gene_name']) else gene_id
        # gene_type = gene.attributes['gene_type'] if isset(gene.attributes['gene_type']) else "UNDEF"
        gene_name = gene_id
        gene_type = "UNDEF"
        # if dict(gene.attributes).has_key('gene_name'):
        #     gene_name = gene.attributes['gene_name'][0]
        if dict(gene.attributes).has_key('gene_type'):
            gene_type = gene.attributes['gene_type'][0]
        elif dict(gene.attributes).has_key('Note'):
            gene_type = gene.attributes['Note'][0]

        reverse_strand = "+" if gene_strand == "-" else "-"

        # if gene_start > 20000:
        # break


        reads_dict[gene_id] = {}
        reads_dict[gene_id]["exon"] = {}
        reads_dict[gene_id]["exon"]["sense"] = 0
        reads_dict[gene_id]["exon"]["anti"] = 0
        reads_dict[gene_id]["exon"]["depth"] = 0
        reads_dict[gene_id]["exon"]["coverage"] = 0
        reads_dict[gene_id]["exon"]["rpkm"] = 0
        reads_dict[gene_id]["exon"]["gene_strand"] = gene_strand
        reads_dict[gene_id]["exon"]["gene_start"] = gene_start
        reads_dict[gene_id]["exon"]["gene_end"] = gene_end
        reads_dict[gene_id]["exon"]["gene_name"] = gene_name
        reads_dict[gene_id]["exon"]["gene_type"] = gene_type

        # if gene_type[0] != "protein_coding":
        # continue

        ga = HTSeq.GenomicArray([chr], stranded=True, typecode='i')


        for exon in db.children(gene_id, featuretype="exon"):
            # print(exon)
            exon_start = exon.start
            exon_end = exon.end
            exon_iv = HTSeq.GenomicInterval(chr, exon_start - 1, exon_end, gene_strand)
            if exon_iv.length == 0:
                continue
            ga[exon_iv] = 3


        gene_iv = HTSeq.GenomicInterval(chr, gene_start - 1, gene_end, gene_strand)
        exon_len = 0
        for iv, value in ga[gene_iv].steps():
            if value >= 3:
                exon_len += iv.length
        reads_dict[gene_id]["exon"]["exon_len"] = exon_len


        ga[gene_iv] = 1
        gene_len = gene_iv.length


        reads_dict[gene_id]["exon"]["gene_len"] = gene_len


        if exon_len == 0:
            continue


        exon_total_base = 0
        coverage = HTSeq.GenomicArray([chr], stranded=True, typecode="i")


        for isoform in db.children(gene_id, level=1, featuretype=trans):
            isoform_iv = HTSeq.GenomicInterval(chr, isoform.start - 1, isoform.end, isoform.strand)
            for r in bamfile[isoform_iv]:
                r_name = r.read.name
                if usedreads.has_key(r_name):
                    if usedreads[r.read.name] == "":
                        continue
                    elif r.iv.strand == isoform_iv.strand:
                        anti_info = usedreads[r.read.name].split("::")
                        reads_dict[anti_info[0]]["exon"]["anti"] -= float(anti_info[1])

                # print("::"+r_name+"\t"+isoform.id)

                if not r.aligned:
                    continue
                r_len = len(r.read)
                iv_seq = (co.ref_iv for co in r.cigar if co.type == "M" and co.size > 0)
                iv_seq_reverse = (invert_strand(co.ref_iv) for co in r.cigar if
                                  co.type == "M" and co.size > 0)
                for iv in iv_seq:
                    # print(iv)
                    coverage[iv] += 1
                    for iv2, value2 in ga[iv].steps():

                        if value2 >= 1:
                            iv_len = iv2.length
                            exon_total_base += iv_len
                            ga[iv2] = 2
                            # print(iv_len)
                            reads_dict[gene_id]["exon"]["sense"] += float(iv_len) / r_len
                        usedreads[r.read.name] = ""
                reverse_len = 0
                reverse_flag = 0
                for iv in iv_seq_reverse:
                    for iv2, value2 in ga[iv].steps():
                        # if value2 >= 1:
                        if value2 >= 1:
                            iv_len = iv2.length
                            reads_dict[gene_id]["exon"]["anti"] += float(iv_len) / r_len
                            reverse_len += float(iv_len) / r_len
                            reverse_flag = 1
                if reverse_flag==1:
                    usedreads[r.read.name] = gene_id + "::" + str(reverse_len)


        reads_dict[gene_id]["exon"]["depth"] = round(float(exon_total_base) / gene_len, 2)


        coverage_len = 0
        for iv, value in ga[gene_iv].steps():
            if value == 2:
                coverage_len += iv.length
        reads_dict[gene_id]["exon"]["coverage"] = round(float(coverage_len) / gene_len, 2)

        reads_dict[gene_id]["exon"]["rpkm"] = round(1e9 * int(reads_dict[gene_id]["exon"]["sense"]) / gene_len / TMR, 2)

        i += 1
        if i > 0 and i % 200 == 0:
            sys.stderr.write("%s : %d gene processed.\n" % (chr, i))

        ## randCheck gene
        window = int(gene_len / 100)
        if window > 0:
            if gene_strand == "+":
                temp_randCheck_gene_list = [0 for x in range(100)]
                for iv, value in coverage[gene_iv].steps():
                    if value > 0:
                        for j in range(iv.start, iv.end):
                            temp_randCheck_gene_list[int(100 * (j - gene_start + 1) / gene_len)] += value
                for x in range(100):
                    check_dict["randCheck_gene"][x] += temp_randCheck_gene_list[x] / window
            elif gene_strand == "-":
                temp_randCheck_gene_list = [0 for x in range(100)]
                for iv, value in coverage[gene_iv].steps():
                    if value > 0:
                        for j in range(iv.start, iv.end):
                            temp_randCheck_gene_list[int(100 * (gene_end - 1 - j) / gene_len)] += value
                for x in range(100):
                    check_dict["randCheck_gene"][x] += temp_randCheck_gene_list[x] / window

        ## randCheck mRNA
        window = int(exon_len / 100)
        if window > 0:
            if gene_strand == "+":
                temp_randCheck_mRNA_list = [0 for x in range(100)]
                sum_exon_len = 0
                for iv, value in ga[gene_iv].steps():
                    if value > 2:
                        for iv2, value2 in coverage[iv].steps():
                            if value2 > 0:
                                for j in range(iv2.start, iv2.end):
                                    temp_randCheck_mRNA_list[
                                        int(100 * (sum_exon_len + j - iv.start) / gene_len)] += value2
                        sum_exon_len += iv.length
                for x in range(100):
                    check_dict["randCheck_mRNA"][x] += temp_randCheck_mRNA_list[x] / window
            elif gene_strand == "-":
                temp_randCheck_mRNA_list = [0 for x in range(100)]
                sum_exon_len = 0
                for iv, value in ga[gene_iv].steps():
                    if value > 2:
                        for iv2, value2 in coverage[iv].steps():
                            if value2 > 0:
                                for j in range(iv2.start, iv2.end):
                                    temp_randCheck_mRNA_list[
                                        int(100 * (gene_len - sum_exon_len - j + iv.start - 1) / gene_len)] += value2
                        sum_exon_len += iv.length
                for x in range(100):
                    check_dict["randCheck_mRNA"][x] += temp_randCheck_mRNA_list[x] / window

    reads[chr] = reads_dict.copy()
    check[chr] = check_dict.copy()
    del reads_dict
    del check_dict
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

    if not os.path.isfile(opt.bam + '.bai'):
        os.system("samtools index " + opt.bam)

    TMR = getBamReadsNumber(opt.bam)


    Watcher()
    pool = multiprocessing.Pool(processes=15)
    server = multiprocessing.Manager()
    reads = server.dict()
    check = server.dict()

    chr_dict = readBamHeader(opt.bam)
    for chr in db.seqids():
        if not chr in chr_dict:
            continue
        # print(chr)
        reads[chr] = {}
        check[chr] = {}
        # readChr(chr, reads, check, TMR)
        pool.apply_async(readChr,args=(chr, reads, check, TMR))
    pool.close()
    pool.join()
    # reads["chr1"]={}
    # readChr("chr1",reads["chr1"])
    os.chdir(opt.outDir)
    fout = open(opt.outfile, 'w')
    fout.writelines(
        "#Gene\tChro\tStrand\tStart\tEnd\tLength\tExonLen\tIntroLen\tDepth\tCoverage\tRPKM\tTotalReads\tSenseReads\tAntisenseReads\tGeneType\n")

    mout = open(outPath + '/' + sample + 'randCheck_mRNA.txt', 'w')
    mout.writelines("+loci\tsumCoverage\n")
    gout = open(outPath + '/' + sample + 'randCheck_gene.txt', 'w')
    gout.writelines("+loci\tsumCoverage\n")

    d = dict(reads).copy()
    c = dict(check).copy()
    server.shutdown()
    randCheck_gene_list = [0 for x in range(100)]
    randCheck_mRNA_list = [0 for x in range(100)]
    for chr in sorted(d.keys()):
        print(chr)
        for x in range(100):
            randCheck_gene_list[x] += c[chr]["randCheck_gene"][x]
            randCheck_mRNA_list[x] += c[chr]["randCheck_mRNA"][x]
        for gene in sorted(dict(d[chr]).keys()):
            fout.writelines(d[chr][gene]["exon"]["gene_name"] + "\t" + chr + "\t" + str(
                d[chr][gene]["exon"]["gene_strand"]) + "\t" + str(
                d[chr][gene]["exon"]["gene_start"]) + "\t" + str(
                d[chr][gene]["exon"]["gene_end"]) + "\t" + str(
                d[chr][gene]["exon"]["gene_len"]) + "\t" + str(
                d[chr][gene]["exon"]["exon_len"]) + "\t" + str(
                d[chr][gene]["exon"]["gene_len"] - d[chr][gene]["exon"]["exon_len"]) + "\t" + str(
                d[chr][gene]["exon"]["depth"]) + "\t" + str(
                d[chr][gene]["exon"]["coverage"]) + "\t" + str(
                d[chr][gene]["exon"]["rpkm"]) + "\t" + str(
                int(d[chr][gene]["exon"]["sense"]) + int(d[chr][gene]["exon"]["anti"])) + "\t" + str(
                int(d[chr][gene]["exon"]["sense"])) + "\t" + str(
                int(d[chr][gene]["exon"]["anti"])) + "\t" + d[chr][gene]["exon"]["gene_type"] + "\n")

    for x in range(100):
        mout.writelines(str(x) + '\t' + str(randCheck_mRNA_list[x]) + '\n')
        gout.writelines(str(x) + '\t' + str(randCheck_gene_list[x]) + '\n')

        # profile = numpy.array(randCheck_mRNA_list)
        # pyplot.plot(numpy.arange(0, 100), profile)
        # pyplot.show()
        #
        # profile = numpy.array(randCheck_gene_list)
        # pyplot.plot(numpy.arange(0, 100), profile)
        # pyplot.show()



    mout.close()
    gout.close()

    cmd = "cd " + outPath + "&& Rscript " + binPath + "/plot/Line_single_ggplot2.r -f " + sample + "randCheck_gene.txt -t " + sample + "randCheck_gene -n " + sample + "randCheck_gene -o ./ && Rscript " + binPath + "/plot/Line_single_ggplot2.r -f " + sample + "randCheck_mRNA.txt -t " + sample + "randCheck_mRNA -n " + sample + "randCheck_mRNA -o ./ \n"



    os.system(cmd)


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
logging.debug("   ：Program start at %s" % startTime)
logging.debug("   ：Program end at %s" % currentTime)
logging.debug("   ：Program ran %.2d:%.2d:%.2d" % (runningTime / 3600, (runningTime % 3600) / 60, runningTime % 60))
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



