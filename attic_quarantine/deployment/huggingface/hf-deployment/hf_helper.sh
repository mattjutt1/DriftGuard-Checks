#!/bin/bash
# HuggingFace helper script for future deployments

# Load HF credentials
source /home/matt/prompt-wizard/.env.hf

# Function to push updates to HF Space
push_to_hf() {
    echo "Pushing changes to HuggingFace Space..."
    export HF_TOKEN=$HF_TOKEN
    
    # Activate venv if not already active
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source /home/matt/prompt-wizard/hf-deployment/venv/bin/activate
    fi
    
    python /home/matt/prompt-wizard/hf-deployment/upload_to_hf.py
}

# Function to test HF Space status
test_hf() {
    echo "Testing HuggingFace Space status..."
    python /home/matt/prompt-wizard/test_hf_space.py
}

# Function to view HF Space logs
view_logs() {
    echo "Opening HF Space logs in browser..."
    echo "URL: https://huggingface.co/spaces/$HF_SPACE_REPO/logs"
}

# Main menu
case "$1" in
    push)
        push_to_hf
        ;;
    test)
        test_hf
        ;;
    logs)
        view_logs
        ;;
    *)
        echo "Usage: ./hf_helper.sh [push|test|logs]"
        echo "  push - Push current changes to HF Space"
        echo "  test - Test if HF Space is working"
        echo "  logs - Show URL for HF Space logs"
        ;;
esac