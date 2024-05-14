#!/bin/sh

USE_PYENV=$1

# Install build libraries
echo "############################################################"
echo "Installing python buildtool libraries..."
echo "############################################################"
#python3 -m pip install wheel check-wheel-contents --user
python3 -m pip install wheel check-wheel-contents

# Build wheel file
echo "\n############################################################"
echo "Building mdbaas wheel file from project code"
echo "############################################################"
python3 setup/setup.py bdist_wheel

# Check integrity of wheel file
WHEEL_FILE_PATH=$(ls -d -1 dist/** | tail -n 1)
echo "\n############################################################"
echo "\nChecking wheel file $WHEEL_FILE_PATH..."
echo "############################################################"
check-wheel-contents $WHEEL_FILE_PATH

# Install wheel file
echo "\n############################################################"
echo "\nInstalling wheel file..."
echo "############################################################"
#python3 -m pip install $WHEEL_FILE_PATH --force-reinstall --user
python3 -m pip install $WHEEL_FILE_PATH --force-reinstall