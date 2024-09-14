import os
import requests

# Set your Anthropic Claude API key
claude_api_key = 'your_claude_api_key'  # Replace with your Claude API key

# Function to send prompts to Claude AI
def send_to_claude(prompt):
    headers = {
        'Authorization': f'Bearer {claude_api_key}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': 'claude-1',  # Replace with your Claude model choice if needed
        'prompt': prompt,
        'max_tokens_to_sample': 1000,  # Adjust based on your needs
    }

    response = requests.post('https://api.anthropic.com/v1/complete', headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['completion']
    else:
        return f"Failed to retrieve response from Claude AI. Status code: {response.status_code}"

def get_github_repo_contents(owner, repo):
    # Initialize an array to store contents of all files
    all_files_contents = []

    # GitHub API URL for the repository contents
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = requests.get(url)

        # Check if the request was successful
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

def get_file_content(file_url):
    try:
        file_response = requests.get(file_url)

        if file_response.status_code == 200:
            return file_response.text
        else:
            return f"Failed to retrieve file content. Status code: {file_response.status_code}"

    except Exception as e:
        return f"An error occurred while fetching file content: {e}"

def explore_directory(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    subdirectory_contents = []

    try:
        response = requests.get(url)

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

def main():
    owner = "webrendhq"  # Replace with the GitHub user/organization
    repo = "WebRendNew"  # Replace with the repository name
    repo_contents = get_github_repo_contents(owner, repo)

    # Create a single prompt with all file contents
    prompt = "Here are the contents of the repository files:\n"
    for file_info in repo_contents:
        prompt += f"\n--- File: {file_info['filename']} ---\n"
        prompt += f"{file_info['content']}\n"

    # Send the consolidated content to Claude AI
    response = send_to_claude(prompt)
    print("\nClaude AI Response:\n", response)

    # Clear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Prompt the user
    while True:
        user_input = input("What do you need help with?\n")
        response = send_to_claude(user_input)
        print("\nClaude AI Response:\n", response)

if __name__ == "__main__":
    main()
