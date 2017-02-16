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
Pipeline main
"""

### Import
import os
import sys
import re

import configparser
import pygraphviz as pgv

sys.path.insert(1, os.path.split(os.path.realpath(__file__))[0] + "/../../")
from ablib.utils.tools import *
from ablib.pipeline import pipeline_modules
# from pipeline.base import Module
# from ablib.utils.distribution import *
import gffutils

### Version
_version = 'v2.0'
print("pipeline_main")


# -----------------------------------------------------------------------------------
### S Class definitions
# ------------------------------------------------------------------------------------
class Config:
    """
    """

    def __init__(self):
        self.gc = {}
        self.sample = {}
        self.list = {}
        self.group = {}
        self.switch = {}
        self.switchorder = {}
        self.finish = {}
        self.module = {}
        self.moduledef = {}
        self.custom = {}

        self._readFinish()
        self._registModules()

    def readConfigFile(self, configfile):
        self.configfile = os.path.abspath(configfile)
        os.system('cat ' + self.configfile + ' | perl -ne "s/^\\*+//;print $_;" > temp/configfile.tmp')
        self.configfile = os.path.abspath('temp/configfile.tmp')
        self.config = configparser.ConfigParser(allow_no_value=True, delimiters=('=',), comment_prefixes=('#',))
        self.config.read(self.configfile)

        self._readGlobleConfig()
        self._readSampleInfo()
        self._readSwitch()

        self._makeFlowChart()

    def _readGlobleConfig(self):
        genomedb = '/data0/Genome/genome_db.xls'
        if "genomedb" in self.config['gc']:
            genomedb = self.config['gc']["genomedb"]
        if "genomeid" in self.config['gc']:
            g = Genome(genomedb)
            if self.config['gc']['genomeid'] in g.allgenome:
                self.gc = g.allgenome[self.config['gc']['genomeid']].copy()
        # print(self.gc)
        self.gc.update(dict(self.config['gc']))
        self.gc["outdir"] = os.path.abspath("./")
        if "make-cmd-only" not in self.gc:
            self.gc["make-cmd-only"] = False
        if "run-post-only" not in self.gc:
            self.gc["run-post-only"] = False
        # print(self.gc)
        if "gffdb" in self.gc:
            db = gffutils.FeatureDB(self.gc["gffdb"])
            self.gc["genenumber"] = db.count_features_of_type("gene")
            # print(self.gc["genenumber"])
        if "genome" in self.gc:
            if ("chrlen" not in self.gc) or self.gc["chrlen"] is None:
                cmd = 'getChrLength.pl ' + self.gc["genome"] + ' chrlen'
                logging.debug(cmd)
                if not os.path.isfile('chrlen'):
                    os.system(cmd)
                self.gc["chrlen"] = self.gc["outdir"] + '/chrlen'

    def _readSampleInfo(self):
        self.gc["sample_num"] = 0
        if 'sample' not in self.config:
            return None
        for key in self.config['sample']:
            if key.lower().startswith('sample'):
                info = self.config['sample'][key].split(':')
                samplename = info[0]
                self.sample[samplename] = {}

                if info[1] and info[1] != "":
                    if not (info[1].startswith('/') or info[1].startswith('~')):
                        info[1] = self.config['sample']['indir'] + '/' + info[1]
                    self.sample[samplename]['end1'] = info[1]
                    self.sample[samplename]['single'] = info[1]
                else:
                    raise Exception(samplename + "没有指定fq文件")

                if len(info) >= 3 and info[2] != "":
                    if not (info[2].startswith('/') or info[2].startswith('~')):
                        info[2] = self.config['sample']['indir'] + '/' + info[2]
                    self.sample[samplename]['end2'] = info[2]
                    self.sample[samplename]['pe'] = "pairend"
                else:
                    self.sample[samplename]['pe'] = "single"

                if len(info) >= 4 and info[3] != "":
                    self.sample[samplename]['library-type'] = info[3]
                else:
                    self.sample[samplename]['library-type'] = self.config['sample']['library-type']

                self.gc["sample_num"] += 1

            if key.lower().startswith('group'):
                # info = self.config['sample'][key].split(':')
                # if len(info) == 2:
                #     self.list[info[1]] = info[0].split(',')
                self.group[key]=self.config['sample'][key].split(':')

    def _readSwitch(self):
        for section in self.config.sections():
            if section.startswith('module:'):
                info = section.split(':')
                module_name = info[1]
                order = self.config[section]['order']
                module_argv = dict(self.config[section])
                module_argv['name'] = module_name
                if 'id' not in module_argv:
                    module_argv['id'] = module_name

                if 'skip' not in self.config[section] or not to_bool(self.config[section]['skip']):
                    if order not in self.switchorder:
                        self.switchorder[order] = []
                    self.switchorder[order].append(module_argv)

    def _makeFlowChart(self):
        G = pgv.AGraph(strict=False, directed=True)
        G.graph_attr['label'] = 'Pipeline Flow Chart'
        # G.add_node("Sample", shape='box')
        for section in self.config.sections():
            if section.startswith('module:'):
                info = section.split(':')
                module_name = info[1]
                order = self.config[section]['order']
                module_argv = dict(self.config[section])
                module_argv['name'] = module_name
                if 'id' not in module_argv:
                    module_argv['id'] = module_name
                if 'skip' not in self.config[section] or not to_bool(self.config[section]['skip']):
                    G.add_node(module_argv['id'], shape='box', color='cornflowerblue', style='filled', fontcolor='white')
                    for option in module_argv:
                        if option.startswith("output:") or option.startswith("o:") or option.startswith("out:"):
                            outputkey = re.sub(r'^\w+\:', '', option)
                            G.add_node(module_argv['id'] + ":" + outputkey, label=outputkey, shape='diamond', style='filled', color='darkgoldenrod2', fontcolor='navy', fontsize='12')
                            G.add_edge(module_argv['id'], module_argv['id'] + ":" + outputkey)
                            if module_argv[option] is None:
                                continue
                            if module_argv[option].startswith("target|sample:"):
                                match = re.search(r'^target\|sample:([\w\-]+)', module_argv[option])
                                if not match:
                                    continue
                                skey = match.group(1)
                                G.add_edge(module_argv['id'] + ":" + outputkey, 'Sample', label=skey)
                            continue
                        if module_argv[option] is None:
                            continue
                        inputkey = option
                        if option.startswith("input:") or option.startswith("i:") or option.startswith("in:"):
                            inputkey = re.sub(r'^\w+\:', '', option)
                        if module_argv[option].startswith("source|sample:"):
                            match = re.search(r'^source\|sample:([\w\-]+)', module_argv[option])
                            if not match:
                                continue
                            skey = match.group(1)
                            G.add_edge('Sample', module_argv['id'], label=skey)
                        elif module_argv[option].startswith("source|gc:"):
                            match = re.search(r'^source\|gc:([\w\-]+)', module_argv[option])
                            if not match:
                                continue
                            skey = match.group(1)
                            G.add_edge('GC', module_argv['id'], label=skey)
                        elif module_argv[option].startswith("source|"):
                            match = re.search(r'^source\|([\w\-]+):([\w\-]+)', module_argv[option])
                            if not match:
                                continue
                            mid = match.group(1)
                            mkey = match.group(2)
                            G.add_edge(mid + ":" + mkey, module_argv['id'])
        G.write("flowchart.dot")
        G.layout(prog='dot')
        G.draw('flowchart.png')

    def _readFinish(self):
        if not os.path.isfile('finished_modules.txt'):
            temp = open('finished_modules.txt', "w")
            temp.close()
            return None
        for line in open('finished_modules.txt'):
            line = line.strip()
            self.finish[line] = 1

    def _registModules(self):
        self.moduledef = pipeline_modules.register()

    def checkconfig(self, type, key, modulename=""):
        if type == "gc":
            if (key not in self.gc) or self.gc[key] is None:
                return False
            else:
                return self.gc[key]
        elif type == "module":
            if (key not in self.module[modulename]) or self.module[modulename][key] is None:
                return False
            else:
                return self.module[modulename][key]


class Genome:
    """
    Genome处理类
    """

    def __init__(self, genomedb=None):
        self.genomedb = genomedb
        self.allgenome = {}
        if genomedb is not None:
            self.readGenomeDB()

    def readGenomeDB(self):
        title = []
        for line in open(self.genomedb):
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            if line.startswith('genomeid'):
                title = line.split('\t')
            else:
                temp = line.split('\t')
                i = 0
                for item in temp:
                    if i == 0:
                        self.allgenome[item] = {}
                    else:
                        self.allgenome[temp[0]][title[i]] = item
                    i += 1

    def showGenome(self, id="all"):
        if id == "all":
            for g in self.allgenome:
                print(g)
        else:
            if id in self.allgenome:
                for key in self.allgenome[id]:
                    print(key + ' : ' + self.allgenome[id][key])
            else:
                print("Genome " + id + " is not in genome db file yet")


# -----------------------------------------------------------------------------------
### E Class definitions
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------

def runThem(module_list, config, fi):
    jobs = []
    n = 0
    server = multiprocessing.Manager()
    error_module = server.dict()

    for module in module_list:
        # print(module)
        t = multiprocessing.Process(target=runModule, args=(config, module, error_module))
        jobs.append(t)
        n += 1
    for i in range(n):
        jobs[i].start()
    for i in range(n):
        jobs[i].join()

    ed = dict(error_module).copy()
    server.shutdown()
    for module in module_list:
        if module['id'] not in config.finish and module['id'] not in ed:
            fi.writelines(module['id'] + '\n')
        config.finish[module['id']] = 1
        updateConfig(config, module)


def runModule(config, module, error_module):
    """
    :param config:
    :return:
    """
    if module['name'] in config.moduledef:
        ThisModule = config.moduledef[module['name']]
        m = ThisModule(config, module)
        check_error = m.run()
        if check_error == "error":
            error_module[module['id']] = 1
        return module['name']
    else:
        logging.info("[" + module['name'] + "] is not defined")
        return None


def updateConfig(config, module):
    if module['name'] in config.moduledef:
        ThisModule = config.moduledef[module['name']]
        m = ThisModule(config, module)
        m.update_config(config)
        # print(config.sample)
        return module['name']
    else:
        logging.info("[" + module['name'] + "] is not defined")
        return None


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
    ### E
    # -----------------------------------------------------------------------------------
