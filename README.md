## Introduce

ABLIRC is a workflow for peak-calling and analyzing CLIP-seq sequencing datasets.

## Download

Download current release: [ABLIRC-1.0.0](http://ablife.cc/ABLIRC/RELEASE/ABLIRC.tar.gz)

Download example data:    [ABLIRC-example-data](http://ablife.cc/ABLIRC/RELEASE/ABLIRC-example-data.tar.gz)

## Installation

The program only works on linux platform, before the installation, both python2 and python3 are required, during the installation, the program will create a new virtual environment for python, and all the relevant toolkits will be installed in this virtual environment. Process will check the current environment to find the dependent packages, if not found, the pocess will install them by pip, CPAN automatically, so make sure your network connection activity. Besides, there are some repuired tools which need for manual installation, all the requirements are as followed:  

Required software:

* Perl (>=5.10, https://www.perl.org/get.html)

* Python2 (>=2.7, https://www.python.org/downloads/)

* Python3 (>=3.3, https://www.python.org/downloads/)

* R (>=3.2.0, https://cloud.r-project.org/)

* Samtools (>=1.2, http://www.htslib.org/download/)

* bedtools (http://bedtools.readthedocs.io/en/latest/)

* Bowtie2 (>=2.2.5, http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

* TopHat2 (>=2.0.13, http://ccb.jhu.edu/software/tophat/index.shtml)

* FASTX-Toolkit (>=0.013, http://hannonlab.cshl.edu/fastx_toolkit/)

Required R packages:

* ggplot2  

* reshape2  

* plotrix  

* methods  

* corrplot  

* RColorBrewer  

* Gtable  

* Grid  


After all of the requirments being installed, you can install the program as followed:   

1. Unzip the file `ABLIRC.tar.gz`:   
	`tar -zxf ABLIRC.tar.gz`   

2. Writting the path of python2 and python3 to the python2_path file and python3_path file.  
	a) Open the ABLIRC root folder:   
		`cd install/`   
		`vi python2_path`  
		`vi python3_path`   

	b) Open the ABLIRC root folder:   
		`make`  

## Usage

First time to run the program,you can by the fowlling steps:  

1. Step1:  
cp the configuration file `clipseq.config.sample` to you workdir:  
	`cp clipseq.config.sample <workdir>`  

2. Step2:  
Fill in the configuration file correctly fill in the parameters according to the information in the configuration file, which parameter starts with a `*` is required , it means there is no default value with it ,you should fill it with you data information or chose correctly value according to you task, specific requirements will be detailed in the annotation. The other parameters are optional parameters, It is recommended to use the default value, all the required parameters are divided into the following parts:

	a) Select whether to use the sge cluster for the calculation, if sge is already installed on your platform, you could fill `usesge=yes`, and determine the number of nodes and CPUs used by sge. Else, the task will be running with multi-process at a single node. (reference parameters: usesge, cpu, sgequeue)  
	b) definitions about you clip data, fill in the folder where the full path, the name of each file and definite the corresponding sample name, make sure that each of you clipseq-data-file following the lines of SAMPLE. (reference parameters: indir, library-type,sample1,sample2...)  
	c) Modify the specific parameters of each module as needed. More details of the parameters, please refer to the comments in the config file.  

3. Step3:  
Run the ABLIRC : Make sure the `runPipe` in you path configure or you can use absolute path , then you can run the ABLIRC like this:  
	`runPipe -c clipseq_config.sample`  

## Config file template

You can copy and modify this config template.

```
#===================================================================#
#================= Globle config and Genome config =================#
#===================================================================#
[gc]

# Project infomation, for Report front cover
Title = Clip-seq Analyze with ABLIRC
Institutions = Example Lab
Reportdate = 2015-5-20

# If filled 'T', The program only generates commands , but the command is not executed,if filled 'F', the command will be executed immediately after generation.
make-cmd-only = F

# Genome ID used in the analysis, genomeinfo table should be filled. (genomeinfo.xls)
GenomeID = human_gencode_v23

# decide whether to use the sge server for qsub task delivery, if you have installed sge, fill 'yes', the task will be distributed to each node through the qsub, otherwise fill 'no', the task will be running with multi-threaded at a single node.
usesge = yes

# number of CPUs to use, if you choose to use sge, then the number of CPU is the maximum number of threads used.
cpu = 16

# The delivery node, it was needed if 'useage' is yes.
sgequeue = new.q

#======================================================#
#================= Sample information =================#
#======================================================#
[sample]

# fullname of the clipseq data input-dir-path.
indir = /data12/dev/magl/updata_pipeline/ablifedev/clipseq/reads

# choose whether the library was build on strand, fill 'strand' or 'unstrand'
library-type = unstrand

# name the each sample, the naming rules is 'sampleX = sample alias: sample file name'，you must list all you samples in the list, and specify an alias for each of them, all the alias must be different.
SAMPLE1 = Eif3b_1:HEK293_Eif3b_1st.fq
SAMPLE2 = Eif3b_2:HEK293_Eif3b_2nd.fq
SAMPLE3 = IgG_1:HEK293_IgG_1st.fq
SAMPLE4 = IgG_2:HEK293_IgG_2nd.fq

# You must define the groups, normally, the sample and its control sample may be placed in a group. You can list all you samples with many groups, each group will be generated a result of callpeak.
GROUP1 = Eif3b_1:IgG_1
GROUP2 = Eif3b_2:IgG_2

#======================================================#
#======== Modules setting[module:modulename] ==========#
#======================================================#
# The following sections describe the parameter settings for each module



# Clean the raw reads, Remove unqualified reads.
[module:cleanreads]
#The execution order of this module
order = 1
id = clean

#whether skip the module,if is "F" , this module will be executed normal,if is "T", this module will be skipped, even not make a commamd.
skip = F
o:cleanreads_dir
o:rawstat

# Select a part of the reads to test and evaluate the quality of the data.
[module:testreads]
order = 2
id = statics
skip = F
cleanreads_dir = source|clean:cleanreads_dir
rawstat = source|clean:rawstat
o:statics_dir

# Analysis of data quality statistics by fastqc.
[module:fastqc]
order = 2
skip = F

# Align sequence to the genome, The mapping tool used is Tophat2, you can set the parameters below.
[module:mapping_tophat2]
id = mapping__tophat2
order = 2
skip = F
# most threads to use.
threads = 5
# Maximum number of mismatches.
readmis = 2
# Maximum number of mismatches to bowtie2.
b2mis = 1
# You can add any tophat or bowtie2 parameters on this line,they will be executed during the Tophat2 running.
other_argv = -a 8 -m 0 -g 2 -p 12 --microexon-search --no-coverage-search --report-secondary-alignments

# The definition of the output files, they are needed by the downstream modules. We recommend that you do not modify them.
o:uniqbam
o:mapresult

# Convert the resulting bam file to a bed file, and remove the duplication results, the output will be used to callpeak.
[module:bam2bed]
id = mapping__bam2bed
order = 3
skip = F
uniqbam = source|mapping__tophat2:uniqbam
o:rmdup_uniq_bam
o:rmdup_uniq_bed

# Statistical information on the different regions of the gene annotation file.
[module:gff]
order = 3
skip = F

# According to the results of mapping, statistics the distribution of regions where reads aligned on the genome.
[module:mapregion]
id = basic__mapregion
order = 3
skip = F
uniqbam = source|mapping__tophat2:uniqbam
mapresult = source|mapping__tophat2:mapresult

# According to the results of mapping, statistics the distribution of the distance between reads and TSS,TTS.
[module:distance2xxx]
id = basic__distance2xxx
order = 3
skip = F
uniqbam = source|mapping__tophat2:uniqbam

# According to the results of mapping, calulate the expression of each genes.
[module:exp]
id = basic__exp
order = 3
skip = F
uniqbam = source|mapping__tophat2:uniqbam

# The basic analysis of the clipseq, the correlation between the individual samples is calculated.
[module:clip_basic]
id = basic__clip_basic
order = 4
skip = F
min_sum_rpkm = 0.3
uniqbam = source|mapping__bam2bed:rmdup_uniq_bam
#raw_pas_bam = source|filter_pas_reads:raw_pas_bam
#o:pas_bam_discardip

# This module is used to callpeak, make sure the module 'mapping_tophat2' has been runned and the output file 'rmdup_uniq_bed' and 'rmdup_uniq_bam' are exist. If you have listed your samples into groups previously, each group would be generated a result of callpeak. Besides, you can compare the difference of the callpeak result between two groups, you just need fill the parameter 'ablife_groupX', notice that the two group was connected with a ':', samples in each group was connected with a "_vs_".
[module:clip_callpeak_ablife]
id = clip_callpeak__ablife
order = 4
skip = F

uniqbed = source|mapping__bam2bed:rmdup_uniq_bed
uniqbam = source|mapping__bam2bed:rmdup_uniq_bam
o:peakfa
o:peakinfo
o:nonoverlap_peaks
o:peakreads
o:peaksense
o:peakantisense


# This module is used to statistics the result of callpeak. Calculate the sense and antisense peaks, compare overlap peaks between different groups.
[module:clip_stat]
id = clip_callpeak__stat
order = 7
skip = F
uniqbam = source|mapping__bam2bed:rmdup_uniq_bam
peakinfo1 = source|clip_callpeak__ablife:peakinfo
peak_nonoverlap1 = source|clip_callpeak__ablife:nonoverlap_peaks
peakreads1 = source|clip_callpeak__ablife:peakreads
peaksense = source|clip_callpeak__ablife:peaksense
peakantisense = source|clip_callpeak__ablife:peakantisense

# Find the motif sequences according to the callpeak result.
[module:clip_findmotifs]
id = clip_callpeak__findmotifs
order = 7
skip = F
peakfa_ablife = source|clip_callpeak__ablife:peakfa

# Plot a diagram by circos, which showing the distribution of the peaks on the genome. 
[module:clip_plot]
id = clip_plot
order = 8
skip = F
uniqbam = source|mapping__bam2bed:rmdup_uniq_bam
peakinfo1 = source|clip_callpeak__ablife:peakinfo

# Generate a report of the result.
[module:clip_report]
id = report
order = 9
skip = F
Template = CLIP-seq.template
Clean_INFO = clean_info.txt
Sample_INFO = sample_info.txt

# Appendix.
Sup0 = Reference_genome
Sup1 = Library
Sup2 = Quality_control
Sup3 = Mapping
Sup4 = Correlation
Sup5 = Peak_and_peak_gene
Sup6 = Motif_results
Sup7 = Peak_gene_function

```
