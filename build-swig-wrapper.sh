#!/usr/bin/env bash
set -e

sudo apt-get install -y swig build-essential python3-setuptools
git clone https://github.com/apertium/lttoolbox.git
cd lttoolbox
./autogen.sh --enable-python-bindings && make -j 4
cd python
python3 setup.py install

git clone https://github.com/apertium/apertium-lex-tools.git
cd apertium-lex-tools
./autogen.sh --enable-python-bindings && make -j 4
cd python
python3 setup.py install

git clone -b swig_wrapper https://github.com/Vaydheesh/apertium.git
cd apertium
./autogen.sh --enable-python-bindings && make -j 30
cd python
python3 setup.py install
