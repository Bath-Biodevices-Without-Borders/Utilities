import os
import shutil
import subprocess

def syncData(repository: str) -> None:
  """
  Clones the given git repository into the repository directory

  Params:
    repository (str): The GitHub repository HTTP address
  """

  gitClone(repository)
  gitBranch("update-team-details")
  moveDataToRepo()
  gitPush()
  deleteRepo()


def gitClone(repository: str) -> None:
    print("Cloning the repository...")

    # Remove the repository directory if it exists
    if os.path.exists("repository"):
        shutil.rmtree("repository", ignore_errors=True)

    # git clone the given repository
    result = subprocess.run(f"git clone {repository} repository", shell=True)
    if result.returncode != 0:
        print("Error: Repository not cloned successfully")
        exit(1)

    # Check if the repository was cloned successfully and is a git repo
    if not os.path.exists("repository/.git"):
        print("Error: 'repository' is not a valid git repository")
        exit(1)

    print("Repository cloned successfully")


def gitBranch(branchName: str) -> None:
    """
    Create and push a new branch to the remote repository if it doesn't exist.
    If the branch exists remotely, check it out and pull the latest changes.
    """
    os.chdir("repository")

    # Fetch all branches
    subprocess.run(["git", "fetch"], check=True)

    # Check if branch exists locally
    branches = subprocess.run(["git", "branch"], capture_output=True, text=True)
    if branchName not in branches.stdout:
        # Check if branch exists remotely
        remote_branches = subprocess.run(["git", "branch", "-r"], capture_output=True, text=True)
        if f"origin/{branchName}" in remote_branches.stdout:
            subprocess.run(["git", "checkout", branchName], check=True)
            subprocess.run(["git", "pull", "origin", branchName], check=True)
        else:
            subprocess.run(["git", "checkout", "-b", branchName], check=True)
            subprocess.run(["git", "push", "--set-upstream", "origin", branchName], check=True)
    else:
        subprocess.run(["git", "checkout", branchName], check=True)
        subprocess.run(["git", "pull", "origin", branchName], check=True)

    os.chdir("..")

def moveDataToRepo() -> None:
  """
  Moves the team details data and images to the repository.

  This function moves the contents of the 'images' folder to the 'images' folder in the repository,
  and moves the 'team_details.json' file to the 'src/content' folder in the repository.

  Note: This function assumes that the 'images' folder and 'team_details.json' file exist in the current directory.

  """
  print("Updating team details...")

  # Move the contents of the images folder to the images folder in the
  # repository
  imageDir = os.path.join("repository", "src", "images", "team_profiles")
  os.makedirs(imageDir, exist_ok=True)
  shutil.copytree("images", imageDir, dirs_exist_ok=True)

  # Move the team_details.json file to the repository
  jsonFilepath = os.path.join(
      "repository",
      "src",
      "content",
      "team_details.json")
 

  os.remove(jsonFilepath)
  shutil.copy("team_details.json", jsonFilepath)


def gitPush() -> None:
    """
    Pushes the changes made in the local repository to the remote repository.
    Handles rejected pushes by pulling remote changes and retrying.
    """
    original_dir = os.getcwd()
    try:
        os.chdir("repository")

        # Add the changes to the repository
        subprocess.run(["git", "add", "."], check=True)

        # Check if there are changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            print("Nothing to commit, working tree clean")
        else:
            # Commit the changes
            subprocess.run(["git", "commit", "-m", "Updated team details"], check=True)

        # Push the changes to the repository
        push = subprocess.run(["git", "push"], capture_output=True, text=True)
        if push.returncode != 0 and "fetch first" in push.stderr:
            print("Push rejected, attempting to pull and re-push...")
            subprocess.run(["git", "pull", "--rebase"], check=True)
            subprocess.run(["git", "push"], check=True)
        elif push.returncode != 0:
            print("Error occurred while pushing changes:", push.stderr)
        else:
            print("Changes pushed successfully")
    except Exception as e:
        print("Error occurred while pushing changes:", str(e))
    finally:
        os.chdir(original_dir)


def deleteRepo() -> None:
  """
  Deletes the repository directory.

  This function changes the current directory back to the original directory,
  removes the repository directory using the `rm -rf` command, and prints a
  success message when the repository is deleted successfully.
  """
  print("Deleting the repository...")

  # Change directory back to the original directory
  os.chdir("..")

  # Remove the repository directory
  #os.system("rm -rf repository")
  #windows version
  shutil.rmtree("repository", ignore_errors=True)

  print("Repository deleted successfully")