#!/bin/sh

# Use embedded virtualenv
REAL=`python -c 'import os,sys;print os.path.realpath(sys.argv[1])' "$0"`
cd $(dirname $REAL)


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


. venv/venv-py3/bin/activate
echo "Installing required libraries for virtual python3 env"
pip install -r install/requirements-py3.txt

# echo `python -V`



# echo `python -V`

# # if [ $(uname -s) = "Darwin" ]; then
# #     # Mac OS X Mountain Lion compiles with clang by default...
# #     # clang and cython don't get along... so force it to use gcc

# #     if [ "$(cc --version | grep -i clang)" != "" ]; then
# #         echo "Using GCC"
# #         export CC=/usr/bin/gcc
# #         export CXX=/usr/bin/g++
# #     fi
# # fi

# # PYTHONMAJOR=$($PYTHON -V 2>&1 | sed -e 's/\./ /g' | awk '{print $2}')
# # PYTHONMINOR=$($PYTHON -V 2>&1 | sed -e 's/\./ /g' | awk '{print $3}')

# # if [ "$PYTHONMAJOR" -ne 2 ]; then
# #     echo "Requires Python 2.6+"
# #     exit
# # fi
# # if [ "$PYTHONMINOR" -lt 6 ]; then
# #     echo "Requires Python 2.6+"
# #     exit
# # fi
# # if [ "$PYTHONMINOR" -eq 6 ]; then
# #     pip install unittest2
# # fi







