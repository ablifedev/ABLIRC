#!/bin/sh

# Use embedded virtualenv
REAL=`python -c 'import os,sys;print os.path.realpath(sys.argv[1])' "$0"`
cd $(dirname $REAL)

# Check required software
type perl >/dev/null 2>&1 || { echo >&2 "perl is required but it's not installed."; }
type R >/dev/null 2>&1 || { echo >&2 "R is required but it's not installed."; }
type tophat2 >/dev/null 2>&1 || { echo >&2 "tophat2 is required but it's not installed."; }
type samtools >/dev/null 2>&1 || { echo >&2 "samtools is required but it's not installed."; }
type bowtie2 >/dev/null 2>&1 || { echo >&2 "bowtie2 is required but it's not installed."; }
type bedtools >/dev/null 2>&1 || { echo >&2 "bedtools is required but it's not installed."; }
type fastq_quality_filter >/dev/null 2>&1 || { echo >&2 "fastq_quality_filter is required but it's not installed."; }
type findMotifs.pl >/dev/null 2>&1 || { echo >&2 "Homer is required but it's not installed."; }

# Check python2 and python3 path
PYTHON2=`head -1 $(dirname $REAL)/install/python2_path`
PYTHON3=`head -1 $(dirname $REAL)/install/python3_path`

echo $PYTHON2
echo $PYTHON3

if [ ! -e venv/venv-py2 ]; then
    echo "Initializing virtualenv folder (venv-py2)"
    VIRTUALENV="$PYTHON2 $(dirname $REAL)/venv/virtualenv_embedded/virtualenv.py"
    $VIRTUALENV --no-site-packages venv/venv-py2
fi

if [ ! -e venv/venv-py3 ]; then
    echo "Initializing virtualenv folder (venv-py3)"
    VIRTUALENV="$PYTHON3 $(dirname $REAL)/venv/virtualenv_embedded/virtualenv.py"
    $VIRTUALENV --no-site-packages venv/venv-py3
fi

. venv/venv-py2/bin/activate
echo "Installing required libraries for virtual python2 env"
pip install numpy
pip install -r install/requirements-py2.txt

rm -rf venv/venv-py2/lib/python2.*/site-packages/gffutils
cp -r install/external_lib/gffutils venv/venv-py2/lib/python2.*/site-packages/

rm -rf venv/venv-py2/lib/python2.*/site-packages/HTSeq*
cp -r install/external_lib/HTSeq venv/venv-py2/lib/python2.*/site-packages/

. venv/venv-py3/bin/activate
echo "Installing required libraries for virtual python3 env"
pip install -r install/requirements-py3.txt


# install R packages automatically if delete the comments
# Rscript install/requirements-R.r
