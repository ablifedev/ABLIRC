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
Modules regist
"""

### Import

from ablib.pipeline.modules import clipseq
from ablib.pipeline.modules import dataclean
from ablib.pipeline.modules import public

### Version
_version = 'v1.0'
print("pipeline_modules")

# -----------------------------------------------------------------------------------
### S modules regist function
# -----------------------------------------------------------------------------------

def register():
    moduledef = {}

    ## ===================== dataclean ==================== ##
    moduledef["cleanreads"] = dataclean.CleanReads
    moduledef["testreads"] = dataclean.TestReads

    ## ===================== public ====================== ##

    moduledef["gff"] = public.Gff
    moduledef["fastqc"] = public.Fastqc
    moduledef["mapping_tophat2"] = public.Mapping_Tophat2
    moduledef["bam2bed"] = public.Bam2bed

    moduledef["exp"] = public.EXP
    moduledef["mapregion"] = public.MapRegion
    moduledef["distance2xxx"] = public.Distance2XXX
    moduledef["plotgenome"] = public.PlotGenome

    moduledef["genome_coverage"] = public.Genome_coverage

    moduledef["ckconfig"] = public.CheckConfig

    ## ===================== clip ====================== ##
    moduledef["clip_basic"] = clipseq.ClipBasic
    moduledef["clip_callpeak_ablife"] = clipseq.ClipCallpeakAblife
    moduledef["clip_stat"] = clipseq.ClipStat
    #moduledef["clip_overlap"] = clipseq.ClipOverlap
    moduledef["clip_findmotifs"] = clipseq.ClipFindMotifs
    moduledef["clip_report"] = clipseq.ClipReport
    moduledef["clip_plot"] = clipseq.ClipPlot


    return moduledef

# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

