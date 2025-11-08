import json
import os
import shutil
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    assert github_token, "GITHUB_TOKEN not found in .env file"

    # Get Copilot token and endpoints
    token_url = "https://api.github.com/copilot_internal/v2/token"
    headers = {"Authorization": f"token {github_token}", "editor-version": "vscode/1.97.2"}

    response = requests.get(token_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get Copilot token: {response.status_code} {response.text}")
        exit(1)

    token_data = response.json()
    copilot_token = token_data["token"]
    endpoints = token_data["endpoints"]

    print(f"Copilot token obtained: {copilot_token[:10]}...")
    print(f"Endpoints: {endpoints}")

    # Get models list
    models_url = endpoints["api"] + "/models"
    headers = {
        "Authorization": f"Bearer {copilot_token}",
        "Content-Type": "application/json",
        "editor-version": "vscode/1.97.2",
        "User-Agent": "VSCode/1.97.2",
    }

    response = requests.get(models_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get models: {response.status_code} {response.text}")
        exit(1)

    models_data = response.json()["data"]
    print("Models list fetched successfully. Saving to models.json...")
    Path("models.json").write_text(json.dumps(models_data, indent=2))
    print("Saved models.json")
    prettier_path = shutil.which("prettier")
    if prettier_path:
        print("Running prettier on models.json...")
        subprocess.check_call([prettier_path, "--write", "models.json"])
        print("Prettier formatting complete.")
    else:
        print("Prettier not found, skipping formatting.")


if __name__ == "__main__":
    main()
