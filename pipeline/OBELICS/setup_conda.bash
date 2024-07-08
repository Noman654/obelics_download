#!/bin/bash

# Set the Miniconda version to download
MINICONDA_VERSION=latest
MINICONDA_OS=Linux
MINICONDA_ARCH=x86_64

# Construct the Miniconda download URL
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-${MINICONDA_OS}-${MINICONDA_ARCH}.sh"

# Download the Miniconda installer
echo "Downloading Miniconda installer from $MINICONDA_URL..."
wget $MINICONDA_URL -O Miniconda3-latest-Linux-x86_64.sh

# Make the installer executable
chmod +x Miniconda3-latest-Linux-x86_64.sh

# Run the installer
echo "Running the Miniconda installer..."
./Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda

# Initialize Conda
echo "Initializing Conda..."
source $HOME/miniconda/bin/activate
conda init

# Clean up the installer
rm Miniconda3-latest-Linux-x86_64.sh
conda create -n mm python=3.8 -y
conda activate mm
pip install -r requirements.txt
pip install datasets
echo "Miniconda installation is complete. Please restart your terminal or run 'source ~/.bashrc' to start using Conda."