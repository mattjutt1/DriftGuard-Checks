#!/usr/bin/env python3
"""Upload files to HuggingFace Space using the API"""

from huggingface_hub import HfApi, CommitOperationAdd
import os

# Initialize API (will use token from environment or prompt)
api = HfApi()

# Space details
repo_id = "unfiltrdfreedom/prompt-evolver"
repo_type = "space"

# Files to upload
files_to_upload = [
    ("requirements.txt", "requirements.txt"),
    ("app.py", "app.py")
]

print("Uploading files to HuggingFace Space...")
print(f"Space: {repo_id}")
print("-" * 50)

try:
    # Create operations for each file
    operations = []
    for local_path, repo_path in files_to_upload:
        if os.path.exists(local_path):
            print(f"Adding {local_path} -> {repo_path}")
            with open(local_path, "rb") as f:
                operations.append(
                    CommitOperationAdd(
                        path_in_repo=repo_path,
                        path_or_fileobj=f.read()
                    )
                )
        else:
            print(f"Warning: {local_path} not found")
    
    if operations:
        # Commit all files
        print("\nCommitting changes...")
        commit_info = api.create_commit(
            repo_id=repo_id,
            repo_type=repo_type,
            operations=operations,
            commit_message="Fix: Update requirements.txt to fix transformers import issue"
        )
        print(f"✅ Success! Commit: {commit_info}")
        print(f"\nSpace URL: https://huggingface.co/spaces/{repo_id}")
        print(f"Live URL: https://unfiltrdfreedom-prompt-evolver.hf.space")
    else:
        print("No files to upload")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nYou need to set your HuggingFace token:")
    print("1. Get your token from: https://huggingface.co/settings/tokens")
    print("2. Run: export HF_TOKEN='your_token_here'")
    print("3. Run this script again")