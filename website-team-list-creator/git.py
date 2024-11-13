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

  # git clone the given repository
  os.system(f"git clone {repository} repository")

  # Check if the repository was cloned successfully
  if not os.path.exists("repository"):
    print("Error: Repository not cloned successfully")
    return

  print("Repository cloned successfully")


def gitBranch(branchName: str) -> None:
  """
  Create and push a new branch to the remote repository.

  Params:
    branchName (str): The name of the new branch.

  Returns:
    None
  """

  # Change directory to the repository
  os.chdir("repository")

  # Create a new branch
  os.system(f"git checkout -b {branchName}")

  # Push the branch to the origin
  os.system(f"git push --set-upstream origin {branchName}")

  # Change directory back to the original directory
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

  This function changes the directory to the repository, adds the changes to the repository,
  commits the changes with a message, and pushes the changes to the remote repository.

  Raises:
    Exception: If an error occurs while pushing the changes.

  """
  try:
    # Change directory to the repository
    os.chdir("repository")

    # Add the changes to the repository
    subprocess.run(["git", "add", "."])

    # Commit the changes
    subprocess.run(["git", "commit", "-m", "Updated team details"])

    # Push the changes to the repository
    subprocess.run(["git", "push"])

    print("Changes pushed successfully")
  except Exception as e:
    print("Error occurred while pushing changes:", str(e))


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
  os.system("rm -rf repository")

  print("Repository deleted successfully")