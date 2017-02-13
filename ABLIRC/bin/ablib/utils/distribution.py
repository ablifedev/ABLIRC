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
distribution
"""

###
import re, os, sys, logging, time, datetime
from optparse import OptionParser
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
import HTSeq
import numpy
import gffutils
from matplotlib import pyplot


###
_version = 'v1.0'


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------


def getPos(dbfile, pos_type):
    pos = set()
    db = gffutils.FeatureDB(dbfile)

    if pos_type.lower() == "tss":
        for gene in db.features_of_type('gene', order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    pos.add(tss_pos)
                if isoform.strand == "-":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    pos.add(tss_pos)
                break

    if pos_type.lower() == "tts":
        for gene in db.features_of_type('gene', order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    pos.add(tts_pos)
                if isoform.strand == "-":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    pos.add(tts_pos)
                break

    if pos_type.lower() == "startcodon":
        for gene in db.features_of_type('gene', order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start'):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.start, strand=cds.strand)
                        pos.add(this_pos)
                        break
                if isoform.strand == "-":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start', reverse=True):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.end, strand=cds.strand)
                        pos.add(this_pos)
                        break
                break

    if pos_type.lower() == "stopcodon":
        for gene in db.features_of_type('gene', order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start', reverse=True):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.end, strand=cds.strand)
                        pos.add(this_pos)
                        break
                if isoform.strand == "-":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start'):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.start, strand=cds.strand)
                        pos.add(this_pos)
                        break
                break

    return pos


def getPeakSummit(peakfile, peaktype="ncRNA"):
    # ncRNA peak:
    # NC_005810.1     5573    5918    +       346     216     5634    54      25985

    # clip peak:
    # #Chr    Start   End     PeakID  Tags    Strand  Length  maxHeight       Summit
    # chr1    826803  826861  chr1_382396     8       -       59      6       826829

    pos = set()

    if peaktype.lower() == "ncrna":
        for eachLine in open(peakfile):
            if eachLine.startswith('\n') or eachLine.startswith('#'):
                continue
            line = eachLine.strip().split('\t')
            chr = line[0]
            strand = line[3]
            summit = int(line[6])
            summit_pos = HTSeq.GenomicPosition(chr, summit, strand=strand)
            pos.add(summit_pos)

    if peaktype.lower() == "clip":
        for eachLine in open(peakfile):
            if eachLine.startswith('\n') or eachLine.startswith('#'):
                continue
            line = eachLine.strip().split('\t')
            chr = line[0]
            strand = line[5]
            summit = int(line[8])
            summit_pos = HTSeq.GenomicPosition(chr, summit, strand=strand)
            pos.add(summit_pos)

    return pos


def getIntervalSet(sortedbamfile, window):
    iset = list()
    for r in sortedbamfile[window]:
        iv_seq = (co.ref_iv for co in r.cigar if co.type == "M" and co.size > 0)
        for almnt in iv_seq:
            iset.append(almnt)
    return iset


def distributionToOnePoint(bamfile, dbfile, outfile, type, halfwinwidth, gff=None):
    sortedbamfile = HTSeq.BAM_Reader(bamfile)
    if gff is not None:
        db = gffutils.create_db(gff, dbfile, merge_strategy="create_unique", verbose=False, force=True)

        # fragmentsize = 200

    pos = set()
    pos = getPos(dbfile, type)

    profile = numpy.zeros(2 * halfwinwidth, dtype='i')
    for p in pos:
        print(p)
        # window = HTSeq.GenomicInterval(p.chrom,
        #                                p.pos - halfwinwidth - fragmentsize, p.pos + halfwinwidth + fragmentsize, ".")
        if p.pos < halfwinwidth:
            p.pos = halfwinwidth
        window = HTSeq.GenomicInterval(p.chrom, p.pos - halfwinwidth, p.pos + halfwinwidth, ".")

        interval_set = set()
        interval_set = getIntervalSet(sortedbamfile, window)

        for iv in interval_set:
            # almnt.iv.length = fragmentsize
            if p.strand == "+":
                start_in_window = iv.start - p.pos + halfwinwidth
                end_in_window = iv.end - p.pos + halfwinwidth
            else:
                start_in_window = p.pos + halfwinwidth - iv.end
                end_in_window = p.pos + halfwinwidth - iv.start
            start_in_window = max(start_in_window, 0)
            end_in_window = min(end_in_window, 2 * halfwinwidth)
            if start_in_window >= 2 * halfwinwidth or end_in_window < 0:
                continue
            profile[start_in_window: end_in_window] += 1
    with open(outfile, 'w') as o:
        o.writelines("#distance\tdensity\n")
        i = 0 - halfwinwidth
        for k in profile:
            o.writelines(str(i) + '\t' + str(k) + '\n')
            i += 1
    pyplot.plot(numpy.arange(-halfwinwidth, halfwinwidth), profile)
    pyplot.show()


def peakDistributionToSummit(bamorbedfile, peakfile, outfile, halfwinwidth=200, type="ncRNA"):
    intype = "bam"
    match = re.search(r'\.bam$', bamorbedfile)
    if not match:
        intype = "bed"
    # print(intype)
    sortedbamfile = HTSeq.BAM_Reader(bamorbedfile) if intype == "bam" else None
    bedga, bed_dict = store_bed_iv(bamorbedfile) if intype == "bed" else ("", "")

    sortedbamfile = HTSeq.BAM_Reader(bamorbedfile)

    pos = getPeakSummit(peakfile, peaktype=type)

    profile = numpy.zeros(2 * halfwinwidth, dtype='i')
    for p in pos:
        print(p)
        # window = HTSeq.GenomicInterval(p.chrom,
        #                                p.pos - halfwinwidth - fragmentsize, p.pos + halfwinwidth + fragmentsize, ".")
        if p.pos < halfwinwidth:
            p.pos = halfwinwidth
        window = HTSeq.GenomicInterval(p.chrom, p.pos - halfwinwidth, p.pos + halfwinwidth, ".")

        interval_set = list()
        if intype == "bam":
            interval_set = getIntervalSet(sortedbamfile, window)
        elif intype == "bed":
            # print(bed_dict)
            interval_set = get_bed_set_in_iv(bedga, bed_dict, window)

        for iv in interval_set:
            # almnt.iv.length = fragmentsize
            if p.strand == "+":
                start_in_window = iv.start - p.pos + halfwinwidth
                end_in_window = iv.end - p.pos + halfwinwidth
            else:
                start_in_window = p.pos + halfwinwidth - iv.end
                end_in_window = p.pos + halfwinwidth - iv.start
            start_in_window = max(start_in_window, 0)
            end_in_window = min(end_in_window, 2 * halfwinwidth)
            if start_in_window >= 2 * halfwinwidth or end_in_window < 0:
                continue
            profile[start_in_window: end_in_window] += 1
    with open(outfile, 'w') as o:
        o.writelines("+distance\tdensity\n")
        i = 0 - halfwinwidth
        for k in profile:
            o.writelines(str(i) + '\t' + str(k) + '\n')
            i += 1
            # pyplot.plot(numpy.arange(-halfwinwidth, halfwinwidth), profile)
            # pyplot.show()


def getPosByChr(chr, dbfile, pos_type):
    pos = set()
    db = gffutils.FeatureDB(dbfile)

    if pos_type.lower() == "tss":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    pos.add(tss_pos)
                if isoform.strand == "-":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    pos.add(tss_pos)
                break

    if pos_type.lower() == "tts":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    pos.add(tts_pos)
                if isoform.strand == "-":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    pos.add(tts_pos)
                break

    if pos_type.lower() == "startcodon":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start'):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.start, strand=cds.strand)
                        pos.add(this_pos)
                        break
                if isoform.strand == "-":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start', reverse=True):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.end, strand=cds.strand)
                        pos.add(this_pos)
                        break
                break

    if pos_type.lower() == "stopcodon":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start', reverse=True):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.end, strand=cds.strand)
                        pos.add(this_pos)
                        break
                if isoform.strand == "-":
                    for cds in db.children(isoform.id, level=1, featuretype='CDS', order_by='start'):
                        this_pos = HTSeq.GenomicPosition(cds.seqid, cds.start, strand=cds.strand)
                        pos.add(this_pos)
                        break
                break

    if pos_type.lower() == "intronstart":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    flag = 0
                    for exon in db.children(isoform.id, level=1, featuretype='exon', order_by='start', reverse=True):
                        if flag == 0:
                            flag = 1
                            continue
                        this_pos = HTSeq.GenomicPosition(exon.seqid, exon.end, strand=exon.strand)
                        pos.add(this_pos)
                if isoform.strand == "-":
                    flag = 0
                    for exon in db.children(isoform.id, level=1, featuretype='exon', order_by='start'):
                        if flag == 0:
                            flag = 1
                            continue
                        this_pos = HTSeq.GenomicPosition(exon.seqid, exon.start, strand=exon.strand)
                        pos.add(this_pos)
                break

    if pos_type.lower() == "intronend":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    flag = 0
                    for exon in db.children(isoform.id, level=1, featuretype='exon', order_by='start'):
                        if flag == 0:
                            flag = 1
                            continue
                        this_pos = HTSeq.GenomicPosition(exon.seqid, exon.start, strand=exon.strand)
                        pos.add(this_pos)
                if isoform.strand == "-":
                    flag = 0
                    for exon in db.children(isoform.id, level=1, featuretype='exon', order_by='start', reverse=True):
                        if flag == 0:
                            flag = 1
                            continue
                        this_pos = HTSeq.GenomicPosition(exon.seqid, exon.end, strand=exon.strand)
                        pos.add(this_pos)
                break

    return pos


def store_bed_iv(bedFile):
    bedfile = HTSeq.BED_Reader(bedFile)
    bedga = HTSeq.GenomicArrayOfSets("auto", stranded=False)
    n = 0
    bed_dict = {}
    for r in bedfile:
        r.name = r.line
        # print(r.line)
        n += 1
        bed_dict[str(n)] = r
        bedga[r.iv] += str(n)
    return bedga, bed_dict


def get_bed_set_in_iv(bedga, bed_dict, iv):
    iset = list()
    bfs = set()
    # print(iv)
    # print(bedga)
    for biv, fs in bedga[iv].steps():
        bfs = bfs.union(fs)
    for n in bfs:
        bed = bed_dict[n]
        iset.append(bed.iv)
    return iset


def distributionToOnePointByChr(chr, bamorbedfile, dbfile, outfile, pos_type, halfwinwidth, server_list, gff=None):
    # print(chr)
    intype = "bam"
    match = re.search(r'\.bam$', bamorbedfile)
    if not match:
        intype = "bed"
    # print(intype)
    sortedbamfile = HTSeq.BAM_Reader(bamorbedfile) if intype == "bam" else None
    bedga, bed_dict = store_bed_iv(bamorbedfile) if intype == "bed" else ("", "")

    if gff is not None:
        db = gffutils.create_db(gff, dbfile, merge_strategy="create_unique", verbose=False, force=True)

        # fragmentsize = 200

    pos = set()
    pos = getPosByChr(chr, dbfile, pos_type)

    # profile = [0 for x in range(2 * halfwinwidth)]
    profile = numpy.zeros(2 * halfwinwidth, dtype='i')
    for p in pos:
        # print(p)
        # window = HTSeq.GenomicInterval(p.chrom,
        #                                p.pos - halfwinwidth - fragmentsize, p.pos + halfwinwidth + fragmentsize, ".")
        if p.pos < halfwinwidth:
            p.pos = halfwinwidth
        window = HTSeq.GenomicInterval(p.chrom, p.pos - halfwinwidth, p.pos + halfwinwidth, ".")

        interval_set = list()
        if intype == "bam":
            interval_set = getIntervalSet(sortedbamfile, window)
        elif intype == "bed":
            # print(bed_dict)
            interval_set = get_bed_set_in_iv(bedga, bed_dict, window)

        for iv in interval_set:
            # almnt.iv.length = fragmentsize
            if p.strand == "+":
                start_in_window = iv.start - p.pos + halfwinwidth
                end_in_window = iv.end - p.pos + halfwinwidth
            else:
                start_in_window = p.pos + halfwinwidth - iv.end
                end_in_window = p.pos + halfwinwidth - iv.start
            start_in_window = max(start_in_window, 0)
            end_in_window = min(end_in_window, 2 * halfwinwidth)
            if start_in_window >= 2 * halfwinwidth or end_in_window < 0:
                continue
            profile[start_in_window:end_in_window] += 1

    server_list[chr] = profile[:]


def iv_distribution_around_gene_bychr(chr, bamorbedfile, dbfile, pos_type, halfwinwidth, gff=None):
    # print(chr)
    fout = open("_ivaround_gene_" + chr, 'w')
    intype = "bam"
    match = re.search(r'\.bam$', bamorbedfile)
    if not match:
        intype = "bed"
    # print(intype)
    sortedbamfile = HTSeq.BAM_Reader(bamorbedfile) if intype == "bam" else None
    bedga, bed_dict = store_bed_iv(bamorbedfile) if intype == "bed" else ("", "")

    if gff is not None:
        db = gffutils.create_db(gff, dbfile, merge_strategy="create_unique", verbose=False, force=True)

    for p, isoform, gene, window in getIsoformandPosByChr(chr, dbfile, pos_type, halfwinwidth):

        interval_set = list()
        if intype == "bam":
            interval_set = getIntervalSet(sortedbamfile, window)
        elif intype == "bed":
            interval_set = get_bed_set_in_iv(bedga, bed_dict, window)

        for iv in interval_set:
            if iv.strand != p.strand:
                continue
            summit_pos = iv.start + int((iv.end - iv.start) / 2)
            distance = 0
            abs_distance = 0
            if p.strand == "+":
                distance = summit_pos - p.pos
                abs_distance = abs(distance)
            else:
                distance = p.pos - summit_pos
                abs_distance = abs(distance)
            if abs_distance > halfwinwidth:
                continue
            fout.writelines(isoform.seqid + "\t" + str(isoform.start) + "\t" + str(isoform.end) + "\t" + isoform.strand + "\t" + isoform.id + "\t" + gene.id + "\t" + str(iv.start) + "\t" + str(iv.end) + "\t" + str(distance) + "\n")
    fout.close()


def getIsoformandPosByChr(chr, dbfile, pos_type, halfwinwidth):
    pos = list()
    db = gffutils.FeatureDB(dbfile)

    if pos_type.lower() == "tss":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    window = HTSeq.GenomicInterval(tss_pos.chrom, tss_pos.pos - halfwinwidth, isoform.end, tss_pos.strand)
                    if tss_pos.pos < halfwinwidth:
                        window = HTSeq.GenomicInterval(tss_pos.chrom, 0, isoform.end, tss_pos.strand)
                    pos.append((tss_pos, isoform, gene, window))
                if isoform.strand == "-":
                    tss_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    window = HTSeq.GenomicInterval(tss_pos.chrom, isoform.start, tss_pos.pos + halfwinwidth, tss_pos.strand)
                    pos.append((tss_pos, isoform, gene, window))

    if pos_type.lower() == "tts":
        for gene in db.features_of_type('gene', seqid=chr, order_by='start'):
            # print(gene)
            ## gene info
            gene_id = gene.id
            gene_strand = gene.strand
            gene_start = gene.start
            # if gene_start > 20000:
            #     break
            trans = ('mRNA', 'miRNA', 'mRNA_TE_gene', 'ncRNA', 'rRNA', 'snoRNA', 'snRNA', 'tRNA', 'transcript')
            for isoform in db.children(gene_id, level=1, featuretype=trans):
                if isoform.strand == "+":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.end, strand=isoform.strand)
                    window = HTSeq.GenomicInterval(tts_pos.chrom, isoform.start, tts_pos.pos + halfwinwidth, tts_pos.strand)
                    pos.append((tts_pos, isoform, gene, window))
                if isoform.strand == "-":
                    tts_pos = HTSeq.GenomicPosition(isoform.seqid, isoform.start, strand=isoform.strand)
                    window = HTSeq.GenomicInterval(tts_pos.chrom, tts_pos.pos - halfwinwidth, isoform.end, tts_pos.strand)
                    if tts_pos.pos < halfwinwidth:
                        window = HTSeq.GenomicInterval(tts_pos.chrom, 0, isoform.end, tts_pos.strand)
                    pos.append((tts_pos, isoform, gene, window))
    return pos


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def test():
    """this is test function"""
    pass

    # getCumulativeDataFromFile TEST
    # infile = "cisnat_classification_rpkm.txt"
    # outfile = "inflorescence_minor_ratio_Cumulative.txt"
    # getCumulativeDataFromFile(infile, 19, outfile)

    ## distributionToOnePoint TEST
    # bamfile = "accepted_hits.uniq.fix.bam"
    # dbfile = "tair10.db"
    # outfile = "startcodon"
    # type = "stopcodon"
    # halfwinwidth = 10000
    # distributionToOnePoint(bamfile, dbfile, outfile, type, halfwinwidth)
    #
    # bamfile = "/data1/project1/chend/Y.pestis_paper/CLIP-Seq/CLIP-Seq_bowtie2_0807/HFQ_Flag_clip_clean.fq/HFQ_Flag_clip_clean.fq_mapped.uniq.bam"
    # peakfile = "/data1/project1/chend/Y.pestis_paper/CLIP-Seq/CLIP_PeakCalling/Hfq_Flag/Hfq_Flag_filter.txt"
    # outfile = "test_peak.txt"
    # halfwinwidth = 100
    # peakDistributionToSummit(bamfile, peakfile, outfile, halfwinwidth, type="ncRNA")


if __name__ == '__main__':
    test()



    # -----------------------------------------------------------------------------------
    ### E
    # -----------------------------------------------------------------------------------
