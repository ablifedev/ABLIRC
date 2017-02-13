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
public
"""

###
# import subprocess
# import smtplib
# import email.mime.multipart
# import email.mime.text
# import multiprocessing
# import shutil

# sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../../")
from ablib.utils.tools import *
from ablib.pipeline.base import *


# if sys.version_info < (3, 0):
# print("Python Version error: please use phthon3")
# sys.exit(-1)


_version = 'v2.0'


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------

class Gff(Module):
    """Gff"""

    def init_input(self):
        pass

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_qsub_cmd(self):
        self.qsub_cmd += 'cd ' + self.outdir + ' && perl ' + self.config.gc['src'] + '/public/format/gff/stat_coding_gene_type.pl ' + self.config.gc["gff"] + ' ' + self.config.gc["species"] + ' && '
        self.qsub_cmd += '\n'
        self.qsub_cmd += 'cd ' + self.outdir + ' && perl ' + self.config.gc['src'] + '/public/format/gff/stat_gff_region_len.pl ' + self.config.gc["gff"] + ' ' + self.config.gc['chrlen'] + ' ' + self.config.gc["species"] + ' && '
        self.qsub_cmd += '\n'

    def makde_pre_cmd(self):
        pass

    def make_post_cmd(self):
        pass


class Fastqc(Module):
    """Fastqc"""

    def init_input(self):
        pass

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_qsub_cmd(self):
        for s in self.config.sample:
            if self.config.sample[s]['pe'] == "single":
                fq_name = re.sub(r'\S+/', '', self.config.sample[s]['single'])
                if fq_name.endswith('.fastq'):
                    fq_name = re.sub(r'\.fastq', '', fq_name)
                self.qsub_cmd += 'cd ' + self.outdir + ' && fastqc -t 12 -o ' + self.outdir + ' ' + self.config.sample[s]['single'] + ' && mv ' + fq_name + '_fastqc ' + s + '_fastqc && rm -rf ' + fq_name + '_fastqc.zip && '
                self.qsub_cmd += '\n'

    def make_pre_cmd(self):
        pass

    def make_post_cmd(self):
        self.post_cmd += 'cd ' + self.outdir + ' && perl ' + self.config.gc['src'] + '/Basic/FastQc/fastqc_stat.pl'
        self.post_cmd += '\n'



class Mapping_Tophat2(Module):
    """tophat2"""

    def init_input(self):
        self.input_ids["INT"].append("threads")
        self.inputs["threads"] = 16
        self.input_ids["INT"].append("readmis")
        self.inputs["readmis"] = 4
        self.input_ids["INT"].append("b2mis")
        self.inputs["b2mis"] = 1
        self.input_ids["STR"].append("other_argv")
        self.inputs["other_argv"] = ''

    def init_output(self):
        self.output_ids["DICT"].append('uniqbam')
        self.outputs['uniqbam'] = {}
        self.output_ids["DICT"].append('mapresult')
        self.outputs['mapresult'] = {}
        self.output_ids["DICT"].append('junctionbed')
        self.outputs['junctionbed'] = {}
        for s in self.config.sample:
            self.outputs['uniqbam'][s] = self.outdir + '/' + s + '_mapping/accepted_hits.uniq.bam'
            self.outputs['mapresult'][s] = self.outdir + '/' + s + '_mapping/map_result.txt'
            self.outputs['junctionbed'][s] = self.outdir + '/' + s + '_mapping/junctions.bed'

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            if self.config.sample[s]['pe'] == "single":
                self.qsub_cmd += 'mkdir -p ' + self.outdir + "/" + s + "_mapping &&"
                self.qsub_cmd += tophat2(self.config, s, self.outdir, self.config.sample[s]['end1'], readmis=self.inputs["readmis"], b2mis=self.inputs["b2mis"], other_argv=self.inputs["other_argv"], cpu=self.inputs["threads"])
                self.qsub_cmd += ' &&\n\n'

    def make_post_cmd(self):
        for s in self.config.sample:
            tmp = os.popen('cd ' + self.outdir + '/' + s + '_mapping && cat _splice_reads_number').readlines()
            splice_reads_num = int(tmp[0].strip())
            uniq_map = 0
            mapresult = ""
            for line in open(self.outdir + '/' + s + '_mapping/map_result.txt'):
                line = line.strip()
                if not line.startswith("Splice reads:") and not line.startswith("Nonsplice reads:"):
                    mapresult += line + "\n"
                if not line.startswith('Total Uniquely mapped'):
                    continue
                match = re.search(r'Total Uniquely mapped:(\d+)', line)
                #match = re.search(r'uniq mapped reads:(\d+)', line)
                if not match:
                    continue
                uniq_map = int(match.group(1))
            nonsplice_reads_num = uniq_map - splice_reads_num
            splice_reads_percent = round(100 * float(splice_reads_num) / uniq_map, 2)
            nonsplice_reads_percent = round(100 * float(nonsplice_reads_num) / uniq_map, 2)
            splice_result = "Splice reads:" + str(splice_reads_num) + "(" + str(splice_reads_percent) + "%)" + "\n"
            nonsplice_result = "Nonsplice reads:" + str(nonsplice_reads_num) + "(" + str(nonsplice_reads_percent) + "%)" + "\n"
            with open(self.outdir + '/' + s + '_mapping/map_result.txt', 'w') as o:
                o.writelines(mapresult)
                o.writelines(splice_result)
                o.writelines(nonsplice_result)

        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/public/pipeline_stat.pl -i ./ -p _mapping -m map_result.txt -o _Mapping_of_clean_reads_on_the_reference_genome.txt && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/public/transpose_tab_file.pl _Mapping_of_clean_reads_on_the_reference_genome.txt > Mapping_of_clean_reads_on_the_reference_genome.txt && rm -rf _Mapping_of_clean_reads_on_the_reference_genome.txt'
        self.post_cmd += '\n'



class Bam2bed(Module):
    """bam2bed"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam')
        # self.input_ids["STR"].append("use_rmdup_bam")

    def init_output(self):
        self.output_ids["DICT"].append('rmdup_uniq_bam')
        self.outputs['rmdup_uniq_bam'] = {}
        self.output_ids["DICT"].append('rmdup_uniq_bed')
        self.outputs['rmdup_uniq_bed'] = {}
        for s in self.config.sample:
            self.outputs['rmdup_uniq_bam'][s] = self.outdir + '/' + s + '_mapping/accepted_hits.uniq.rmdup.bam'
            self.outputs['rmdup_uniq_bed'][s] = self.outdir + '/' + s + '_mapping/accepted_hits.uniq.rmdup.bed'

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            if self.config.sample[s]['pe'] == "single":
                self.qsub_cmd += bam2bed(s, self.outdir, uniqbam=self.inputs["uniqbam"][s])
                self.qsub_cmd += ' &&\n\n'

    def make_post_cmd(self):
        for s in self.config.sample:
            rmdup_bam = self.outdir + '/' + s + '_mapping/accepted_hits.uniq.rmdup.bam'
            rmdup_reads = getBamReadsNumber(rmdup_bam)
            uniq_map = -1
            mapresult = ""
            for line in open(self.outdir + '/' + s + '_mapping/map_result.txt'):
                line = line.strip()
                if not line.startswith("rmdup reads:"):
                    mapresult += line + "\n"
                if not line.startswith('Total Uniquely mapped:'):
                    continue
                match = re.search(r'Total Uniquely mapped:(\d+)', line)
                if not match:
                    continue
                uniq_map = int(match.group(1))

            rmdup_reads_percent = round(100 * float(rmdup_reads) / uniq_map, 2)
            rmdup_result = "rmdup reads:" + str(rmdup_reads) + "(" + str(rmdup_reads_percent) + "%)" + "\n"
            with open(self.outdir + '/' + s + '_mapping/map_result.txt', 'w') as o:
                o.writelines(mapresult)
                o.writelines(rmdup_result)
            self.post_cmd += '\n'
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/public/pipeline_stat.pl -i ./ -p _mapping -m map_result.txt -o _Mapping_of_clean_reads_on_the_reference_genome.txt && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/public/transpose_tab_file.pl _Mapping_of_clean_reads_on_the_reference_genome.txt > Mapping_of_clean_reads_on_the_reference_genome.txt && rm -rf _Mapping_of_clean_reads_on_the_reference_genome.txt'
        self.post_cmd += '\n'

class EXP(Module):
    """expression"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam')

    def init_output(self):
        self.output_ids["FILE"].append('exp_reads')
        self.outputs['exp_reads'] = self.outdir + '/expressed_gene_reads.txt'
        self.output_ids["FILE"].append('exp')
        self.outputs['exp'] = self.outdir + '/expressed_gene_RPKM.txt'
        self.output_ids["FILE"].append('raw_exp_reads')
        self.outputs['raw_exp_reads'] = self.outdir + '/expressed_gene_reads.txt.tmp'
        self.output_ids["FILE"].append('raw_exp')
        self.outputs['raw_exp'] = self.outdir + '/expressed_gene_RPKM.txt.tmp'
        self.output_ids["DICT"].append('sample_exp')
        self.outputs['sample_exp'] = {}
        self.output_ids["DICT"].append('rpkm_cumu')
        self.outputs['rpkm_cumu'] = {}
        for s in self.config.sample:
            self.outputs['sample_exp'][s] = self.outdir + '/' + s + '_basic/' + s + '_expression_profile.txt'
            self.outputs['rpkm_cumu'][s] = self.outdir + '/' + s + '_basic/' + s + '_RPKM_Cumulative.txt'

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            if self.config.sample[s]['pe'] == "single":
                self.qsub_cmd += 'cd ' + self.outdir + ' && '
                if self.config.sample[s]['library-type'] == "unstrand":
                    self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                    self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/expression_quantity_calculation_v2.2.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' -u && '
                else:
                    self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                    self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/expression_quantity_calculation_v2.2.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
                mydir = s + '_basic'
                self.qsub_cmd += 'cd ' + mydir + ' && '
                self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
                self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/get_Cumulative_Data_From_File.py -k RPKM -i ' + s + "_expression_profile.txt -n 10 " + " -o " + s + "_RPKM_Cumulative.txt && "
                self.qsub_cmd += 'Rscript ' + self.config.gc["src"] + '/plot/Line_single_Cumulative_ggplot2.r -f ' + s + "_RPKM_Cumulative.txt -t " + s + "_RPKM -n " + s + "_RPKM -o ./ &&"
                self.qsub_cmd += '\n'

            elif self.config.sample[s]['pe'] == "pairend":
                self.qsub_cmd += 'cd ' + self.outdir + ' && '
                if self.config.sample[s]['library-type'] == "unstrand":
                    self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                    self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/expression_quantity_calculation_v2.2.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' -u && '
                else:
                    self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                    self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/expression_quantity_calculation_v2.2.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
                mydir = s + '_basic'
                self.qsub_cmd += 'cd ' + mydir + ' && '
                self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
                self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/get_Cumulative_Data_From_File.py -k RPKM -i ' + s + "_expression_profile.txt -n 10 " + " -o " + s + "_RPKM_Cumulative.txt && "
                self.qsub_cmd += 'Rscript ' + self.config.gc["src"] + '/plot/Line_single_Cumulative_ggplot2.r -f ' + s + "_RPKM_Cumulative.txt -t " + s + "_RPKM -n " + s + "_RPKM -o ./ &&"
                self.qsub_cmd += '\n'

    def make_post_cmd(self):
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/pipeline_stat_exp.pl -i ./ -p _basic -m _expression_profile.txt -c 10 -o expressed_gene_RPKM.txt.tmp && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/exp_add_anno.pl -exp expressed_gene_RPKM.txt.tmp -anno ' + self.config.gc["geneanno"] + ' -o expressed_gene_RPKM.txt'
        self.post_cmd += '\n'
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/pipeline_stat_exp.pl -i ./ -p _basic -m _expression_profile.txt -c 12 -o expressed_gene_reads.txt.tmp && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/exp_add_anno.pl -exp expressed_gene_reads.txt.tmp -anno ' + self.config.gc["geneanno"] + ' -o expressed_gene_reads.txt'
        self.post_cmd += '\n'
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/public/stat_gene_exp_for_deg.pl -exp expressed_gene_RPKM.txt.tmp -t ' + str(self.config.gc["genenumber"]) + ' -o Mapped_normalized_reads_on_expressed_genes_in_reference_genome.txt'
        self.post_cmd += '\n'


class MapRegion(Module):
    """map region"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam')
        self.input_ids["DICT"].append('mapresult')
        self.inputs['mapresult'] = {}

    def init_output(self):
        self.output_ids["FILE"].append('exp')
        self.outputs['exp'] = ''

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            if self.config.sample[s]['library-type'] == "unstrand":
                self.qsub_cmd += 'cd ' + self.outdir + ' && '
                self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/mapping_distribution_analyse.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' -u && '
                self.qsub_cmd += '\n'
            else:
                self.qsub_cmd += 'cd ' + self.outdir + ' && '
                self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
                self.qsub_cmd += 'python ' + self.config.gc['src'] + '/public/mapping_distribution_analyse.py -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
                self.qsub_cmd += '\n'

    def make_post_cmd(self):
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc['src'] + '/Basic/MapRegion/pipeline_mapregion_result_stat.pl -i ./ -p _basic -o Reads_distribution_across_reference_Genomic_Regions.txt'
        self.post_cmd += '\n'

        for s in self.config.sample:
            if s not in self.inputs['mapresult']:
                continue
            if self.config.sample[s]['library-type'] == "strand":
                uniq_map = 0
                mapresult = ""
                for line in open(self.inputs['mapresult'][s]):
                    line = line.strip()
                    if not line.startswith('Sense reads:') and not line.startswith('Antisense reads:'):
                        mapresult += line + '\n'
                    if not line.startswith('Total Uniquely mapped:'):
                        continue
                    match = re.search(r'Total Uniquely mapped:(\d+)', line)
                    if not match:
                        continue
                    uniq_map = int(match.group(1))

                antisense_reads = 0
                for line in open(self.outdir + '/' + s + '_basic/' + s + '_Mapping_distribution.txt'):
                    line = line.strip()
                    if not line.startswith('antisense'):
                        continue
                    match = re.search(r'antisense\s*(\d+)', line)
                    if not match:
                        continue
                    antisense_reads = int(match.group(1))
                sense_reads = uniq_map - antisense_reads
                sense_reads_percent = round(100 * float(sense_reads) / uniq_map, 2)
                antisense_reads_percent = round(100 * float(antisense_reads) / uniq_map, 2)
                sense_result = "Sense reads:" + str(sense_reads) + "(" + str(sense_reads_percent) + "%)" + "\n"
                antisense_result = "Antisense reads:" + str(antisense_reads) + "(" + str(antisense_reads_percent) + "%)" + "\n"
                with open(self.outdir + '/' + s + '_basic/map_result.txt', 'w') as o:
                    o.writelines(mapresult)
                    o.writelines(sense_result)
                    o.writelines(antisense_result)
        self.post_cmd += 'cd ' + self.outdir + ' && '
        self.post_cmd += 'perl ' + self.config.gc["src"] + '/public/pipeline_stat.pl -i ./ -p _basic -m map_result.txt -o Mapping_of_clean_reads_on_the_reference_genome.txt'
        self.post_cmd += '\n'


class Distance2XXX(Module):
    """distance to tss tts"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam')

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            self.qsub_cmd += 'cd ' + self.outdir + ' && '
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
            self.qsub_cmd += 'python ' + self.config.gc['src'] + '/Basic/Distance2XXX/reads_or_peaks_distribution_relative2xxx.py -p tss -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
            self.qsub_cmd += '\n'
            self.qsub_cmd += 'cd ' + self.outdir + ' && '
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
            self.qsub_cmd += 'python ' + self.config.gc['src'] + '/Basic/Distance2XXX/reads_or_peaks_distribution_relative2xxx.py -p tts -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
            self.qsub_cmd += '\n'
            self.qsub_cmd += 'cd ' + self.outdir + ' && '
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
            self.qsub_cmd += 'python ' + self.config.gc['src'] + '/Basic/Distance2XXX/reads_or_peaks_distribution_relative2xxx.py -p startcodon -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
            self.qsub_cmd += '\n'
            self.qsub_cmd += 'cd ' + self.outdir + ' && '
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py2/bin/activate && "
            self.qsub_cmd += 'python ' + self.config.gc['src'] + '/Basic/Distance2XXX/reads_or_peaks_distribution_relative2xxx.py -p stopcodon -d ' + self.config.gc["gffdb"] + ' -b ' + self.inputs['uniqbam'][s] + ' -O ' + s + '_basic -n ' + s + ' && '
            self.qsub_cmd += '\n'

    def make_post_cmd(self):
        for s in self.config.sample:
            mydir = self.outdir + "/" + s + "_basic"
            self.post_cmd += 'cd ' + mydir + ' && '
            self.post_cmd += 'Rscript ' + self.config.gc["src"] + '/plot/Line_multiSample_multiText.r -f ' + s + '_distance2startcodon_reads_density.txt,' + s + '_distance2stopcodon_reads_density.txt -s startcondon,stopcodon -t ' + s + '_distance2xxx_reads_density_codon &'
            self.post_cmd += '\n'
            self.post_cmd += 'cd ' + mydir + ' && '
            self.post_cmd += 'Rscript ' + self.config.gc["src"] + '/plot/Line_multiSample_multiText.r -f ' + s + '_distance2tss_reads_density.txt,' + s + '_distance2tts_reads_density.txt -s tss,tts -t ' + s + '_distance2xxx_reads_density_tss_tts &'
            self.post_cmd += '\n'
        self.post_cmd += 'wait'
        self.post_cmd += '\n'


class Genome_coverage(Module):
    """Genome coverage"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam_stat')
        self.inputs["uniqbam_stat"] = {}

    def init_output(self):
        self.output_ids["FILE"].append('genome_coverage')
        self.outputs['genome_coverage'] = self.outdir + '/Genome_coverage.xls'

    def make_pre_cmd(self):
        genome_size = 0
        for eachLine in open(self.config.gc["chrlen"]):
            line = eachLine.strip().split("\t")
            genome_size += int(line[1])
        reads = {}
        bases = {}
        avglen = {}
        for s in self.config.sample:
            for eachLine in open(self.inputs["uniqbam_stat"][s]):
                line = eachLine.strip().split("\t")
                if len(line)<3:
                    continue
                if line[1] == "bases mapped:":
                    bases[s] = line[2]
                elif line[1] == "average length:":
                    avglen[s] = line[2]
                elif line[1] == "reads mapped:":
                    reads[s] = line[2]
        with open(self.outdir + '/Genome_coverage.xls', 'w') as o:
            o.writelines("Sample\tReads Mapped\tBases Mapped\tReads Average Length\tCoverage\n")
            for s in sorted(self.config.sample.keys()):
                cov = round(int(bases[s]) / genome_size, 2)
                o.writelines(s + "\t" + reads[s] + "\t" + bases[s] + "\t" + avglen[s] + "\t" + str(cov) + "\n")
            o.writelines("###Genome Size : " + str(genome_size) + "\n")


class PlotGenome(Module):
    """plot genome circos"""

    def init_input(self):
        self.input_ids["DICT"].append('uniqbam')
        self.input_ids["INT"].append('chromosome-minlength')
        self.inputs['chromosome-minlength'] = 1000000

    def init_output(self):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            self.qsub_cmd += 'cd ' + self.outdir + ' && '
            self.qsub_cmd += "samtools depth " + self.inputs['uniqbam'][s] + "|perl -ne 'BEGIN{%sum=();$totalchrlen=0;%chrlen=();open IN,\"" + self.config.gc["chrlen"] + "\";while(<IN>){chomp;@line=split;$chrlen{$line[0]}=$line[1];$totalchrlen+=$line[1];}$cunit=int($totalchrlen/100000+1)}chomp;@line=split;$i=int($line[1]/$cunit);$sum{$line[0]}{$i}+=$line[2];END{foreach $chr(sort keys %sum){next if not defined($chrlen{$chr});$i=int($chrlen{$chr}/$cunit)+1;for(my $j=0;$j<$i;$j++){$end=$j*$cunit+$cunit-1;if($j==$i-1){$end=$chrlen{$chr};}print $chr,\"\\t\",$j*$cunit,\"\\t\",$end,\"\\t\",log($sum{$chr}{$j}/$cunit+1),\"\\n\";}}}' > " + s + "_coverage.txt &&"
            self.qsub_cmd += '\n'

    def make_post_cmd(self):
        for key in self.inputs:
            if key.startswith("plotgroup"):
                samples = self.inputs[key].split(",")
                self.post_cmd += 'mkdir -p ' + self.outdir + '/' + key + ' && '
                self.post_cmd += 'cd ' + self.outdir + '/' + key + ' && '
                coverage_list = []
                name_list = []
                for s in samples:
                    coverage_list.append(self.outdir + "/" + s + "_coverage.txt")
                    name_list.append(s)
                coverages = ','.join(coverage_list)
                names = ','.join(name_list)
                self.post_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
                self.post_cmd += 'python ' + self.config.gc['src'] + '/public/circos_plot.py -c ' + coverages + ' -n ' + names + ' -l ' + self.config.gc["chrlen"] + ' -g ' + self.config.gc["gff"] + ' -m ' + str(self.inputs['chromosome-minlength']) + ' -o ' + key + '_reads_density_of_whole_genome_circos.png &'
                self.post_cmd += '\n'
        self.post_cmd += 'wait\n'


class ConfigTemplate(Module):
    def init_input(self):
        self.input_ids["DICT"].append('pipedict')
        self.inputs["pipedict"] = {}
        self.inputs["pipedict"]["rnaseq"] = self.config.gc["src"] + "/Pipeline_configs/RNA-seq/rnaseq.config.sample"
        self.input_ids["STR"].append('pipe')
        self.inputs["pipe"] = "rnaseq"
        self.input_ids["FILE"].append('config')


# class MakeConfigTemplate(ConfigTemplate):

#     rnaseq，chipseq，clipseq，as，lncrna，mirnaseq，cage, pas, bsseq
#     """
#
#     def init_input(self):
#         super().init_input()
#         self.input_ids["STR"].append('pipe')
#         self.inputs["pipe"] = "rnaseq"
#
#     def init_output(self):
#         pass
#
#     def make_pre_cmd(self):
#         outfile = self.inputs["pipe"] + ".config"
#         self.pre_cmd += "cd " + self.outdir + "/../../ && "
#         self.pre_cmd += cpfile(self.inputs["pipedict"][self.inputs["pipe"]], targetfile=outfile, deli="")
#         self.pre_cmd += "\n"


class CheckConfig(ConfigTemplate):
    """
    """

    # def init_input(self):
    #     super()
    #     self.input_ids["STR"].append('pipe')
    #     self.inputs["pipe"] = "rnaseq"
    #     self.input_ids["FILE"].append('config')

    def init_output(self):
        pass

    def make_pre_cmd(self):
        thisconfig_version = check_config_version(self.inputs["config"])
        if self.inputs["pipe"] not in self.inputs["pipedict"]:
            print(Fore.RED + Style.DIM + "your config type is not supported" + Style.RESET_ALL)
            print(Fore.RED + Style.DIM + "your config file version is : " + thisconfig_version + Style.RESET_ALL)
            return
        latestconfig_version = check_config_version(self.inputs["pipedict"][self.inputs["pipe"]])
        if thisconfig_version == latestconfig_version:
            print(Fore.RED + Style.DIM + "your config file is latest: " + latestconfig_version + Style.RESET_ALL)
        else:
            print(Fore.RED + Style.DIM + "your config file version is : " + thisconfig_version + Style.RESET_ALL)
            print(Fore.RED + Style.DIM + "latest config file version is : " + latestconfig_version + Style.RESET_ALL)

# # -----------------------------------------------------------------------------------
# ### E
# # -----------------------------------------------------------------------------------
