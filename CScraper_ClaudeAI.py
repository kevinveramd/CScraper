import os
import requests
from git import Repo

# Set your Anthropic Claude API key
claude_api_key = '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'  # Replace with your Claude API key

# Hard-coded GitHub API token for demonstration purposes
GITHUB_API_TOKEN = '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'  # Replace with your GitHub API token
GITHUB_API_HEADERS = {
    'Authorization': f'token {GITHUB_API_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Function to send prompts to Claude AI
def send_to_claude(prompt):
    headers = {
        'Authorization': f'Bearer {claude_api_key}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': 'claude-2',  # Make sure this is the correct model name
        'prompt': prompt,
        'max_tokens_to_sample': 1000,  # Adjust based on your needs
    }

    try:
        response = requests.post('https://api.anthropic.com/v1/complete', headers=headers, json=data)
        response.raise_for_status()  # This will raise an error for 4xx/5xx responses
        return response.json().get('completion', "No completion received from Claude AI.")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "Authentication failed. Check your API key."
        else:
            return f"Failed to retrieve response from Claude AI. Error: {e}"
    except requests.exceptions.RequestException as e:
        return f"Failed to retrieve response from Claude AI. Error: {e}"

# Function to get the contents of the GitHub repository
def get_github_repo_contents(owner, repo):
    all_files_contents = []
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = requests.get(url, headers=GITHUB_API_HEADERS)
        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item['type'] == 'file':
                    print(f"\nFetching content of file: {item['path']}")
                    file_content = get_file_content(item['download_url'])
                    all_files_contents.append({'filename': item['path'], 'content': file_content})
                elif item['type'] == 'dir':
                    print(f"\nExploring directory: {item['path']}")
                    subdirectory_contents = explore_directory(owner, repo, item['path'])
                    all_files_contents.extend(subdirectory_contents)
        else:
            print(f"Failed to retrieve repository contents. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return all_files_contents

# Function to get the content of a file
def get_file_content(file_url):
    try:
        file_response = requests.get(file_url)
        if file_response.status_code == 200:
            return file_response.text
        else:
            return f"Failed to retrieve file content. Status code: {file_response.status_code}"
    except Exception as e:
        return f"An error occurred while fetching file content: {e}"

# Function to explore directories recursively
def explore_directory(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    subdirectory_contents = []

    try:
        response = requests.get(url, headers=GITHUB_API_HEADERS)
        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item['type'] == 'file':
                    print(f"\nFetching content of file: {item['path']}")
                    file_content = get_file_content(item['download_url'])
                    subdirectory_contents.append({'filename': item['path'], 'content': file_content})
                elif item['type'] == 'dir':
                    print(f"\nExploring subdirectory: {item['path']}")
                    subdirectory_contents.extend(explore_directory(owner, repo, item['path']))
        else:
            print(f"Failed to retrieve directory contents. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return subdirectory_contents

# Function to commit and push changes using GitPython
def commit_and_push_changes(local_repo_path, file_path, commit_message):
    try:
        # Initialize the repo
        repo = Repo(local_repo_path)

        # Stage the file for commit
        repo.index.add([file_path])

        # Commit the changes
        repo.index.commit(commit_message)

        # Push the changes
        origin = repo.remote(name='origin')
        push_info = origin.push()

        # Check for push errors
        for info in push_info:
            if info.flags & info.ERROR:
                print(f"Error pushing to remote: {info.summary}")
            else:
                print(f"Successfully committed and pushed changes: {commit_message}")
    except Exception as e:
        print(f"An error occurred while committing and pushing changes: {e}")

# Function to handle file and folder creation
def create_file_or_folder(local_repo_path, path, is_folder=False):
    try:
        full_path = os.path.join(local_repo_path, path)
        if is_folder:
            os.makedirs(full_path, exist_ok=True)
            print(f"Folder created: {full_path}")
        else:
            folder_path = os.path.dirname(full_path)
            os.makedirs(folder_path, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("")  # Creates an empty file
            print(f"File created: {full_path}")
    except Exception as e:
        print(f"An error occurred while creating file or folder: {e}")

def main():
    owner = "webrendhq"  # Replace with the GitHub user/organization
    repo = "Test-Repo-for-CScraper"  # Replace with the repository name
    local_repo_path = "/Documents/Github/Test-Repo-for-CScraper"  # Replace with the path to your local repo

    while True:
        # Retrieve and send the current repo contents to Claude AI
        repo_contents = get_github_repo_contents(owner, repo)
        prompt = "Here are the contents of the repository files:\n"
        for file_info in repo_contents:
            prompt += f"\n--- File: {file_info['filename']} ---\n"
            prompt += f"{file_info['content']}\n"

        # Send the consolidated content to Claude AI
        response = send_to_claude(prompt)
        print("\nClaude AI Response:\n", response)

        # Clear the terminal
        # os.system('cls' if os.name == 'nt' else 'clear')

        # Ask user for input on what they want to change
        print(prompt)
        user_input = input("What would you like to change? (Type 'exit' or 'done' to finish)\n")
        
        if user_input.lower() in ["exit", "done"]:
            print("Exiting...")
            break

        # Check if user wants to create a new file or folder
        if "create folder" in user_input.lower():
            folder_path = input("Enter the folder path to create: ")
            create_file_or_folder(local_repo_path, folder_path, is_folder=True)
        elif "create file" in user_input.lower():
            file_path = input("Enter the file path to create: ")
            create_file_or_folder(local_repo_path, file_path)

        # Send user input to Claude AI for further processing
        response = send_to_claude(user_input)
        print("\nClaude AI Response:\n", response)

        # Ask if the user wants to commit changes
        if "commit" in user_input.lower():
            file_path = input("Enter the file path to commit: ")
            content = input("Enter the new content for the file: ")
            commit_message = input("Enter the commit message: ")

            # Write new content to the file
            with open(file_path, 'w') as f:
                f.write(content)

            # Commit and push the changes
            commit_and_push_changes(local_repo_path, file_path, commit_message)

if __name__ == "__main__":
    main()
