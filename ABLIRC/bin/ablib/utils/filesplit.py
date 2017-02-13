#!/usr/bin/env python3
# coding: utf-8

####################################################################################
### Copyright (C) 2015-2019 by ABLIFE
####################################################################################





####################################################################################

####################################################################################
# Date           Version       Author            ChangeLog

#
#
#
#
#####################################################################################

"""
  （  ）    ：      ，           （  ）
"""


import re, os, sys, logging, time, datetime
from optparse import OptionParser
import subprocess



# if sys.version_info < (3, 0):
#     print("Python Version error: please use phthon3")
#     sys.exit(-1)


_version = 'v1.0'


# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
class SplitFiles():
    """      ."""

    def __init__(self, file_name, line_count_list, line_per_job=2, temp_path='./'):
        """                    """
        self.file_name = file_name
        self.line_count_list = line_count_list
        self.line_per_job = line_per_job
        self.part_file_list = []
        self.temp_path = temp_path

    def split_file(self):
        if self.file_name and os.path.exists(self.file_name):
            i = 0
            part_num = 1
            line_count = self.line_count_list[i] * self.line_per_job
            jobs_number = len(self.line_count_list)
            while line_count == 0 and i < jobs_number - 1:
                self.part_file_list.append('')
                i = i + 1
                line_count = self.line_count_list[i] * self.line_per_job
            try:
                with open(self.file_name) as f:
                    temp_count = 0
                    temp_content = []
                    for line in f:
                        if temp_count < line_count:
                            temp_count += 1
                        else:
                            if i < jobs_number - 1:
                                self.write_file(part_num, temp_content)
                                i = i + 1
                                line_count = self.line_count_list[i] * self.line_per_job
                                while line_count == 0 and i < jobs_number - 1:
                                    self.part_file_list.append('')
                                    i = i + 1
                                    line_count = self.line_count_list[i] * self.line_per_job
                                part_num += 1
                                temp_count = 1
                                temp_content = []
                        temp_content.append(line)
                    self.write_file(part_num, temp_content)


            except IOError as err:
                print(err)
        else:
            print("%s is not a validate file" % self.file_name)

    def get_part_file_name(self, part_num):
        """"          ：                temp_part_file，               """
        part_file_name = self.temp_path
        part_file_name += os.sep + "temp_file_" + str(part_num) + ".part"
        return part_file_name

    def write_file(self, part_num, *line_content):
        """                   """
        part_file_name = self.get_part_file_name(part_num)
        self.part_file_list.append(part_file_name)
        # print(line_content)
        try:
            with open(part_file_name, "w") as part_file:
                part_file.writelines(line_content[0])
        except IOError as err:
            print(err)


#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
