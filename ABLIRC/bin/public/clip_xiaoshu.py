#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-10-19 17:11:32
# @Last Modified by:   anchen
# @Last Modified time: 2016-11-14 14:10:54
import os,re
import sys

for paramIndex in range(0,len(sys.argv)):
    if sys.argv[paramIndex] == "-i":
        input_file=sys.argv[paramIndex+1]

f1=open(input_file,"r")
lines=f1.readlines()
f1.close()
f2=open(input_file,"w")
for i in range(len(lines)):
	if i==0:
		f2.write(lines[i])
	else:
		items=lines[i].split("\t")
		for j in range(1,len(items)):
			items[j]="%.4f"%float(items[j])
		f2.write("\t".join(items)+"\n")

# 	EIF3B_1st	EIF3B_2nd	IgG_1st	IgG_2nd
f2.close()
# EIF3B_1st	1.0000	0.9937	0.9222	0.9768
# EIF3B_2nd	0.9937	1.0000	0.9164	0.9740
# IgG_1st	0.9222	0.9164	1.0000	0.9333
# IgG_2nd	0.9768	0.9740	0.9333	1.0000