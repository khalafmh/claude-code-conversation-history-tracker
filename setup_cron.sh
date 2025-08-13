#!/bin/bash

# Setup cron job for Claude history sync
# This script adds a cron job to sync Claude conversation history every 3 hours

SCRIPT_DIR="/home/mahdi/Projects/claude-conversations"
PYTHON_PATH="/usr/bin/python3"
LOG_FILE="$SCRIPT_DIR/claude_history_json/sync.log"

# Create the cron job entry
CRON_JOB="0 */3 * * * cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_DIR/export_claude_history.py --sync-all >> $SCRIPT_DIR/claude_history_json/sync.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "export_claude_history.py --sync-all" > /dev/null; then
    echo "Cron job already exists. Removing old entry..."
    # Remove existing entry
    (crontab -l 2>/dev/null | grep -v "export_claude_history.py --sync-all") | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job successfully added!"
echo ""
echo "The following cron job has been set up:"
echo "$CRON_JOB"
echo ""
echo "This will:"
echo "  - Run every 3 hours (at minute 0)"
echo "  - Change to directory: $SCRIPT_DIR"
echo "  - Execute: python3 export_claude_history.py --sync-all"
echo "  - Log output to: $SCRIPT_DIR/claude_history_json/sync.log"
echo ""
echo "To view current cron jobs, run: crontab -l"
echo "To remove this cron job, run: crontab -e and delete the line"
echo "To view sync logs, run: tail -f $SCRIPT_DIR/claude_history_json/sync.log"