#!/bin/sh

if [ "$PYTHON" = "" ]; then
    PYTHON="python"
fi

# PYTHON=`cat`

# Use embedded virtualenv
REAL=`python -c 'import os,sys;print os.path.realpath(sys.argv[1])' "$0"`
echo $REAL
