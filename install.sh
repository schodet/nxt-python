#!/bin/bash -e

echo "This builds nxt-python for Python 3"
echo "and installs it to the user's home directory."
echo "Root is not required."
echo ""

rm -Rf ~/.local/lib/python3.4/site-packages/nxt
rm -Rf ~/.local/lib/python2.7/site-packages/nxt # should not be needed
python3 setup.py install --user
