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
tools functions
"""

### import packages
import re, os, sys, logging, time, datetime
from optparse import OptionParser
import subprocess
import smtplib
import email.mime.multipart
import email.mime.text
import fnmatch
import multiprocessing
import signal


### version
_version = 'v1.0'


# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
class Watcher:
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.  See Appendix A of The Little Book of Semaphores.
    http://greenteapress.com/semaphores/

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.
    """

    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            # I put the capital B in KeyBoardInterrupt so I can
            # tell when the Watcher gets the SIGINT
            print('KeyBoardInterrupt')
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------
### S functions
# -----------------------------------------------------------------------------------

def block(file, size=65536):
    while True:
        nb = file.read(size)
        if not nb:
            break
        yield nb


def isset(v):
    try:
        type(eval(v))
    except:
        return 0
    else:
        return 1


def getLineCount(filename, title=0, restr="\n"):
    """
    :param filename
    :param title: title line number
    :param restr:\n
    :return:
    """
    with open(filename, "r") as f:
        return sum(line.count(restr) for line in block(f)) - title


def makeFaIntoSingle(fa, outFa):
    seq = ''
    temp = {}
    name = ''
    with open(outFa, 'w') as o:
        for line in open(fa):
            line = line.strip()
            if line.startswith('>'):
                if seq != '':
                    temp[name] = seq
                # o.writelines(seq+'\n') if seq!='' else None
                seq = ''
                name = line
            else:
                seq += line
        temp[name] = seq if seq != '' else None
        for i in temp:
            o.writelines(str(i) + '\n')
            o.writelines(str(temp[i]) + '\n')




def all_file(root, patterns='*', single_level=False, yield_folders=False):
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern.strip()):
                    yield os.path.join(path, name)
        if single_level:
            break




def getBamReadsNumber(bamfile, model="single"):
    mapped_fragment = 0
    mapped_reads = 0
    mapped_pair = 0
    for tmp in os.popen('samtools stats ' + bamfile).readlines():
        match = re.search(r'reads mapped:\s+(\d+)', tmp.strip())
        match2 = re.search(r'reads mapped and paired:\s+(\d+)', tmp.strip())
        if match:
            mapped_reads = int(match.group(1))
        elif match2:
            mapped_pair = int(match2.group(1)) / 2
        else:
            continue
    mapped_fragment = mapped_reads - mapped_pair
    if model == "paired":
        return mapped_fragment
    else:
        return mapped_reads


def readBamHeader(bamfile, min_len=0):
    cmd = 'samtools view -H ' + bamfile
    chr_dict = {}
    logging.info("readBamHeader: " + cmd)
    output = os.popen(cmd).readlines()
    # status, output = subprocess.getstatusoutput(cmd)
    # if (int(status) != 0):  # it did not go well
    #     logging.debug("error in blast %s" % status)
    #     logging.debug("error detail: %s" % output)
    for eachLine in output:
        logging.info(eachLine)
        eachLine.strip()
        match = re.search(r'^\@SQ\s*SN:([\w\.\-]+)\s.*LN:(\d+)', eachLine)
        if not match:
            continue
        chr = match.group(1)
        len = match.group(2)
        if len < min_len:
            continue
        chr_dict[chr] = len
    return chr_dict


def splitBam(bamfile, chr_dict, outdir="./"):
    splitPath = outdir + '/bam_split'
    os.system('rm -rf ' + splitPath) if os.path.isdir(splitPath) else None
    os.mkdir(splitPath) if not os.path.isdir(splitPath) else None
    cmd = ""
    for chr in chr_dict:
        cmd += "samtools view -b " + bamfile + " " + chr + " > " + splitPath + "/" + chr + ".bam && samtools index " + splitPath + "/" + chr + ".bam & \n"
    status, output = subprocess.getstatusoutput(cmd)
    if (int(status) != 0):  # it did not go well
        logging.debug("error in blast %s" % status)
        logging.debug("error detail: %s" % output)


def readTophatMapResult(resultdir, resultfile="align_summary.txt"):
    # Reads:
    #           Input     :  32675031
    #            Mapped   :  30323782 (92.8% of input)
    #             of these:   1049740 ( 3.5%) have multiple alignments (299770 have >2)
    # 92.8% overall read mapping rate.
    if not os.path.isfile(resultdir + '/' + resultfile):
        print('you don\'t have align_summary.txt ')
        return
    d = {}
    linenum = 0
    for line in open(resultdir + '/' + resultfile):
        linenum += 1
        line = line.strip()
        if linenum == 1 and line.startswith('Reads:'):
            continue
        if linenum == 2:
            match = re.search(r'\s*Input\s*:\s*(\d+)', line)
            if not match:
                continue
            d["input_data_count"] = int(match.group(1))
        if linenum == 3:
            match = re.search(r'\s*Mapped\s*:\s*(\d+)', line)
            if not match:
                continue
            d["total_mapped_reads_count"] = int(match.group(1))
        if linenum == 4:
            match = re.search(r'\s*of\s*these\s*:\s*(\d+)', line)
            if not match:
                d["multiple_mapped_reads_count"] = 0
                continue
            d["multiple_mapped_reads_count"] = int(match.group(1))

    d["uniq_mapped_reads_count"] = d["total_mapped_reads_count"] - d["multiple_mapped_reads_count"]
    d["total_mapped_persent"] = round(100 * float(d["total_mapped_reads_count"]) / d["input_data_count"], 2)
    d["uniq_mapped_persent"] = round(100 * float(d["uniq_mapped_reads_count"]) / d["total_mapped_reads_count"], 2)
    d["multiple_mapped_persent"] = round(100 * float(d["multiple_mapped_reads_count"]) / d["total_mapped_reads_count"], 2)

    report = ""
    report += "input reads:" + str(d["input_data_count"]) + "\n"
    report += "total mapped reads:" + str(d["total_mapped_reads_count"]) + "(" + str(d["total_mapped_persent"]) + "%)" + "\n"
    report += "uniq mapped reads:" + str(d["uniq_mapped_reads_count"]) + "(" + str(d["uniq_mapped_persent"]) + "%)" + "\n"
    report += "multiple mapped reads:" + str(d["multiple_mapped_reads_count"]) + "(" + str(d["multiple_mapped_persent"]) + "%)" + "\n"

    return d, report


def selectIndex(title, name):
    n = 0
    for item in title.strip().split('\t'):
        if item.lower() == name.lower():
            return n
        else:
            n += 1
    return -1


def selectIndexRe(title, rename):
    n = 0
    L = []
    rename = rename.lower()
    for item in title.strip().split('\t'):
        item = item.lower()
        if re.search(rename, item) is not None:
            L.append(n)
            n += 1
    return L


def getTitle(file):
    title = ""
    for line in open(file, "r"):
        line = line.strip()
        title = line
        return title


def to_bool(value):
    """
    Converts 'something' to boolean. Raises exception if it gets a string it doesn't handle.
    Case is ignored for strings. These string values are handled:
      True: 'True', "1", "TRue", "yes", "y", "t"
      False: "", "0", "faLse", "no", "n", "f"
    Non-string values are passed to bool.
    """
    if type(value) == type(''):
        if value.lower() in ("yes", "y", "true", "t", "1"):
            return True
        if value.lower() in ("no", "n", "false", "f", "0", ""):
            return False
        raise Exception('Invalid value for boolean conversion: ' + value)
    return bool(value)


def getCumulativeData(l):
    d = {}
    accumulative_value = 0
    for i in l:
        if d.has_key(i):
            d[i] += 1
        else:
            d[i] = 1
    for key in sorted(dict.keys(), key=float):
        accumulative_value += d[key]
        d[key] = accumulative_value

    for k in sorted(d.keys(), key=float):
        yield k, d[k]


def getCumulativeDataFromFile(file, n, outfile, keyname="key"):
    l = []
    for line in open(file):
        line = line.strip()
        if line.startswith('#'):
            continue
        temp = line.split('\t')

        if temp[n] == "-1" or temp[n] == keyname or float(temp[n]) == 0:
            # if temp[n]=="-1"    :
            continue
        l.append(temp[n])

    max_value = len(l)

    d = {}
    accumulative_value = 0
    for i in l:
        if i in d.keys():
            d[i] += 1
        else:
            d[i] = 1
    for key in sorted(d.keys(), key=float):
        accumulative_value += d[key]
        d[key] = accumulative_value

    with open(outfile, 'w') as o:
        o.writelines("+" + keyname + "\tpercent\taccumulative_value\n")
        o.writelines('0\t0.0\t0\n')
        for k in sorted(d.keys(), key=float):
            o.writelines(str(k) + '\t' + str(round(d[k] * 100 / max_value, 1)) + '\t' + str(d[k]) + '\n')


## 2016/2/4 Add by chengc
def cpfile(file, targetdir='./', targetfile='', deli='&&'):
    cmd = ''
    os.system('mkdir -p ' + targetdir)
    if not os.path.isfile(file):
        errormsg = "Warning: " + file + " is not exist for copy"
        cmd += "echo " + errormsg + deli
    else:
        cmd += 'cp ' + file + ' ' + targetdir + '/' + targetfile + deli
    return cmd


def cpdir(dir, targetdir='./', include='', exclude='', deli='&&', restr=""):
    cmd = ''
    os.system('mkdir -p ' + targetdir)
    if not os.path.isdir(dir):
        errormsg = "Warning: " + dir + " is not exist for copy"
        cmd += "echo " + errormsg + deli
    else:
        if include == '' and exclude == '':
            cmd += 'rsync -aL ' + dir + '/ ' + targetdir
            if re != "":
                for path in os.listdir(dir):
                    if os.path.isdir(dir+'/'+path):
                        newpathname = re.sub(restr+r'$', '', path)
                        if newpathname == path:
                            continue
                        cmd += '&& mv ' + targetdir + '/' + path + ' ' + targetdir + '/' + newpathname
            cmd += deli


        elif include == '' and exclude != '':
            cmd += 'rsync -aL'
            for pattern in exclude.split(','):
                cmd += ' --exclude="' + pattern + '"'
            cmd += ' ' + dir + '/ ' + targetdir
            if re != "":
                for path in os.listdir(dir):
                    if os.path.isdir(dir+'/'+path):
                        newpathname = re.sub(restr+r'$', '', path)
                        if newpathname == path:
                            continue
                        cmd += '&& mv ' + targetdir + '/' + path + ' ' + targetdir + '/' + newpathname
            cmd += deli
        elif include != '':
            cmd += 'rsync -aL '
            for pattern in include.split(','):
                cmd += ' --include="' + pattern + '"'
            cmd += ' --exclude="*" ' + dir + '/ ' + targetdir
            if re != "":
                for path in os.listdir(dir):
                    if os.path.isdir(dir+'/'+path):
                        newpathname = re.sub(restr+r'$', '', path)
                        if newpathname == path:
                            continue
                        cmd += '&& mv ' + targetdir + '/' + path + ' ' + targetdir + '/' + newpathname
            cmd += deli
    return cmd


# -----------------------------------------------------------------------------------
### E
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
### S
# -----------------------------------------------------------------------------------
def test():
    """this is test function"""
    pass

    ## splitBam Test
    # bamfile = "accepted_hits.bam"
    # if not os.path.isfile(bamfile + '.bai'):
    #     cmd = "samtools index " + bamfile
    #     status, output = subprocess.getstatusoutput(cmd)
    #     if (int(status) != 0):  # it did not go well
    #         logging.debug("error in blast %s" % status)
    #         logging.debug("error detail: %s" % output)
    # dict = readBamHeader(bamfile)
    # splitBam(bamfile,dict)

    ## readTophatMapResult Test
    # rdir = "/users/chengc/project/project_2015/antisense_RNA/reads/leaf_0409"
    # d, report = readTophatMapResult(rdir)
    # # print(d)
    # print(report)


if __name__ == '__main__':
    test()



    # -----------------------------------------------------------------------------------
    ### E
    # -----------------------------------------------------------------------------------
