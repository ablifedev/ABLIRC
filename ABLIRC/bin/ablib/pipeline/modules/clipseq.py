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
clip seq
"""

#
# import subprocess
# import smtplib
# import email.mime.multipart
# import email.mime.text
# import multiprocessing
# import shutil
import os
from ablib.utils.tools import *
from ablib.pipeline.base import *

# version
_version = 'v2.0'



# -----------------------------------------------------------------------------------
# S
# -----------------------------------------------------------------------------------


class ClipBasic(Module):
    """   """

    def init_input(self):
        self.input_ids['FLOAT'].append('min_sum_rpkm')
        self.inputs['min_sum_rpkm'] = 0.3
        self.input_ids["DICT"].append('uniqbam')
        self.inputs['uniqbam'] = {}

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                groupname = sample1 + "_vs_" + sample2
                mydir = self.outdir + '/correlation/' + groupname
                for s in self.config.group[key]:
                    rmdupbam = self.inputs['uniqbam'][s]
                    self.qsub_cmd += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
                    self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                    self.qsub_cmd += 'python '+ self.config.gc["src"] + '/public/expression_quantity_calculation_v2.1_intron.py -d ' + self.config.gc["gffdb"] + ' -b ' + rmdupbam + ' -O ' + s + '_exp -n ' + s + ' && '
                    self.qsub_cmd += '\n'

    def make_qsub_cmd2(self):
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                groupname = sample1 + "_vs_" + sample2
                mydir = self.outdir + '/correlation/' + groupname
                self.qsub_cmd2 += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
                self.qsub_cmd2 += 'perl '+ self.config.gc["src"] + '/public/pipeline_stat_exp.pl -i ./ -p _exp -m _expression_profile.txt -c 10 -o expressed_gene_RPKM.txt -f ' + str(self.inputs["min_sum_rpkm"]) + " && "
                self.qsub_cmd2 += 'perl '+ self.config.gc["src"] + '/public/pipeline_stat_exp.pl -i ./ -p _exp -m _expression_profile.txt -c 11 -o expressed_gene_reads.txt && '
                self.qsub_cmd2 += 'Rscript '+ self.config.gc["src"] + '/plot/Cor_line.r -f expressed_gene_RPKM.txt -l 10 -s 2 -c 3 -o ./ &&'
                self.qsub_cmd2 += '\n'

    def make_post_cmd(self):
        self.post_cmd += 'cd ' + self.outdir + '/correlation/' + ' && mkdir -p Cor && cd Cor && ln -s -f ../*/*exp . && perl '+ self.config.gc["src"] + '/public/pipeline_stat_exp.pl -i ./ -p _exp -m _expression_profile.txt -c 10 -o expression_correlation.txt &&'
        self.post_cmd += 'Rscript ' + self.config.gc["src"] + '/plot/heatmap_sample_cor_from_exp.r -f expression_correlation.txt &&'
        self.post_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
        self.post_cmd += 'python '+ self.config.gc["src"] + '/public/clip_xiaoshu.py -i Sample_correlation.xls\n'


class ClipCallpeakAblife(Module):
    def init_input(self):
        self.input_ids["DICT"].append('uniqbed')
        self.input_ids["DICT"].append('uniqbam')
        self.input_ids["INT"].append("cluster_extend_times")
        self.inputs["cluster_extend_times"] = 10

    def init_output(self):
        self.output_ids["DICT"].append("peakfa")
        self.outputs["peakfa"] = {}
        self.output_ids["DICT"].append("peakinfo")
        self.outputs["peakinfo"] = {}
        self.output_ids["DICT"].append("nonoverlap_peaks")
        self.outputs["nonoverlap_peaks"] = {}
        self.output_ids["DICT"].append("peakreads")
        self.outputs["peakreads"] = {}
        self.output_ids["DICT"].append("peaksense")
        self.outputs["peaksense"] = {}
        self.output_ids["DICT"].append("peakantisense")
        self.outputs["peakantisense"] = {}
        # self.output_ids["DICT"].append("cims_expand")
        # self.outputs["cims_expand"] = {}

        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                mydir = sample1 + "_vs_" + sample2
                self.outputs['peakfa'][key] = self.outdir + '/ablife/' + mydir + '/peak.fa'
                self.outputs['peakinfo'][key] = self.outdir + '/ablife/' + mydir + '/' + sample1 + "_peak_info_addanno.txt"
                self.outputs['nonoverlap_peaks'][key] = self.outdir + '/ablife/' + mydir + '/' + sample1 + "_nonoverlap_peaks.txt"
                self.outputs['peakreads'][key] = self.outdir + '/ablife/' + mydir + '/peak_reads.bam'
                self.outputs['peaksense'][key] = self.outdir + '/ablife/' + mydir + '/' + sample1 + '_nonoverlap_sense_normalized_peak.txt'
                self.outputs['peakantisense'][key] = self.outdir + '/ablife/' + mydir + '/' + sample1 + '_nonoverlap_antisense_normalized_peak.txt'

        return  # !important: must exist return

    def check_config(self):
        return False

    def make_pre_cmd(self):

        mydir = self.outdir + '/ablife/'
        os.system('mkdir -p ' + mydir)
        self.pre_cmd += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
        self.pre_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
        self.pre_cmd += 'python ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/cal_intergenic_region.py -d ' + self.config.gc['gffdb'] + ' -i ' + self.config.gc['chrlen'] + ' && perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/intergenic_to_gff.pl -inter intergenic.txt -gff intergenic.gff && cat ' + self.config.gc['gff'] + ' intergenic.gff > all.gff && '+"source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "+'python ' + self.config.gc["src"]+'/public/gff2db.py -g all.gff -d all.db &\n'
        self.pre_cmd += 'wait\n\n'

        for s in self.config.sample:
            rawbed = self.inputs["uniqbed"][s]
            mydir = self.outdir + '/ablife/' + s + '_ablife'
            self.pre_cmd += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
            # == step1
            self.pre_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
            self.pre_cmd += 'python ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/reads_cluster.py -b ' + rawbed + ' -o _' + s + '_peak.bed && '
            self.pre_cmd += 'cat _' + s + """_peak.bed |grep -v '#' | grep '>'|perl -ne 'chomp;@line=split(/\\t/);$line[0]=~s/^>//;print $line[1],"\\t",$line[2],"\\t",$line[3],"\\t",$line[0],"\\t",$line[4],"\\t",$line[7],"\\n";' > raw_cluster.bed && """
            # == step2
            self.pre_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/cluster_normalization_to_gene_multiprocess.pl -gff ../all.gff -peak _' + s + '_peak.bed -o _' + s + '_sense_gene_peak.bed -strand sense && '
            self.pre_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/cluster_normalization_to_gene_multiprocess.pl -gff ../all.gff -peak _' + s + '_peak.bed -o _' + s + '_antisense_gene_peak.bed -strand antisense && '
            self.pre_cmd += 'python ' + self.config.gc["src"]+'/public/mapping_distribution_statics_v2.py -d ../all.db -b raw_cluster.bed -o raw_cluster_exp.txt -m raw_cluster_region_info.txt && perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/cal_trans_len.pl raw_cluster_region_info.txt ' + str(self.inputs["cluster_extend_times"]) + ' && '
            # == step3
            self.pre_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/filter_antisense_peak_present_in_sense_peak.pl -gene_sense_peak _' + s + '_sense_gene_peak.bed -gene_antisense_peak _' + s + '_antisense_gene_peak.bed -o _' + s + '_antisense_gene_peak_no_overlap.bed & \n'
        self.pre_cmd += 'wait\n\n'

    def make_qsub_cmd(self):
        # == step4
        for s in self.config.sample:
            mydir = self.outdir + '/ablife/' + s + '_ablife'
            self.qsub_cmd += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
            self.qsub_cmd += 'perl ' + self.config.gc["src"] + '/Clip-Seq/ABLIFE/silico_random_IP/run_all_genes_random_IP_qsub.pl -usesge ' + 'no' + ' -cpu ' + self.config.gc["cpu"] + ' -queue ' + self.config.gc["sgequeue"] + ' -trans_len trans_length.txt -gene_peak _' + s + '_sense_gene_peak.bed -times 500 -outdir _' + s + '_sense_P_value && '
            self.qsub_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/silico_random_IP/filter_cluster_through_max_height.pl -gene_peak _' + s + '_sense_gene_peak.bed -p_value _' + s + '_sense_P_value/p_value -o _' + s + '_sense_normalized_peak && \n'

            self.qsub_cmd += 'mkdir -p ' + mydir + ' && cd ' + mydir + ' && '
            self.qsub_cmd += 'perl ' + self.config.gc["src"] + '/Clip-Seq/ABLIFE/silico_random_IP/run_all_genes_random_IP_qsub.pl -usesge ' + 'no' + ' -cpu ' + self.config.gc["cpu"] + ' -queue ' + self.config.gc["sgequeue"] + ' -trans_len trans_length.txt -gene_peak _' + s + '_antisense_gene_peak_no_overlap.bed -times 500 -outdir _' + s + '_antisense_P_value && '
            self.qsub_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/silico_random_IP/filter_cluster_through_max_height.pl -gene_peak _' + s + '_antisense_gene_peak_no_overlap.bed -p_value _' + s + '_antisense_P_value/p_value -o _' + s + '_antisense_normalized_peak && \n'

    def make_post_cmd(self):
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                mydir = sample1 + "_vs_" + sample2
                self.post_cmd += 'cd ' + self.outdir + '/ablife/ && mkdir -p ' + mydir + ' && '
                self.post_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/CLIP_overlap_peaks.pl ' + sample1 + '_ablife/_' + sample1 + '_sense_normalized_peak ' + sample2 + '_ablife/_' + sample2 + '_sense_normalized_peak > ' + mydir + '/' + sample1 + '_nonoverlap_sense_normalized_peak.txt & '
                self.post_cmd += '\n'
                self.post_cmd += 'cd ' + self.outdir + '/ablife/ && mkdir -p ' + mydir + ' && '
                self.post_cmd += 'perl ' + self.config.gc['src'] + '/Clip-Seq/ABLIFE/CLIP_overlap_peaks.pl ' + sample1 + '_ablife/_' + sample1 + '_antisense_normalized_peak ' + sample2 + '_ablife/_' + sample2 + '_antisense_normalized_peak > ' + mydir + '/' + sample1 + '_nonoverlap_antisense_normalized_peak.txt &'
                self.post_cmd += '\n'
                self.post_cmd += 'wait\n'
                self.post_cmd += 'cd ' + self.outdir + '/ablife/' + mydir + ' && '
                self.post_cmd += 'cat ' + sample1 + '_nonoverlap_sense_normalized_peak.txt ' + sample1 + '_nonoverlap_antisense_normalized_peak.txt > ' + sample1 + '_nonoverlap_peaks.txt '
                self.post_cmd += '\n'
                # step5
                peakfile = sample1 + '_nonoverlap_peaks.txt '
                self.post_cmd += peakstat(self.config, self.outdir + '/ablife/' + mydir, peakfile, sample1, self.inputs['uniqbam'][sample1], type="clip_ablife")
        self.post_cmd += 'cd ' + self.outdir + '/ablife/ && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/pipeline_mapregion_result_stat_v2.pl -m "_peak_Mapping_distribution.txt" -i ./ -p "_vs_" -o peak_mapping_distribution.txt'
        self.post_cmd += '\n'



# class GoKegg(Module):
#
#     def init_input(self):
#         self.input_ids['DICT'].append('peakinfo_ablife')
#         self.inputs["peakinfo_ablife"] = {}
#         self.input_ids['STR'].append('GROUP1')
#         self.inputs["GROUP1"] = ""
#         self.input_ids["DICT"].append('uniqbed')
#         self.inputs["uniqbed"] = {}
#
#     def init_output(self):
#         pass
#
#     def check_config(self):
#         return False
#
#     def make_pre_cmd(self):
#         pass
#
#     def make_qsub_cmd(self):
#         for key in self.inputs.keys():
#             if key.startswith("group"):
#                 for p_name in self.inputs.keys():
#                     if p_name.startswith("peakinfo"):
#                         peakinfo = self.inputs[p_name][key]
#                         sample1 = self.inputs[key].split(":")[0]
#                         sample2 = self.inputs[key].split(":")[1]
#                         mydir = sample1 + "_vs_" + sample2
#                         gokeggdir = self.outdir + '/' + p_name.split('_')[1] + '/' + mydir + "/gokegg"
#                         self.qsub_cmd += gokegg(self.config, gokeggdir, self.config.gc['godes'], self.config.gc['species_code'], peakinfo, uppre=p_name.split('_')[1], symbol=self.config.gc['geneid_or_symbol'], kg=self.config.gc['kg'])
#                         self.qsub_cmd += '&&\n'
#
#     def make_post_cmd(self):
#         pass


class ClipStat(Module):
    """
    """

    def init_input(self):
        self.input_ids["DICT"].append("uniqbam")
        self.input_ids["DICT"].append("peaksense")
        self.input_ids["DICT"].append("peakantisense")
        self.input_ids["DICT"].append("peakall")
        self.input_ids["DICT"].append("peakreads1")
        self.input_ids["DICT"].append("peakreads2")
        self.input_ids["DICT"].append("peakreads3")
        self.input_ids["DICT"].append("peakinfo1")
        self.input_ids["DICT"].append("peakinfo2")
        self.input_ids["DICT"].append("peakinfo3")
    def init_output(self):
        # self.output_ids["DICT"].append("pas_bam_discardip")
        # self.outputs["pas_bam_discardip"] = {}
        # for s in self.config.sample:
        #     self.outputs["pas_bam_discardip"][s] = self.outdir + '/' + s + '_pas/pas_discardip.bam'
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        # ablife
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                s = sample1 + '_vs_' + sample2
                mydir = self.outdir + '/ablife/' + s
                peaknum_sense = getLineCount(self.inputs['peaksense'][key], restr='>')
                peaknum_antisense = getLineCount(self.inputs['peakantisense'][key], restr='>')
                peaknum = peaknum_sense + peaknum_antisense
                with open(mydir + '/peaknum.txt', "w") as o:
                    o.writelines("peak number:" + str(peaknum) + "\n")
        self.post_cmd += 'cd ' + self.outdir + '/ablife/ && '
        self.post_cmd += 'perl ' + self.config.gc["src"]+'/public/pipeline_stat.pl -i ./ -p _ablife -m peaknum.txt -o Peak_number_statics_of_eachsample_identified_by_ablifepipeline.txt'
        self.post_cmd += '\n'
        # nonoverlap：
        with open(self.outdir + "/peak_statics.xls", 'w') as o:
            o.writelines("group\tmethod\trmdup_reads\tpeak_number\tpeakreads_number\tgene_number\n")
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                mydir = sample1 + "_vs_" + sample2
                rmdup_bam = self.inputs['uniqbam'][sample1]
                rmdup_reads = getBamReadsNumber(rmdup_bam)
                
                ablife_nonoverlap_peak_file = self.inputs['peakinfo1'][key]
                ablife_peakreads = self.inputs['peakreads1'][key]
                ablife_peaknum = getLineCount(ablife_nonoverlap_peak_file, title=1)
                ablife_peakreadsnum = getBamReadsNumber(ablife_peakreads)
                ablife_peakreads_ratio = round(100 * float(ablife_peakreadsnum) / rmdup_reads, 2)
                tmp = os.popen("cat " + ablife_nonoverlap_peak_file + " | awk '{print $NF}'|grep  -v '\-\-'|sort|uniq |wc -l").readlines()
                ablife_genenum = int(tmp[0].strip()) - 1

                with open(self.outdir + "/peak_statics.xls", 'a') as o:
                    o.writelines(mydir + "\tablife\t" + str(rmdup_reads) + "\t" + str(ablife_peaknum) + "\t" + str(ablife_peakreadsnum) + "(" + str(ablife_peakreads_ratio) + "%)" + "\t" + str(ablife_genenum) + "\n")


    def make_qsub_cmd(self):
        overlap_dir = self.outdir + '/overlap'
        if len(self.config.group.keys())>1:
            groups = self.config.group.keys()
            groups=list(groups)
            self.qsub_cmd += "mkdir -p " + overlap_dir + " && cd " + overlap_dir + "&& "
            group1 = self.config.group[groups[0]][0]+"_vs_"+self.config.group[groups[0]][1]
            group2 = self.config.group[groups[1]][0]+"_vs_"+self.config.group[groups[1]][1]
            sample_name1=group1.split("_vs_")[0]
            sample_name2=group2.split("_vs_")[0]
            self.qsub_cmd += "cp " + self.outdir + "/ablife/" + group1 + "/" + "*" + "_nonoverlap_peaks.txt ./" + "&&"
            self.qsub_cmd += "cp " + self.outdir + "/ablife/" + group2 + "/" + "*" + "_nonoverlap_peaks.txt ./" + "&&"
            self.qsub_cmd += "cp " + self.outdir + "/ablife/" + group1 + "/" + "*" + "_peak_info_addanno.txt ./" + "&&"
            self.qsub_cmd += "cp " + self.outdir + "/ablife/" + group2 + "/" + "*" + "_peak_info_addanno.txt ./" + "&&"
            self.qsub_cmd += "cat *_nonoverlap_peaks.txt" + " | sort -k 1,1 -k 2,2n | cut -f 1-6 > _allpeaks.bed && "

            self.qsub_cmd += "bedtools cluster -s -i _allpeaks.bed > _allpeaks_cluster.bed && "
            self.qsub_cmd += "perl " + self.config.gc["src"] + "/Clip-Seq/ABLIFE/stat/clip_peak_overlap_sample.pl -a " + sample_name1 + "_peak_info_addanno.txt" + " -b " + sample_name2 + "_peak_info_addanno.txt" + " -i _allpeaks_cluster.bed -o allpeaks_cluster_type.bed && "
            self.qsub_cmd += "cat allpeaks_cluster_type.bed | awk '$NF~/sample1/' > _allpeaks_cluster_type_s1 &&"
            self.qsub_cmd += "cat allpeaks_cluster_type.bed | awk '$NF~/sample2/' > _allpeaks_cluster_type_s2 &&"
            self.qsub_cmd += "awk '{print $(NF-1)}' _allpeaks_cluster_type_s1 | sort -k 1,1n | uniq > _allpeaks_cluster_type_s1_c && "
            self.qsub_cmd += "awk '{print $(NF-1)}' _allpeaks_cluster_type_s2 | sort -k 1,1n | uniq > _allpeaks_cluster_type_s2_c && "

            self.qsub_cmd += "perl " + self.config.gc["src"] + "/public/stat_venn.pl -f _allpeaks_cluster_type_s1_c,_allpeaks_cluster_type_s2_c -l " + sample_name1 + "," + sample_name2 + " > venn.log && "
            self.qsub_cmd += "sort _allpeaks_cluster_type_s1_c _allpeaks_cluster_type_s2_c | uniq -d > " + sample_name1 + "_olp_" + sample_name2 + " && "
            self.qsub_cmd += """cat _allpeaks_cluster_type_s1 | perl -ne 'BEGIN{%cluster=();open IN,""" + sample_name1 + "_olp_" + sample_name2 + """;while(<IN>){chomp;$cluster{$_}=1;}}chomp;@line=split(/\\t/);if($cluster{$line[-2]}==1){print $_,"\\n";}' > _allpeaks_cluster_type_s1_olp_s2 && """
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
            self.qsub_cmd += "python " + self.config.gc["src"] + "/Clip-Seq/ABLIFE/stat/rm__.py && mv _allpeaks_cluster_type_s1_olp_s2.new _allpeaks_cluster_type_s1_olp_s2 &&"
            # cmd += '\n'
            self.qsub_cmd += "rm -rf ablife_venn && mv venn ablife_venn &&"
            self.qsub_cmd += "cd ablife_venn && python3 " + self.config.gc["src"] + "/Clip-Seq/ABLIFE/stat/clip_olp_list.py -olplist ../" + sample_name1 + "_olp_" + sample_name2 + " -typebed ../allpeaks_cluster_type.bed -gene1 " + sample_name1 + " -gene2 " + sample_name2 + " &&"

    def make_post_cmd(self):
        pass
        # overlap_dir = self.outdir + '/overlap'
        # self.post_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
        # self.post_cmd += "cd " + overlap_dir + "&& python " + self.config.gc["src"] + "/Clip-Seq/ABLIFE/stat/overlap_stat.py &&"
        # self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/pipeline_stat_v2.pl -i ./ -p "_vs_" -m venn.log -o Repeated_peaks_in_multiple_analysis.xls'
        # self.post_cmd += '\n'


class ClipFindMotifs(Module):
    """motif"""

    def init_input(self):
        self.input_ids["STR"].append("GROUP1")
        self.input_ids["DICT"].append("peakfa_ablife")

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                mydir = sample1 + "_vs_" + sample2
                motifdir = self.outdir + '/ablife/' + mydir + "/motif"
                peakfa = self.inputs['peakfa_ablife'][key]
                self.qsub_cmd += callmotif(self.config, motifdir, peakfa, type="clip")
                self.qsub_cmd += ' && \n'

    def make_post_cmd(self):
        pass


class ClipPlot(Module):
    """plot peaks"""

    def init_input(self):
        self.input_ids["STR"].append("GROUP1")
        self.input_ids["DICT"].append("peakinfo1")
        self.input_ids["DICT"].append("peakinfo2")
        self.input_ids["DICT"].append("cims_expand")
        self.input_ids["DICT"].append("uniqbam")

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for key in self.config.group.keys():
            if key.startswith("group"):
                sample1 = self.config.group[key][0]
                sample2 = self.config.group[key][1]
                groupname = sample1 + "_vs_" + sample2
                mydir = self.outdir + '/' + groupname
                namelist = sample2 + ',' + 'ablife_' + sample1

                rmdupbam1 = self.inputs['uniqbam'][sample1]
                rmdupbam2 = self.inputs['uniqbam'][sample2]
                bamlist = rmdupbam2 + ',' + rmdupbam1

                peakablife = self.inputs['peakinfo1'][key]

                peaklist = 'none,' + peakablife

                self.qsub_cmd += peakplot(self.config, mydir, bamlist, namelist, peaklist)
                self.qsub_cmd += ' && \n'

    def make_post_cmd(self):
        pass


class ClipReport(Module):

    def make_post_cmd(self):
        self.post_cmd = ""
        for sup in sorted(self.inputs):
            if not sup.startswith("sup"):
                continue
            sup_name = self.inputs[sup]
            sup_dir = self.outdir + '/Supplements/' + sup.capitalize() + '_' + sup_name
            # os.mkdir(sup_dir) if not os.path.isdir(sup_dir) else None  #
            os.system('mkdir -p ' + sup_dir)

            if sup_name == "Reference_genome":
                module_name = "gff"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                self.post_cmd += "cp -r " + module_dir + '/* ' + sup_dir
                self.post_cmd += '\n\n'

            if sup_name == "Clean":
                clean_info = self.inputs["clean_info"]
                # if os.path.isfile(clean_info):
                self.post_cmd += "cp " + clean_info + ' ' + sup_dir + '/Obtain_the_high_quality_clean_reads.xls'
                self.post_cmd += '\n\n'

            if sup_name == "Quality_control":
                module_name = "fastqc"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                self.post_cmd += "mkdir -p " + sup_dir + '/FastqcView && '
                self.post_cmd += "cp -r " + module_dir + '/* ' + sup_dir + '/FastqcView'
                self.post_cmd += '\n'
                for s in self.config.sample:
                    self.post_cmd += 'mkdir -p ' + sup_dir + '/' + s + '_fastqc'
                    s_path = module_dir + '/' + s + '_fastqc/Images/'
                    for root, dirs, files in os.walk(s_path):
                        for file in files:
                            file_rename = s + '_' + file
                            self.post_cmd += "&& cp " + s_path + '/' + file + ' ' + sup_dir + '/' + s + '_fastqc/' + file_rename
                    self.post_cmd += '\n'
                self.post_cmd += '\n'

            if sup_name == "Mapping":
                module_name = "basic"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                # self.post_cmd += "cp -r " + module_dir + '/* ' + sup_dir
                self.post_cmd += 'rm -rf ' + sup_dir + '/*\n'
                self.post_cmd += cpdir(module_dir, sup_dir, restr="_basic", deli="")
                self.post_cmd += '\n'
                module_name = "mapping"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                self.post_cmd += 'rm -rf ' + sup_dir + '/correlation'
                self.post_cmd += '\n'
                self.post_cmd += "cp " + module_dir + '/Mapping_of_clean_reads_on_the_reference_genome.txt ' + sup_dir
                self.post_cmd += '\n'
                ###2016/9/23 cat four picture into one. --magl
                for key in self.config.group.keys():
                    #print (key)
                    if key.startswith("group"):
                        sample1 = self.config.group[key][0]
                        sample2 = self.config.group[key][1]
                        groupname = sample1 + "_vs_" + sample2
                        self.post_cmd += 'cd ' + sup_dir + '/' + sample1 + '&&'
                        self.post_cmd += 'Rscript ' + self.config.gc['src'] + '/plot/Line_multiSample_multiText.r -f ' + sample1 + '_distance2startcodon_reads_density.txt,' + sample1 + '_distance2stopcodon_reads_density.txt,../' + sample2 + '/' + sample2 + '_distance2startcodon_reads_density.txt,../' + sample2 + '/' + sample2 + '_distance2stopcodon_reads_density.txt' + ' -s ' +  sample1 + '_distance2startcodon,' + sample1 + '_distance2stopcodon,' + sample2 + '_distance2startcodon,' + sample2 + '_distance2stopcodon' + ' -n ' + groupname + '_distance2codon_reads_density'
                        self.post_cmd += '\n'
                        self.post_cmd += 'Rscript ' + self.config.gc['src'] + '/plot/Line_multiSample_multiText.r -f ' + sample1 + '_distance2tss_reads_density.txt,' + sample1 + '_distance2tts_reads_density.txt,../' + sample2 + '/' + sample2 + '_distance2tss_reads_density.txt,../' + sample2 + '/' + sample2 + '_distance2tts_reads_density.txt' + ' -s ' +  sample1 + '_distance2tss,' + sample1 + '_distance2tts,' + sample2 + '_distance2tss,' + sample2 + '_distance2tts' + ' -n ' + groupname + '_distance2_tsstts_reads_density'
                        self.post_cmd += '\n'
                self.post_cmd += '\n\n'

            if sup_name == "Correlation":
                module_name = "basic"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name + '/correlation'
                self.post_cmd += "cp -r " + module_dir + '/* ' + sup_dir
                self.post_cmd += '\n'
                self.post_cmd += 'cd ' + sup_dir + '&& rm -rf */*/log && rm -rf Cor* result log* chrlen && rm -rf */*exp */*txt'
                self.post_cmd += '\n'
                self.post_cmd += 'cp ' + module_dir + '/Cor/Sample_correlation.* ' +  sup_dir
                self.post_cmd += '\n\n'

            if sup_name == "Peak_and_peak_gene":
                module_name = "clip_callpeak"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                self.post_cmd += "cp -r " + module_dir + '/* ' + sup_dir
                self.post_cmd += '\n'
                self.post_cmd += 'cd ' + sup_dir + '&& rm -rf temp */*_ablife && rm -rf */*/gokegg */*/motif && rm -rf */*/*bam* */*/*sense* && rm -rf overlap/*/*.bed overlap/*/*.txt && rm -rf all.* && rm -rf *.gff'
                #self.post_cmd += '\n'
                self.post_cmd += '\n\n'

            if sup_name == "Motif_results":
                module_name = "clip_callpeak"
                module_dir = self.config.gc["outdir"] + '/result/' + module_name
                self.post_cmd += 'cd ' + sup_dir + '&& '
                self.post_cmd += "find " + module_dir + """ -path "*/*/motif" -print | cat | perl -ne 'chomp;$_=~/(ablife|piranha|cims|mc)\/(\S+)\/motif/;$dir="$1/$2/";`mkdir -p $dir && cp -r $_/* $dir`;'"""
                self.post_cmd += '\n'
                self.post_cmd += 'cd ' + sup_dir + '&& rm -rf */*/bg_peak.fa '
                self.post_cmd += '\n'


        title = self.config.gc["title"]
        species = self.config.gc["species"]
        institutions = self.config.gc["institutions"]
        reportdate = self.config.gc["reportdate"]
        report_config = """
[[ablife:config]]
Title	""" + title + """
Species	""" + species + """
Institutions	""" + institutions + """
Reportdate	""" + reportdate + """
fujian	Supplements
public	assets/public
    """
        w = open(self.outdir + "/tempconfig", 'w')
        w.writelines(report_config)
        w.close()

        self.post_cmd += 'cd ' + self.outdir
        self.post_cmd += '&& find ./ -depth ! -path "./" -name "*log" -exec rm -rf {} \; -o ! -path "./" -name "_*" -exec rm -rf {} \; -o ! -path "./" -name "Rplots.pdf" -exec rm -rf {} \; -o ! -path "./" -name "*.tmp" -exec rm -rf {} \;'
        self.post_cmd += '&& rm -rf */*/temp && rm -rf temp'
        self.post_cmd += ' && cat tempconfig ' + self.config.gc['src'] + '/ReportParserTools/latest/CLIP-seq.template' + ' > report.template && perl ' + self.config.gc['src'] + '/ReportParserTools/latest/reportparser.pl -t report.template '
        self.post_cmd += '&& tree Supplements > Supplements/Supplements_tree.txt'
        self.post_cmd += '\n\n'


# -----------------------------------------------------------------------------------
# E
# -----------------------------------------------------------------------------------
