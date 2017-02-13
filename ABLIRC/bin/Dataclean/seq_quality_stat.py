#!/usr/bin/env python2.7

"""
Simple sequencing file statistics.


Gather the following numbers:
    * Percentages of bases with quality at least Q40, Q30, and Q20 from FASTQ
      files.
    * Percentages of reads whose average quality is at least Q40, Q30, and Q20.

Requirements:
    * Python == 2.7.x
    * Biopython >= 1.60

Copyright (c) 2013 Wibowo Arindrarto <w.arindrarto@lumc.nl>
Copyright (c) 2013 LUMC Sequencing Analysis Support Core <sasc@lumc.nl>
MIT License <http://opensource.org/licenses/MIT>
"""

RELEASE = False
__version_info__ = ('0', '1',)
__version__ = '.'.join(__version_info__)
__version__ += '-dev' if not RELEASE else ''

import argparse
import json
import os
import sys

from Bio import SeqIO


# quality points we want to measure
# QVALS = range(0, 60, 10)
QVALS = (20,30)


def dict2json(d_input, f_out):
    """Dump the given dictionary as a JSON file."""
    if isinstance(f_out, str):
        target = open(f_out, 'w')
    else:
        target = f_out

    json.dump(d_input, target, sort_keys=True, indent=4,
              separators=(',', ': '))

    target.close()


def gather_stat(in_fastq, out_json, fmt):
    total_bases, total_reads = 0, 0

    bcntd = dict.fromkeys(QVALS, 0)
    rcntd = dict.fromkeys(QVALS, 0)

    for rec in SeqIO.parse(in_fastq, fmt):
        read_quals = rec.letter_annotations['phred_quality']
        read_len = len(read_quals)

        avg_qual = sum(read_quals) / len(read_quals)
        for qval in QVALS:
            bcntd[qval] += len([q for q in read_quals if q >= qval])
            if avg_qual >= qval:
                rcntd[qval] += 1

        total_bases += read_len
        total_reads += 1

    pctd = {
        'filename': os.path.abspath(in_fastq),
        'stats': {
            'bases': {},
            'reads': {},
        },
    }

    for qval in QVALS:
        key = 'Q' + str(qval)
        pctd['stats']['bases'][key] = 100.0 * bcntd[qval] / total_bases
        pctd['stats']['reads'][key] = 100.0 * rcntd[qval] / total_reads

    # dict2json(pctd, out_json)
    target = open(out_json, 'w')
    target.writelines("#name"+"\tQ20(bases):" + "\tQ30(bases):" + "\tQ20(reads):" + "\tQ30(reads):" + '\n')
    target.writelines(in_fastq+"\t"+str(round(pctd['stats']['bases']['Q20'],2))+"\t"+str(round(pctd['stats']['bases']['Q30'],2))+"\t"+str(round(pctd['stats']['reads']['Q20'],2))+"\t"+str(round(pctd['stats']['reads']['Q30'],2))+"\n")



if __name__ == '__main__':
    usage = __doc__.split('\n\n\n')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])

    parser.add_argument('--input', type=str, help='Path to input FASTQ file')
    parser.add_argument('-o', '--output', type=str, default=sys.stdout,
                        help='Path to output JSON file')
    parser.add_argument('--fmt', type=str, choices=['sanger', 'illumina',
                                                    'solexa'], default='sanger', help='FASTQ quality encoding')
    #sanger : 33
    #illumina : 64
    parser.add_argument('--version', action='version', version='%(prog)s ' +
                                                               __version__)

    args = parser.parse_args()

    # adjust format name to Biopython-compatible name
    fmt = 'fastq-' + args.fmt

    gather_stat(args.input, args.output, fmt)
