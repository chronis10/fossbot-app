#!/bin/bash

# Define the path to CoppeliaSim installation
COPPELIA_PATH="$HOME/CoppeliaSim_Edu_V4_6_0_rev16_Ubuntu20_04/coppeliaSim.sh"

# Change to the current directory or specify the directory where your Lua script and scene file are located
CUR_PATH=$(pwd)
echo $CUR_PATH

# Run the fossbot-app (ensure it is executable and the path is correct)
./fossbot-app &

# Start CoppeliaSim with specified Lua script and scene file
"$COPPELIA_PATH" -h -a "$CUR_PATH/coppelia/stream.lua"  -f "$CUR_PATH/coppelia/default.ttt"

# Script ends
exit