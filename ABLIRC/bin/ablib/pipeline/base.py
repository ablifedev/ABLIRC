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
public functions
"""

### Import
import ast
import os
import sys
import traceback

import configparser
from colorama import init, Fore, Style

init(autoreset=True)
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../../")
from ablib.utils.tools import *

### Version
_version = 'v1.0'
print("base")


# -----------------------------------------------------------------------------------
### S Class definitions
# ------------------------------------------------------------------------------------

class Module:
    """parent class of modules"""

    def __init__(self, config=None, module_argv=None):
        self.qsub_cmd = ""
        self.qsub_cmd2 = ""
        self.pre_cmd = ""
        self.pre_cmd2 = ""
        self.post_cmd = ""
        self.post_cmd2 = ""
        self.id = ""
        self.module_name = ""
        self.outdir = ""
        self.inputs = {}
        self.input_ids = {"FLOAT": [], "INT": [], "BOOL": [], "STR": [], "FILE": [], "PATH": [], "LIST": [], "DICT": [], "SAMPLE": []}
        self.outputs = {}
        self.output_ids = {"FLOAT": [], "INT": [], "BOOL": [], "STR": [], "FILE": [], "PATH": [], "LIST": [], "DICT": [], "SAMPLE": []}

        if config is not None:
            self.config = config
            self.module_name = module_argv['name']
            self.id = module_argv['id']
            idstr = self.id.split("__")
            self.outdir = os.path.abspath(self.config.gc["outdir"] + '/result/' + idstr[0])
            os.system('mkdir -p ' + self.outdir)
            self.init_input()
            self.__parseIO(config, module_argv)
            self.init_output()
            # print(self.inputs)
            # print(self.outputs)
            # self.config.module[self.id] = module_argv
            # self.update_config(self.config)

        else:
            # self.config = self.parseConfig()
            from ablib.pipeline import pipeline_main
            self.config = pipeline_main.Config()


    def _nextvalue(self, list, value):
        index = list.index(value)
        return list[index + 1]

    def parseArgv(self, tool_argv):
        pass

    def check_config(self):
        return False

    def init_input(self):
        """
        init input
        :return: input_ids,inputs
        """
        pass

    def init_output(self):
        """
        init output
        :return: output_ids,outputs
        """
        pass

    def __parseIO(self, config=None, module_argv=None):
        """
        parseIO
        :return:
        """
        for option in module_argv:
            # print(option)
            if module_argv[option] is None:
                continue
            if option.startswith("output:") or option.startswith("o:") or option.startswith("out:"):
                outputkey = re.sub(r'^\w+\:', '', option)
                if module_argv[option].startswith("target|sample:"):
                    # print(module_argv[option])
                    match = re.search(r'^target\|sample:([\w\-]+)', module_argv[option])
                    if not match:
                        continue
                    skey = match.group(1)
                    # print(skey)
                    self.outputs[outputkey] = skey
                continue
            inputkey = option
            if option.startswith("input:") or option.startswith("i:") or option.startswith("in:"):
                inputkey = re.sub(r'^\w+\:', '', option)
            if module_argv[option].startswith("source|sample:"):
                match = re.search(r'^source\|sample:([\w\-]+)', module_argv[option])
                if not match:
                    continue
                skey = match.group(1)
                self.inputs[inputkey] = skey
            elif module_argv[option].startswith("source|gc:"):
                match = re.search(r'^source\|gc:([\w\-]+)', module_argv[option])
                if not match:
                    continue
                skey = match.group(1)
                self.inputs[inputkey] = self.config.gc[skey]
            elif module_argv[option].startswith("source|"):
                match = re.search(r'^source\|([\w\-]+):([\w\-]+)', module_argv[option])
                if not match:
                    continue
                mid = match.group(1)
                mkey = match.group(2)
                try:
                    self.inputs[inputkey] = config.module[mid]["outputs"][mkey]
                except:
                    if mid not in config.module:
                        logging.error(mid + " module is not in pipeline for " + self.module_name)
                    elif mkey not in config.module[mid]["outputs"]:
                        logging.error(mkey + " is not in pipeline")
            elif option in self.input_ids["FLOAT"]:
                self.inputs[inputkey] = float(module_argv[option])
            elif option in self.input_ids["INT"]:
                self.inputs[inputkey] = int(module_argv[option])
            elif option in self.input_ids["BOOL"]:
                self.inputs[inputkey] = to_bool(module_argv[option])
            elif option in self.input_ids["STR"] or option in self.input_ids["FILE"] or option in self.input_ids["PATH"]:
                self.inputs[inputkey] = module_argv[option]
            elif option in self.input_ids["LIST"]:
                self.inputs[inputkey] = ast.literal_eval(module_argv[option])
            elif option in self.input_ids["DICT"]:
                self.inputs[inputkey] = ast.literal_eval(module_argv[option])
            else:
                self.inputs[inputkey] = module_argv[option]
                # print(module_argv)
                # print(self.inputs)

    def make_qsub_cmd(self):
        pass

    def make_qsub_cmd2(self):
        pass

    def make_pre_cmd(self):
        pass

    def make_pre_cmd2(self):
        pass

    def make_post_cmd(self):
        pass

    def make_post_cmd2(self):
        pass

    def update_config(self, config):
        config.module[self.id] = {}
        config.module[self.id]["inputs"] = self.inputs
        config.module[self.id]["outputs"] = self.outputs
        self.update_sample(config)

    def update_sample(self, config):
        pass

    def run(self):
        """run module"""

        if self.__check_finish():
            return None

        if self.check_config():
            return None

        logging.info(Fore.YELLOW + Style.NORMAL + "[" + self.id + "] begin" + Style.RESET_ALL)

        ## run post cmd only
        if not self.config.gc["run-post-only"]:
            try:
                self.make_pre_cmd()
            except:
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make pre cmd " + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: \n" + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
                return "error"
            if self.pre_cmd != "":
                sh_file = self.config.gc["outdir"] + '/' + self.id + '_pre.sh'
                sh = open(sh_file, 'w')
                sh.writelines(self.pre_cmd)
                sh.close()
                cmd = 'sh ' + sh_file
                # logging.debug("\n\n[" + self.id + "] pre cmd: \n" + self.pre_cmd)
                if not to_bool(self.config.gc["make-cmd-only"]):
                    status, output = subprocess.getstatusoutput(cmd)
                    if (int(status) != 0):  # it did not go well
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] pre cmd error in running %s" % status + Style.RESET_ALL)
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: %s" % output + Style.RESET_ALL)
                        return "error"
                    else:
                        logging.debug("[" + self.id + "] pre cmd running info:\n%s" % output)
            else:
                logging.info(Fore.GREEN + Style.DIM + "[" + self.id + "]  has no pre cmd." + Style.RESET_ALL)

            try:
                self.make_pre_cmd2()
            except:
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make pre cmd 2 " + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: \n" + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
                return "error"
            if self.pre_cmd2 != "":
                sh_file = self.config.gc["outdir"] + '/' + self.id + '_pre2.sh'
                sh = open(sh_file, 'w')
                sh.writelines(self.pre_cmd2)
                sh.close()
                cmd = 'sh ' + sh_file
                # logging.debug("\n\n[" + self.id + "] pre cmd 2: \n" + self.pre_cmd2)
                if not to_bool(self.config.gc["make-cmd-only"]):
                    status, output = subprocess.getstatusoutput(cmd)
                    if (int(status) != 0):  # it did not go well
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] pre cmd 2 error in running %s" % status + Style.RESET_ALL)
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] pre cmd 2 error detail: %s" % output + Style.RESET_ALL)
                        return "error"
                    else:
                        logging.debug("[" + self.id + "] pre cmd 2 running info:\n%s" % output)

            # if self.qsub_cmd != "" and not self.config.module[self.module_name]['only_run_callback']:
            try:
                queuename = self.make_qsub_cmd()
            except:
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make qsub cmd " + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail:" + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
                return "error"
            if queuename is None:
                queuename = self.config.gc["sgequeue"]
            if self.qsub_cmd != "":
                # logging.debug("\n\n[" + self.id + "] qsub cmd: \n" + self.qsub_cmd)

                sh_file = self.config.gc["outdir"] + '/' + self.id + '_qsub.sh'
                sh = open(sh_file, 'w')
                sh.writelines(self.qsub_cmd)
                sh.close()

                cmd = 'perl ' + self.config.gc["src"] + '/public/qsub-sge.pl --usesge '+self.config.gc["usesge"]+' --queue ' + queuename + ' --reqsub --maxproc '+self.config.gc["cpu"]+' ' + sh_file

                if not to_bool(self.config.gc["make-cmd-only"]):
                    status, output = subprocess.getstatusoutput(cmd)
                    if (int(status) != 0):  # it did not go well
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] qsub cmd error in running %s" % status + Style.RESET_ALL)
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: %s" % output + Style.RESET_ALL)
                        return "error"
            else:
                logging.info(Fore.GREEN + Style.DIM + "[" + self.id + "]  has no qsub cmd." + Style.RESET_ALL)

            try:
                queuename2 = self.make_qsub_cmd2()
            except:
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make qsub2 cmd " + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail:" + Style.RESET_ALL)
                logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
                return "error"
            if queuename2 is None:
                queuename2 = self.config.gc["sgequeue"]
            if self.qsub_cmd2 != "":
                # logging.debug("\n\n[" + self.id + "] qsub2 cmd: \n" + self.qsub_cmd2)

                sh_file = self.config.gc["outdir"] + '/' + self.id + '_qsub2.sh'
                sh = open(sh_file, 'w')
                sh.writelines(self.qsub_cmd2)
                sh.close()

                cmd = 'perl ' + self.config.gc["src"] + '/public/qsub-sge.pl --usesge '+self.config.gc["usesge"]+' --queue ' + queuename + ' --reqsub --maxproc '+self.config.gc["cpu"]+' ' + sh_file

                if not to_bool(self.config.gc["make-cmd-only"]):
                    status, output = subprocess.getstatusoutput(cmd)
                    if (int(status) != 0):  # it did not go well
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] qsub2 cmd error in running %s" % status + Style.RESET_ALL)
                        logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: %s" % output + Style.RESET_ALL)
                        return "error"
            else:
                logging.info(Fore.GREEN + Style.DIM + "[" + self.id + "]  has no qsub2 cmd." + Style.RESET_ALL)

        try:
            self.make_post_cmd()

        except:
            logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make post cmd " + Style.RESET_ALL)
            logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: \n" + Style.RESET_ALL)
            logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
            return "error"
        if self.post_cmd != "":
            sh_file = self.config.gc["outdir"] + '/' + self.id + '_post.sh'
            sh = open(sh_file, 'w')
            sh.writelines(self.post_cmd)
            sh.close()
            cmd = 'sh ' + sh_file
            # logging.debug("\n\n[" + self.id + "] post cmd: \n" + self.post_cmd)

            if not to_bool(self.config.gc["make-cmd-only"]):
                status, output = subprocess.getstatusoutput(cmd)
                if (int(status) != 0):  # it did not go well
                    logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] post cmd error in running %s" % status + Style.RESET_ALL)
                    logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] post cmd error detail: %s" % output + Style.RESET_ALL)
                    return "error"
                else:
                    logging.debug("[" + self.id + "] post cmd running info:\n%s" % output)
        else:
            logging.info(Fore.GREEN + Style.DIM + "[" + self.id + "]  has no post cmd.")

        try:
            self.make_post_cmd2()
        except:
            logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] failed when make post cmd 2 " + Style.RESET_ALL)
            logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] error detail: \n" + Style.RESET_ALL)
            logging.error(Fore.RED + Style.BRIGHT + traceback.format_exc() + Style.RESET_ALL)
            return "error"
        if self.post_cmd2 != "":
            sh_file = self.config.gc["outdir"] + '/' + self.id + '_post2.sh'
            sh = open(sh_file, 'w')
            sh.writelines(self.post_cmd2)
            sh.close()
            cmd = 'sh ' + sh_file
            # logging.debug("\n\n[" + self.id + "] post cmd 2: \n" + self.post_cmd2)

            if not to_bool(self.config.gc["make-cmd-only"]):
                status, output = subprocess.getstatusoutput(cmd)
                if (int(status) != 0):  # it did not go well
                    logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] post cmd 2 error in running %s" % status + Style.RESET_ALL)
                    logging.error(Fore.RED + Style.BRIGHT + "[" + self.id + "] post cmd 2 error detail: %s" % output + Style.RESET_ALL)
                    return "error"
                else:
                    logging.debug("[" + self.id + "] post cmd 2 running info:\n%s" % output)
        else:
            logging.info(Fore.GREEN + Style.BRIGHT + "[" + self.id + "] finished" + Style.RESET_ALL)

    def __check_finish(self):
        if self.id in dict(self.config.finish):
            logging.info(Fore.GREEN + Style.DIM + "[" + self.module_name + ":" + self.id + "] seems to have been finished, so skip" + Style.RESET_ALL)
            return True
        else:
            return False

    def print_help(self, src):
        print("-genomeid\tgenome id\n")
        print("-sample[1,2,3,4...]\tsample  [sampleid:end1:end2]\n")
        print("-list[1,2,3,4...]\t      [sample1,sample2:listname]\n")
        self.config.gc["src"] = src
        self.init_input()
        self.init_output()
        for type in self.input_ids:
            for input_id in self.input_ids[type]:
                print("-" + input_id + "\t" + type + "\n")
        for type in self.output_ids:
            for output_id in self.output_ids[type]:
                print("output:" + output_id + "\t" + type + "\t" + str(self.outputs[output_id]) + "\n")


class Report(Module):
    """parent class of report module"""

    def init_input(self):
        self.input_ids["FILE"].append("template")
        self.input_ids["FILE"].append("clean_info")
        self.input_ids["FILE"].append("sample_info")

    def make_pre_cmd(self):
        os.system('cd ' + self.outdir + ' && rm -rf * ')

        self.pre_cmd += 'cd ' + self.outdir
        self.pre_cmd += '\n'
        for key in sorted(self.inputs):
            if key.startswith("sup"):
                sup_name = self.inputs[key]
                sup_dir = self.outdir + '/Supplements/' + key.capitalize() + '_' + sup_name
                self.pre_cmd += 'mkdir -p ' + sup_dir
                self.pre_cmd += '\n'

    def make_qsub_cmd(self):
        pass

    def make_post_cmd(self):
        self.post_cmd += report_parse(self.config, self.outdir, self.inputs['template'])


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------



# -----------------------------------------------------------------------------------
### S tool functions
# -----------------------------------------------------------------------------------

def tophat2(config, s, outdir, end1, readmis=2, b2mis=0, other_argv='', cpu=16):
    cmd = ""
    cmd += 'cd ' + outdir + ' && '
    cmd += 'tophat2 -p ' + str(cpu) + ' -o ' + s + "_mapping" + ' -G ' + config.gc["gff"] + ' --read-edit-dist ' + str(readmis) + ' -N ' + str(readmis) + ' --b2-N ' + str(b2mis) + ' ' + other_argv + ' ' + config.gc["bowtie2_index"] + ' ' + end1 + ' && '
    cmd += 'cd ' + s + "_mapping" + ' && '
    cmd += """samtools view -h accepted_hits.bam | awk -F"\\t" '$1 ~ "^@" || $NF ~ "NH:i:1$"' | samtools view -b -o accepted_hits.uniq.bam - && samtools index accepted_hits.uniq.bam && """
    cmd += """samtools view accepted_hits.uniq.bam | awk '$6~/[0-9]+M[0-9]+N[0-9]+M/' | wc -l > _splice_reads_number && """
    cmd += "source " + config.gc['src'] + "/../venv/venv-py3/bin/activate && "
    cmd += "python " + config.gc['src'] + "/public/read_Tophat_mapresult.py -o map_result.txt && "
    cmd += "samtools stats accepted_hits.uniq.bam > uniqbam_stat.txt"
    return cmd


def bam2bed(s, outdir, uniqbam):
    cmd = ""
    cmd += 'cd ' + outdir + '/' + s + '_mapping && '
    cmd += """ samtools view -h accepted_hits.uniq.bam|perl -ne 'chomp;if(/^@/){print $_,"\\n";next;}$I_sum=0;$D_sum=0;$M_sum=0;$N_sum=0;@I_num=();@D_num=();@M_num=();@N_num=();@line=split/\\t/,$_;@I_num = ($line[5]=~ /(\d+)I/g);@D_num = ($line[5] =~ /(\d+)D/g);@M_num = ($line[5] =~ /(\d+)M/g);@N_num = ($line[5] =~ /(\d+)N/g);$I_sum += $_ for @I_num;$D_sum += $_ for @D_num;$M_sum += $_ for @M_num;$N_sum += $_ for @N_num;$length = $D_sum + $M_sum + $N_num;$end=$line[3]+$length-1;$tag="$line[2]"."_"."$line[1]"."_"."$line[3]"."_"."$end";if(defined $e{$tag}){next}else{print "$_\\n"}$e{$tag}=1' | samtools-latest view -b -o accepted_hits.uniq.rmdup.bam - && samtools-latest index accepted_hits.uniq.rmdup.bam &&"""
    cmd += 'bedtools bamtobed -split -i accepted_hits.uniq.rmdup.bam > accepted_hits.uniq.rmdup.bed '
    return cmd


def callmotif(config, outdir, peakfa, type="clip"):
    cmd = ""

    if type == "clip":
        cmd += 'mkdir -p ' + outdir + ' && cd ' + outdir + ' && '
        cmd += 'perl ' + config.gc["src"] + '/public/pick_gene_fa.pl -w ' + config.gc["genome"] + ' -g ' + config.gc["gff"] + ' && '
        cmd += 'perl ' + config.gc["src"] + '/public/random_gene_fa.pl -w gene.fa -t ' + peakfa + ' -o bg_peak.fa && rm -rf gene.fa && '
        cmd += 'findMotifs.pl ' + peakfa + ' fasta ./ -fasta bg_peak.fa -rna -len 5,6,7,8,9,10,11,12 -p 24 > motif.log '

    return cmd


def peakstat(config, outdir, peak, label, rmdupbam, type="clip_ablife"):
    """

    1.peak mapping distribution statics， peaks  gene      ，   peak  gene。
    2.    。
    3.peak    。
    4.peak distribution relative2xxx
    5.  peak reads
    6.peak reads mapping distribution statics
    7.peak reads    summit
    8.  peak  ， callmotif  。
    :param config:
    :param outdir:
    :param peak:
    :param label:
    :param rmdupbam:
    :param type:
    :return:
    """
    cmd = ""

    if type == "clip_ablife":
        cmd += 'cd ' + outdir + ' && '
        cmd += "source " + config.gc['src'] + "/../venv/venv-py2/bin/activate && "
        cmd += 'python ' + config.gc['src'] + '/public/mapping_distribution_statics_v2.py -d ' + config.gc['gffdb'] + ' -b ' + peak + ' -m ' + label + '_peak_info.txt -n ' + label + '_peak &&'
        cmd += 'perl ' + config.gc['src'] + '/public/exp_add_anno.pl -exp ' + label + '_peak_info.txt -anno ' + config.gc["geneanno"] + ' -o ' + label + '_peak_info_addanno.txt -column -1 &'
        cmd += '\n'
        cmd += 'cd ' + outdir + ' && '
        cmd += "source " + config.gc['src'] + "/../venv/venv-py3/bin/activate && "
        cmd += 'python ' + config.gc['src'] + '/public/get_Cumulative_Data_From_File.py -i ' + peak + ' -n 6 -k Length && '
        cmd += """cat Cumulative.txt | perl -ne 'BEGIN{$f=0;}chomp;@line=split(/\s+/);next if(/^\+/);$n=$line[2]-$f;$f=$line[2];print $line[0],"\\t",$n,"\\n";' > _peak_length && """
        cmd += 'Rscript ' + config.gc['src'] + '/plot/Bar_width.r -f _peak_length -t "Peak Width Distribution" -n Peak_Width_Distribution -o ./ &'
        cmd += '\n'
        cmd += 'wait \n'
        cmd += 'cd ' + outdir + ' && '
        cmd += 'samtools view -L ' + peak + ' -b -o peak_reads.bam ' + rmdupbam + ' &&'
        cmd += 'samtools index peak_reads.bam &&'
        cmd += "source " + config.gc['src'] + "/../venv/venv-py2/bin/activate && "
        cmd += 'python ' + config.gc['src'] + '/public/mapping_distribution_statics_v2.py -d ' + config.gc['gffdb'] + ' -b peak_reads.bam  -n peak_reads && '
        cmd += "source " + config.gc['src'] + "/../venv/venv-py2/bin/activate && "
        cmd += 'python ' + config.gc['src'] + '/public/peakreads_distribution_to_summit.py -b peak_reads.bam -p ' + peak + ' -t clip -w 50 &'
        cmd += '\n'
        cmd += 'cd ' + outdir + ' && '
        cmd += 'perl ' + config.gc['src'] + '/public/pick_bed_fa.pl -bed ' + peak + ' -w ' + config.gc['genome'] + ' -o peak.fa -e 50 &'
        cmd += '\n'
        cmd += 'wait \n'

    return cmd


def peakplot(config, outdir, bamlist, namelist, peaklist):
    cmd = ""

    cmd += 'mkdir -p ' + outdir + ' && cd ' + outdir + ' && '
    cmd += 'perl ' + config.gc["src"] + '/plot/plot_genome_v2.0.4.pl -bam ' + bamlist + ' -name ' + namelist + ' -gff ' + config.gc['gff'] + ' -fa ' + config.gc['genome'] + ' -peak ' + peaklist + ' && '
    cmd += 'cat *.qsub/*.o*|grep cluster > filter.log && '
    cmd += """mkdir filter && cut -f 1 filter.log| sort| uniq | perl -ne 'chomp;$_=~/^(\w+)_cluster/;$chr=$1;print "cp $chr/$_ filter \\n";' > filter.sh && sh filter.sh"""

    return cmd


def report_parse(config, outdir, template):
    cmd = ""
    title = config.gc["title"]
    species = config.gc["species"]
    institutions = config.gc["institutions"]
    reportdate = config.gc["reportdate"]
    report_config = """
[[ablife:config]]
Title	""" + title + """
Species	""" + species + """
Institutions	""" + institutions + """
Reportdate	""" + reportdate + """
fujian	Supplements
public	assets/public
"""
    w = open(outdir + "/tempconfig", 'w')
    w.writelines(report_config)
    w.close()

    cmd += 'cd ' + outdir
    cmd += '\n\n'
    cmd += 'find ./ ! -path "*/log" -name "*.sh" -exec rm -rf {} \; -o ! -path "*/log" -name "log*" -exec rm -rf {} \; -o ! -path "*/log" -name "_*" -exec rm -rf {} \;'
    cmd += '&& rm -rf */*/temp && rm -rf temp'
    cmd += '\n\n'
    cmd += 'cat tempconfig ' + template + ' > report.template && perl ' + self.config.gc['src'] + '/ReportParserTools/latest/reportparser.pl -t report.template '
    cmd += '\n\n'
    cmd += 'tree Supplements > Supplements/Supplements_tree.txt'
    cmd += '\n\n'

    return cmd


def check_config_version(configfile):
    configfile = os.path.abspath(configfile)
    os.system('cat ' + configfile + ' | perl -ne "s/^\\*+//;print $_;" > _configfile.tmp.forcheckversion')
    cfile = os.path.abspath('_configfile.tmp.forcheckversion')
    myconfig = configparser.ConfigParser(allow_no_value=True, delimiters=('=',), comment_prefixes=('#',))
    myconfig.read(cfile)
    versioninfo = "None"
    if "version" in myconfig['gc']:
        versioninfo = myconfig['gc']["version"]
    os.system("rm -rf " + cfile)
    return versioninfo


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def test():
    """this is test function"""
    pass


if __name__ == '__main__':
    test()



    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
