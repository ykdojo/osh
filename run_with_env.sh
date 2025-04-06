#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo ".env file not found!"
    exit 1
fi

# Toggle comments on lines 3 and 4
awk '{
    if (NR == 3 || NR == 4) {
        if ($0 ~ /^#/) {
            print substr($0, 2)
        } else {
            print "#" $0
        }
    } else {
        print $0
    }
}' .env > .env.tmp && mv .env.tmp .env

# Run the clipboard to LLM script
bash run_clipboard_to_llm.sh