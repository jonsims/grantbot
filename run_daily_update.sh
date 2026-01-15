#!/bin/bash
# Daily News Agent - Automated Runner
# Runs daily at 4am to generate and email the update

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the daily update (production mode)
python3 src/main_v2.py

# Log the execution
echo "$(date): Daily update generated" >> logs/automation.log