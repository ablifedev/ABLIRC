#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-10-20 15:02:04
# @Last Modified by:   anchen
# @Last Modified time: 2016-11-18 17:17:49
import os,re
path=os.getcwd()
dirs=os.listdir()
hash1={}
for dir1 in dirs:
	if re.match("ablife_group*",dir1):
		f1=open(path+"/"+dir1+"/ablife_venn/_Repeated_peaks_in_duplicate_experiments","r")
		while 1 :
			line=f1.readline().strip()
			if line=="":
				break
			else:
				items=line.split(" : ")
				#print (items)
				if re.match(".*_olp_peak",items[0]):
					if re.match(".*_merge_olp_peak",items[0]):
						sample=items[0].split("_merge_olp_peak")[0]
						if sample not in hash1:
							hash1[sample]={}
						hash1[sample]["_merge_olp_peak"]=items[1]
					else:
						sample=items[0].split("_olp_peak")[0]
						if sample not in hash1:
							hash1[sample]={}
						hash1[sample]["_olp_peak"]=items[1]
				elif re.match(".*_specific_gene",items[0]):
					sample=items[0].split("_specific_gene")[0]
					if sample not in hash1:
						hash1[sample]={}					
					hash1[sample]["_specific_gene"]=items[1]				
				elif re.match(".*_specific_peak",items[0]):
					sample=items[0].split("_specific_peak")[0]
					if sample not in hash1:
						hash1[sample]={}					
					hash1[sample]["_specific_peak"]=items[1]
				elif re.match(".*_olp_gene",items[0]):
					sample=items[0].split("_olp_gene")[0]
					if sample not in hash1:
						hash1[sample]={}
					hash1[sample]["_olp_gene"]=items[1]
				# elif re.match(".*_merge_olp_peak",items[0]):
				# 	sample=items[0].split("_merge_olp_peak")[0]
				# 	if sample not in hash1:
				# 		hash1[sample]={}
				# 	hash1[sample]["_merge_olp_peak"]=items[1]
		f1.close()
f1=open("Repeated_peaks_in_ablife_group.xls","w")
f1.write("Sample\tolp_peak\tmerge_olp_peak\tspecific_peak\n")
for key in hash1:
	#print (key)
	f1.write(key+"\t"+hash1[key]["_olp_peak"]+"\t"+hash1[key]["_merge_olp_peak"]+"\t"+hash1[key]["_specific_peak"]+"\n")
f1.close()