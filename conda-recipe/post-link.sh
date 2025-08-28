#!/bin/bash
# Post-link script to install pip dependencies

# Install pip dependencies that are not available in conda
$PREFIX/bin/pip install pystac-client>=0.7.0 planetary-computer>=0.5.0
