import requests

def get_github_repo_contents(owner, repo):
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
                    print(file_content)

                elif item['type'] == 'dir':
                    print(f"\nExploring directory: {item['path']}")
                    explore_directory(owner, repo, item['path'])

        else:
            print(f"Failed to retrieve repository contents. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

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
    try:
        response = requests.get(url)

        if response.status_code == 200:
            contents = response.json()

            for item in contents:
                if item['type'] == 'file':
                    print(f"\nFetching content of file: {item['path']}")
                    file_content = get_file_content(item['download_url'])
                    print(file_content)

                elif item['type'] == 'dir':
                    print(f"\nExploring subdirectory: {item['path']}")
                    explore_directory(owner, repo, item['path'])

        else:
            print(f"Failed to retrieve directory contents. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    owner = "octocat"  # Replace with the GitHub user/organization
    repo = "Hello-World"  # Replace with the repository name
    get_github_repo_contents(owner, repo)
