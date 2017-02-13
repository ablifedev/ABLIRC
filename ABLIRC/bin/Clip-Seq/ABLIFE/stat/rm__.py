#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-11-18 17:06:06
# @Last Modified by:   anchen
# @Last Modified time: 2016-11-18 17:13:03
f1=open("_allpeaks_cluster_type_s1_olp_s2","r")
f2=open("_allpeaks_cluster_type_s1_olp_s2.new","w")
while 1 :
	line=f1.readline()
	if line=="":
		break
	else:
		items=line.split("\t")
		if items[10]=="--":
			pass
		else:
			f2.write(line)
f1.close()
f2.close()