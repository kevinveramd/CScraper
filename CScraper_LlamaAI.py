import os
import requests
from git import Repo
from transformers import pipeline
import time

# Use environment variables for sensitive information
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "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")
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN", "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")

# Set up the Hugging Face token
os.environ["HUGGINGFACE_TOKEN"] = HUGGINGFACE_TOKEN

# Initialize GPT-2 model using Hugging Face transformers library
# Explicitly use CPU and a smaller model to avoid memory issues
try:
    model = pipeline('text-generation', model='distilgpt2', device='cpu')
except Exception as e:
    print(f"Failed to initialize the model: {e}")
    model = None

# GitHub API configuration
GITHUB_API_HEADERS = {
    'Authorization': f'token {GITHUB_API_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def send_to_model(prompt):
    if model is None:
        print("Model not initialized. Skipping text generation.")
        return
    try:
        # Generate text using the model, but ignore the output
        _ = model(prompt, max_length=100, num_return_sequences=1, truncation=True)
    except Exception as e:
        print(f"Failed to send prompt to the model. Error: {e}")

def get_github_repo_contents(owner, repo):
    all_files_contents = []
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = requests.get(url, headers=GITHUB_API_HEADERS)
        response.raise_for_status()
        contents = response.json()
        for item in contents:
            if item['type'] == 'file' and not item['name'].startswith('.'):
                print(f"\nFetching content of file: {item['path']}")
                file_content = get_file_content(item['download_url'])
                all_files_contents.append({'filename': item['path'], 'content': file_content})
            elif item['type'] == 'dir':
                print(f"\nExploring directory: {item['path']}")
                subdirectory_contents = explore_directory(owner, repo, item['path'])
                all_files_contents.extend(subdirectory_contents)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching repository contents: {e}")

    return all_files_contents

def get_file_content(file_url):
    try:
        file_response = requests.get(file_url)
        file_response.raise_for_status()
        return file_response.text
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching file content: {e}"

def explore_directory(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    subdirectory_contents = []

    try:
        response = requests.get(url, headers=GITHUB_API_HEADERS)
        response.raise_for_status()
        contents = response.json()
        for item in contents:
            if item['type'] == 'file' and not item['name'].startswith('.'):
                print(f"\nFetching content of file: {item['path']}")
                file_content = get_file_content(item['download_url'])
                subdirectory_contents.append({'filename': item['path'], 'content': file_content})
            elif item['type'] == 'dir':
                print(f"\nExploring subdirectory: {item['path']}")
                subdirectory_contents.extend(explore_directory(owner, repo, item['path']))
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return subdirectory_contents

def create_file_or_folder(repo_path, path, is_folder=False):
    full_path = os.path.join(repo_path, path)
    try:
        if is_folder:
            os.makedirs(full_path, exist_ok=True)
            print(f"Folder created: {full_path}")
        else:
            with open(full_path, 'w') as f:
                f.write('')
            print(f"File created: {full_path}")
    except Exception as e:
        print(f"Error creating {'folder' if is_folder else 'file'}: {e}")

def commit_and_push_changes(repo_path, file_path, commit_message):
    try:
        repo = Repo(repo_path)
        repo.git.add(file_path)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        print("Changes committed and pushed successfully.")
    except Exception as e:
        print(f"Error committing and pushing changes: {e}")

def main():
    owner = "webrendhq"
    repo = "Test-Repo-for-CScraper"
    local_repo_path = "/Documents/Github/Test-Repo-for-CScraper"  # Replace with your actual local repo path

    while True:
        try:
            repo_contents = get_github_repo_contents(owner, repo)
            prompt = "Here are the contents of the repository files:\n"
            for file_info in repo_contents:
                prompt += f"\n--- File: {file_info['filename']} ---\n"
                prompt += f"{file_info['content'][:500]}...\n"  # Limit content to avoid memory issues

            send_to_model(prompt)

            print("Repository contents fetched successfully.")
            user_input = input("What would you like to change? (Type 'exit' or 'done' to finish)\n")
            
            if user_input.lower() in ["exit", "done"]:
                print("Exiting...")
                break

            if "create folder" in user_input.lower():
                folder_path = input("Enter the folder path to create: ")
                create_file_or_folder(local_repo_path, folder_path, is_folder=True)
            elif "create file" in user_input.lower():
                file_path = input("Enter the file path to create: ")
                create_file_or_folder(local_repo_path, file_path)
            elif "commit" in user_input.lower():
                file_path = input("Enter the file path to commit: ")
                content = input("Enter the new content for the file: ")
                commit_message = input("Enter the commit message: ")

                full_file_path = os.path.join(local_repo_path, file_path)
                with open(full_file_path, 'w') as f:
                    f.write(content)

                commit_and_push_changes(local_repo_path, file_path, commit_message)

            send_to_model(user_input)

            time.sleep(1)  # Add a small delay to avoid overwhelming the API
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()