#!/usr/bin/env python2.7
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
from optparse import OptionParser
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
import HTSeq
import numpy
import gffutils

from matplotlib import pyplot



# if sys.version_info < (3, 0):
# print("Python Version error: please use phthon3")
# sys.exit(-1)


_version = 'v1.0'


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
class CTSS:
    """从bam中获取ctss信息的类

    """

    def __init__(self, file, iv=None, only5=False, only3=False):
        """
        :param file:
        :param cluster_dis: cluster内iv的最大间距，iv间距大于该值则会被认为是两个cluster
        :param iv:
        :param only5:
        :param only3:
        :return:
        """
        self.file = os.path.abspath(file)
        self.iv = iv
        self.only5 = only5
        self.only3 = only3

        self.depth_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
        self.cov_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
        self._getGenomicArray()

        fout = open("_ctss_" + iv.chrom, 'w')
        # fout.writelines("#chr\tposition\tstrand\ttags\n")
        self.print_ctss(fout)
        fout.close()

    def _getGenomicArray(self):
        intype = "bam"
        match = re.search(r'\.bam$', self.file)
        if not match:
            intype = "bed"
        if intype == "bam":
            iv_set = get_Bam_iv_set(self.file, self.iv, self.only5, self.only3)
            self.totaliv = len(iv_set)
            for iv in iv_set:
                self.depth_ga[iv] += 1
                self.cov_ga[iv] = 1
        elif intype == "bed":
            bedga, bed_dict = store_bed_iv(self.file)
            iv_set = get_bed_set_in_iv(bedga, bed_dict, self.iv)
            for iv in iv_set:
                self.depth_ga[iv] += 1
                self.cov_ga[iv] = 1

    def print_ctss(self, fout):
        # fout.writelines("#>chr\tposition\tstrand\ttags\n")
        for iv, value in self.depth_ga.steps():
            if value > 0:
                for i in range(iv.start, iv.end):
                    fout.writelines(iv.chrom + "\t" + str(i + 1) + "\t" + iv.strand + "\t" + str(value) + "\n")


class IVcluster:
    """分析流程中config文件的处理类

    """

    def __init__(self, file, cluster_dis=0, iv=None, only5=False, only3=False):
        """
        :param file:
        :param cluster_dis: cluster内iv的最大间距，iv间距大于该值则会被认为是两个cluster
        :param iv:
        :param only5:
        :param only3:
        :return:
        """
        self.file = os.path.abspath(file)
        self.cluster_dis = cluster_dis
        self.iv = iv
        self.only5 = only5
        self.only3 = only3
        self.totaliv = 1000000

        self.depth_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
        self.cov_ga = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
        self._getGenomicArray()

        self.blank_iv = set()
        self.cluster = HTSeq.GenomicArray("auto", stranded=True, typecode='i')
        self._cluster_iv()  ## cluster iv

        # fout = open("_ctss_" + iv.chrom, 'w')
        # # fout.writelines("#chr\tposition\tstrand\ttags\n")
        # self.print_ctss(fout)
        # fout.close()

        fout = open("cluster.txt", 'w')
        self.print_cluster(fout)
        fout.close()

    def _getGenomicArray(self):
        intype = "bam"
        match = re.search(r'\.bam$', self.file)
        if not match:
            intype = "bed"
        if intype == "bam":
            iv_set = get_Bam_iv_set(self.file, self.iv, self.only5, self.only3)
            self.totaliv = len(iv_set)
            for iv in iv_set:
                self.depth_ga[iv] += 1
                self.cov_ga[iv] = 1
        elif intype == "bed":
            bedga, bed_dict = store_bed_iv(self.file)
            self.bedga = bedga
            self.bed_dict = bed_dict
            iv_set = get_bed_set_in_iv(bedga, bed_dict, self.iv)
            for iv in iv_set:
                self.depth_ga[iv] += 1
                self.cov_ga[iv] = 1

    def _cluster_iv(self):
        forward_iv_p = None
        forward_iv_n = None
        if not self.iv:
            for iv, value in self.cov_ga.steps():
                if value == 0:
                    blank_len = iv.length
                    if blank_len > self.cluster_dis and iv.strand == "+":
                        self.blank_iv.add(iv)
                        if not forward_iv_p:
                            forward_iv_p = iv
                            continue
                        elif iv.chrom != forward_iv_p.chrom:
                            forward_iv_p = iv
                            continue
                        else:
                            cluster_start = forward_iv_p.end
                            cluster_end = iv.start
                            cluster_iv = HTSeq.GenomicInterval(iv.chrom, cluster_start, cluster_end, "+")
                            self.cluster[cluster_iv] = 1
                            forward_iv_p = iv
                    if blank_len > self.cluster_dis and iv.strand == "-":
                        self.blank_iv.add(iv)
                        if not forward_iv_n:
                            forward_iv_n = iv
                            continue
                        elif iv.chrom != forward_iv_n.chrom:
                            forward_iv_n = iv
                            continue
                        else:
                            cluster_start = forward_iv_n.end
                            cluster_end = iv.start
                            cluster_iv = HTSeq.GenomicInterval(iv.chrom, cluster_start, cluster_end, "-")
                            self.cluster[cluster_iv] = 2
                            forward_iv_n = iv

    def print_ctss(self, fout):
        # fout.writelines("#>chr\tposition\tstrand\ttags\n")
        for iv, value in self.depth_ga.steps():
            if value > 0:
                for i in range(iv.start, iv.end):
                    fout.writelines(iv.chrom + "\t" + str(i + 1) + "\t" + iv.strand + "\t" + str(value) + "\n")

    def print_cluster(self, fout, type="end5"):
        # fout.writelines("#chr\tcluster_start\tcluster_end\tclusterid\tlength\tstrand\tmaxposition\tmaxpositionTPM\tsum_depth\tsum_tpm\tcount\n")
        fout.writelines("#>chr\tcluster_start\tcluster_end\tclusterid\tlength\tstrand\n")
        fout.writelines("#raw ncRNA info\n")
        id = 0
        for iv, value in self.cluster.steps():
            length = iv.length + 1
            if value > 0:
                id += 1
                clusterid = "cluster_" + str(id)
                tc = ""
                maxposition = 0
                maxpositionTPM = 0
                sum_depth = 0
                sum_tpm = 0
                count = 0
                for iv2, value2 in self.depth_ga[iv].steps():
                    if value2 > 0:
                        tpm = round(float(value2) * 1000000 / self.totaliv, 2)
                        for i in range(iv2.start, iv2.end):
                            # tc += ">" + iv2.chrom + "\t" + str(i + 1) + "\t" + iv2.strand + "\t" + str(
                            #     tpm) + "\t" + str(value2) + "\n"
                            sum_depth += value2
                            sum_tpm += tpm
                            count += 1
                            if tpm > maxpositionTPM:
                                maxpositionTPM = tpm
                                maxposition = i
                bfs = set()
                for biv, fs in self.bedga[iv].steps():
                    bfs = bfs.union(fs)
                for n in bfs:
                    bed = self.bed_dict[n]
                    tc += bed.name + "\n"
                # fout.writelines(">" + iv.chrom + "\t" + str(iv.start) + "\t" + str(iv.end) + "\t" + clusterid + "\t" + str(length) + "\t" + iv.strand + "\t" + str(maxposition) + "\t" + str(maxpositionTPM) + "\t" + str(sum_depth) + "\t" + str(sum_tpm) + "\t" + str(count) + "\n")
                fout.writelines(">" + iv.chrom + "\t" + str(iv.start) + "\t" + str(iv.end) + "\t" + clusterid + "\t" + str(length) + "\t" + iv.strand + "\n")
                fout.writelines(tc)


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------




def get_Bam_iv_set(bamfile, iv=None, only5=False, only3=False):
    iset = list()
    sortedbamfile = HTSeq.BAM_Reader(bamfile)
    if iv:
        for almnt in sortedbamfile[iv]:
            if not almnt.aligned:
                continue

            if not only5 and not only3:
                iset.append(almnt.iv)
            end5_pos = almnt.iv.start_d_as_pos
            end3_pos = almnt.iv.end_d_as_pos

            if only5 and not only3:
                iset.append(end5_pos)

            elif only3 and not only5:
                iset.append(end3_pos)

            elif only3 and only5:
                iset.append(end5_pos)
                iset.append(end3_pos)
    else:
        for almnt in sortedbamfile:
            if not almnt.aligned:
                continue

            if not only5 and not only3:
                iset.append(almnt.iv)
            end5_pos = almnt.iv.start_d_as_pos
            end3_pos = almnt.iv.end_d_as_pos

            if only5 and not only3:
                iset.append(end5_pos)

            elif only3 and not only5:
                iset.append(end3_pos)

            elif only3 and only5:
                iset.append(end5_pos)
                iset.append(end3_pos)

    return iset


def store_bed_iv(bedFile):
    bedfile = HTSeq.BED_Reader(bedFile)
    bedga = HTSeq.GenomicArrayOfSets("auto", stranded=True)
    n = 0
    bed_dict = {}
    for r in bedfile:
        r.name = r.line
        # print(r.line)
        n += 1
        bed_dict[str(n)] = r
        bedga[r.iv] += str(n)
    return bedga, bed_dict


def get_bed_set_in_iv(bedga, bed_dict, iv=None):
    iset = list()
    bfs = set()
    # print(iv)
    # print(bedga)
    if iv:
        for biv, fs in bedga[iv].steps():
            bfs = bfs.union(fs)
    else:
        for biv, fs in bedga.steps():
            bfs = bfs.union(fs)
    for n in bfs:
        bed = bed_dict[n]
        iset.append(bed.iv)
    return iset


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def test():
    """this is test function"""
    # pass

    IVcluster(sys.argv[1],int(sys.argv[2]))


if __name__ == '__main__':

    test()



    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
