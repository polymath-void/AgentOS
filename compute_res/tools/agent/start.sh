#!/bin/bash
# Agent launch script

clear

# Print animated colored Polymath header
echo -e "\e[1;36m"
echo "  ____       _                       _   _    "
sleep 0.1
echo " |  _ \ ___ | |_   _ _ __ ___   __ _| |_| |__ "
sleep 0.1
echo " | |_) / _ \| | | | | '_ \` _ \ / _\` | __| '_ \\"
sleep 0.1
echo " |  __/ (_) | | |_| | | | | | | (_| | |_| | | "
sleep 0.1
echo " |_|   \___/|_|\__, |_| |_| |_|\__,_|\__|_| |_"
sleep 0.1
echo "               |___/                          "
echo -e "\e[0m"
sleep 0.5

# Start the context daemon in background if port 8080 is not listening
if ! python3 -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8080))" 2>/dev/null; then
    echo "Starting Context Daemon in the background..."
    python3 "$(dirname "$0")/context_daemon.py" > "$(dirname "$0")/daemon_stdout.log" 2>&1 &
    # Wait for daemon to spin up
    for i in {1..10}; do
        if python3 -c "import socket; s = socket.socket(); s.connect(('127.0.0.1', 8080))" 2>/dev/null; then
            break
        fi
        sleep 0.5
    done
fi

# Launch the agent
$(dirname "$0")/target/release/polymath-void-agent
