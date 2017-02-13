#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-09-20 14:19:06
# @Last Modified by:   anchen
# @Last Modified time: 2016-10-20 15:50:41
import os,re
import sys

for paramIndex in range(0,len(sys.argv)):
    if sys.argv[paramIndex] == "-venndir":
        venn_dir=sys.argv[paramIndex+1]
    if sys.argv[paramIndex] == "-typebed":
    	type_bed=sys.argv[paramIndex+1]
hash1={}
hash2={}
f1=open(type_bed,"r")
dirname=os.path.dirname(os.getcwd()).split("/")[-1]
while 1 :
	line=f1.readline().strip()
	if line=="":
		break
	else:
		items=line.split("\t")
		if items[-2] not in hash1.keys():
			hash1[items[-2]]=line
		else:
			hash1[items[-2]]=hash1[items[-2]]+"::"+line
# for key in hash1:
# 	print (hash1[key])
#print(hash1[items[-2]])
files=os.listdir(venn_dir)
f1.close()
for file in files:
	if file.endswith(".txt"):
		f1=open(venn_dir+"/"+file,"r")
		f2=open(venn_dir+"/"+file.split(".txt")[0]+"_peak","w")
		names=file.split(".txt")[0].split("_olp_")
		while 1:
			line=f1.readline().strip()
			if line=="":
				break
			else:
				peaks=hash1[line].split("::")
				for name in names:
					for peak in peaks:
						if name == peak.split("\t")[-1]:
							f2.write(peak+"\n")
		f1.close()
		f2.close()


