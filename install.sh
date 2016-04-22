#!/bin/bash

echo "This builds nxt-python for Python 3"
echo "and installs it to the user's home directory."
echo "Root is not required."
echo ""

rm -Rf ~/.local/lib/python3.*/site-packages/nxt
python3 setup.py install --user
