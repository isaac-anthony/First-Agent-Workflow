#!/bin/bash
# Brine.ai Daily Agent Wrapper Script
# This script is called by the Mac Launch Agent

# 1. Navigate to the project directory
cd "/Users/isaacgutierrez/Cursor/Agent Workflow"

# 2. Add execution folder to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/execution

# 3. Run the orchestrator with the Multi-Niche Config
# We use the config/targets.json file to drive the campaigns
/usr/bin/python3 execution/orchestrate_maps_workflow.py "config/targets.json" >> automation.log 2>&1
