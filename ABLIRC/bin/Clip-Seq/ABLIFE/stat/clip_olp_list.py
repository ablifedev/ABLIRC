#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-09-09 15:58:45
# @Last Modified by:   anchen
# @Last Modified time: 2016-11-18 15:15:22
import os,re
import sys

for paramIndex in range(0,len(sys.argv)):
    if sys.argv[paramIndex] == "-olplist":
        olp_list=sys.argv[paramIndex+1]
    if sys.argv[paramIndex] == "-typebed":
        type_bed=sys.argv[paramIndex+1]
    if sys.argv[paramIndex] == "-gene1":
        gene1=sys.argv[paramIndex+1]
    if sys.argv[paramIndex] == "-gene2":
        gene2=sys.argv[paramIndex+1]


hash1={}
hash_stat={}
f1=open(olp_list,"r")
merge_olp_peak=0
while 1 :
	line=f1.readline().strip()
	if line=="":
		break
	else:
		hash1[line]="1"
		merge_olp_peak+=1
f1.close()
f2=open(type_bed,"r")

f3=open(gene1+"_olp_peak","w")
hash_stat[gene1+"_olp_peak"]=0
f4=open(gene2+"_olp_peak","w")
hash_stat[gene2+"_olp_peak"]=0
f5=open(gene1+"_specific_peak","w")
hash_stat[gene1+"_specific_peak"]=0
f6=open(gene2+"_specific_peak","w")
hash_stat[gene2+"_specific_peak"]=0
hasha={}
hashb={}
while 1 :
	line=f2.readline().strip()
	if line=="":
		break
	else:
		items=line.split("\t")
		if items[-2] in hash1:
			if items[-1]=="sample1":
				f3.write(line.split("\t")[-2]+"\t"+line+"\n")
				hash_stat[gene1+"_olp_peak"]=hash_stat[gene1+"_olp_peak"]+1
			elif items[-1]=="sample2":
				f4.write(line.split("\t")[-2]+"\t"+line+"\n")
				hash_stat[gene2+"_olp_peak"]=hash_stat[gene2+"_olp_peak"]+1
		else:	
			if items[-1]=="sample1":
				f5.write(line+"\n")
				hash_stat[gene1+"_specific_peak"]=hash_stat[gene1+"_specific_peak"]+1

			elif items[-1]=="sample2":
				f6.write(line+"\n")
				hash_stat[gene2+"_specific_peak"]=hash_stat[gene2+"_specific_peak"]+1	
f2.close()

hash2={}
f1=open("../_allpeaks_cluster_type_s1","r")
while 1 :
	line=f1.readline().strip()
	if line=="":
		break
	else:
		items=line.split("\t")
		if items[10]=="--":
			pass
		else: 
			hash2[items[10]]=line
f1.close()
hash3={}
f1=open("../_allpeaks_cluster_type_s2","r")
while 1 :
	line=f1.readline().strip()
	if line=="":
		break
	else:
		items=line.split("\t")
		if items[10]=="--":
			pass
		else:
			hash3[items[10]]=line
f1.close()
f7=open("olp_gene","w")
hash_stat[gene1+"_olp_gene"]=0
hash_stat[gene2+"_olp_gene"]=0
f8=open(gene1+"_specific_gene","w")
hash_stat[gene1+"_specific_gene"]=0
f9=open(gene2+"_specific_gene","w")
hash_stat[gene2+"_specific_gene"]=0
for key in hash2.keys():
	if key in hash3:
		f7.write(hash3[key]+"\n")
		hash_stat[gene1+"_olp_gene"]=hash_stat[gene1+"_olp_gene"]+1
		hash_stat[gene2+"_olp_gene"]=hash_stat[gene2+"_olp_gene"]+1
	else:
		f8.write(hash2[key]+"\n")
		hash_stat[gene1+"_specific_gene"]=hash_stat[gene1+"_specific_gene"]+1
for key in hash3.keys():
	if key not in hash2:
		f9.write(hash3[key]+"\n")
		hash_stat[gene2+"_specific_gene"]=hash_stat[gene2+"_specific_gene"]+1

f7.close()
f8.close()
f9.close()
f1=open("_Repeated_peaks_in_duplicate_experiments","w")
for key in hash_stat:
	f1.write(key+" : "+str(hash_stat[key])+"\n")
f1.write(gene1+"_merge_olp_peak : %s\n"%merge_olp_peak)
f1.write(gene2+"_merge_olp_peak : %s\n"%merge_olp_peak)
f1.close()

