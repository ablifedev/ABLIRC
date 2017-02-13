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
data clean
"""

###
# import subprocess
# import smtplib
# import email.mime.multipart
# import email.mime.text
# import multiprocessing
# import shutil

from ablib.utils.tools import *
from ablib.pipeline.base import *

### version
_version = 'v1.0'



# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------

class CleanReads(Module):
    """clean reads"""

    def init_input(self):
        self.input_ids["DICT"].append("rawsamples")
        self.inputs["rawsamples"] = self.config.sample

    def init_output(self):
        self.output_ids["PATH"].append("cleanreads_dir")
        self.outputs["cleanreads_dir"] = self.outdir
        self.output_ids["FILE"].append("rawstat")
        self.outputs["rawstat"] = self.outdir + "/raw_stat.xls"

    def update_sample(self, config):
        for s in config.sample:
            config.sample[s]["end1"] = self.outdir + "/" + s + ".fq"
            config.sample[s]["single"] = self.outdir + "/" + s + ".fq"
        # print(config.sample)
        # pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            self.qsub_cmd += "cd " + self.outdir + " && "
            self.qsub_cmd += "source " + self.config.gc['src'] + "/../venv/venv-py3/bin/activate && "
            self.qsub_cmd += 'perl ' + self.config.gc['src'] + '/Dataclean/nextseq_clean.pl -samplename ' + s + ' -fq ' + self.config.sample[s]["end1"] + " && "
            self.qsub_cmd += "\n"

    def make_post_cmd(self):
        self.post_cmd += "cd " + self.outdir + " && "
        self.post_cmd += "ls " + self.config.gc["outdir"]
        self.post_cmd += """/clean_qsub.sh.*.qsub/clean_qsub_0000*.sh.e* | perl -ne 'BEGIN{print "samplename\\trawreads\\trawbases\\tcleanreads\\tcleanbases\\n";}chomp;@read=();@write=();@baseread=();@basewrite=();open IN,"$_";while(<IN>){chomp;if(/Total reads processed:\s+(\S+)/){$readtmp=$1;$readtmp=~s/,//g;push @read,$readtmp;}if(/Total basepairs processed:\s+(\S+) bp/){$readtmp=$1;$readtmp=~s/,//g;push @baseread,$readtmp;}if(/Reads written \(passing filters\):\s+(\S+) \((\S+)\)/){$readtmp=$1;$ratiotmp=$2;$readtmp=~s/,//g;push @write,$readtmp;}if(/Total written \(filtered\):\s+(\S+) bp \((\S+)\)/){$readtmp=$1;$ratiotmp=$2;$readtmp=~s/,//g;push @basewrite,$readtmp;}if(/Started analysis of (\S+).fq/){$name=$1;print $name,"\\t",$read[0],"\\t",$baseread[0],"\\t",$write[-1],"\\t",$basewrite[-1],"\\n";}}close IN;' > raw_stat.xls\n"""


class TestReads(Module):
    """reads test"""

    def init_input(self):
        self.input_ids["PATH"].append("cleanreads_dir")
        self.inputs["cleanreads_dir"] = self.config.gc["outdir"] + '/result/clean/'
        self.input_ids["FILE"].append("rawstat")
        self.inputs["rawstat"] = self.config.gc["outdir"] + '/result/clean/raw_stat.xls'

    def init_output(self):
        self.output_ids["FILE"].append("statics_file")
        self.outputs["statics_file"] = self.outdir + '/statout.xls'

    def update_sample(self, config):
        pass

    def check_config(self):
        return False

    def make_pre_cmd(self):
        pass

    def make_qsub_cmd(self):
        for s in self.config.sample:
            self.qsub_cmd += "cd " + self.outdir + " && "
            self.qsub_cmd += 'perl ' + self.config.gc['src'] + '/Dataclean/nextseq_test_singleend.pl -samplename ' + s + ' -fq ' + self.config.sample[s]["end1"] + ' -cleandir ' + self.inputs["cleanreads_dir"] + " && "
            self.qsub_cmd += "\n"

    def make_post_cmd(self):
        self.post_cmd += "cd " + self.outdir + " && "
        self.post_cmd += "cat *gc_dup > gc_dup.txt && cat *uniqtag > uniqtag.txt && cat *q30 > q30.txt && "
        self.post_cmd += "perl " + self.config.gc['src'] + "/Dataclean/stastics.pl "+self.inputs["rawstat"]+" uniqtag.txt gc_dup.txt q30.txt\n"

# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------
