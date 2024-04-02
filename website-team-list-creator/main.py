import pandas as pd
import json
import os
import shutil
import subprocess
import datetime

def main():
  """
  Reads data from an Excel file, processes it, and generates a JSON file with team details.

  This function reads data from the 'Website-Content.xlsx' file located in the './website-team-list-creator/' directory.
  It processes the data, creates a dictionary of team details, and saves it as 'team_details.json' in the same directory.

  Returns:
    None
  """
  repository = "https://github.com/George-Madeley/BWB-Website.git"

  # Read the team details from the 'team_details.json' file
  data = readJSON()
  createJSON()
  # gitClone(repository)

def readJSON():
  """
  Reads the 'team_details.json' file and returns the data as a dictionary.

  Returns:
    dict: A dictionary containing team details.
  """
  # Check if the 'team_details.json' file exists
  if not os.path.exists("team_details.json"):
    print("Error: 'team_details.json' file not found")
    return

  existingMembers = []
  existingEmails = []
  with open("team_details.json", "r") as jsonFile:
    data = json.load(jsonFile)
    # Get a lsit of existing members
    for team in data:
      for member in data[team]:
        email = member.get('email', '')
        if email == '':
          raise KeyError(f'Key "email" does not exist')
        if email in existingEmails:
          continue
        else:
          existingEmails.append(email)
          existingMembers.append(member)

  return existingMembers

def createJSON(prevMembers: dict = None):
    df = pd.read_excel("./Website-Content.xlsx")
    df.fillna("", inplace=True)

    members, memberEmails = createMembersList(df)
    addPreviousMembers(prevMembers, members, memberEmails)
    jsonData = formatJSON(members)

    with open("./team_details.json", "w") as jsonFile:
      json.dump(jsonData, jsonFile, indent=4)

def createMembersList(df):
    members = []
    memberEmails = []
    for index, row in df.iterrows():
      renameImage(row)
      member = createMember(row)
      members.append(member)
      email = member.get('email', '')
      memberEmails.append(email)
    return members, memberEmails

def addPreviousMembers(prevMembers, members, memberEmails):
    if prevMembers is not None:
      for prevMember in prevMembers:
        email = prevMember.get(email, '')
        if email == '':
          raise KeyError(f'Key "email" does not exist')
        
        if email not in memberEmails:
          members.append(prevMember)
          memberEmails.append(email)

def formatJSON(members):
    jsonData = {
      "Management": [],
      "Hardware": [],
      "Sensors": [],
      "Software": [],
      "Finance": [],
      "Outreach": [],
      "Social": []
    }

    counter = 0
    for member in members:
      teams = getMemberTeams(member)
      for team in teams:
        memberCopy = member.copy()
        memberCopy['id'] = counter
        jsonData[team].append(memberCopy)
        counter += 1
    return jsonData

def getMemberTeams(member):
  roles = member.get('roles', [])
  teams = []
  for role in roles:
    team = role.get('team')
    teams.append(team)
  return teams

def createMember(row):
  """
  Create a member dictionary from a given row of data.

  Args:
    row (pandas.Series): A row of data containing member information.

  Returns:
    tuple: A tuple containing the member dictionary and a list of teams.

  Raises:
    ValueError: If a role is empty for a team.

  """
  member = {
    "id": 0,
    "name": row["Name"],
    "email": row["Email"],
    "course": row["Course"],
    "link": row["Link"],
    "description": row["Description"],
    "image": row["Image"],
    "startYear": row["Join Date"].year,
    "endYear": datetime.datetime.now().year,
    "legacy": True if row["Legacy"] == "Yes" else False,
    "isLegacy": row["Leave Date"] < pd.Timestamp.now(),
    "roles": []
  }

  teams = row["Teams"]
  teams = teams.split(";")

  for team in teams:
    if row[f"{team} Role"] == "":
      raise ValueError(f"Role for {team} is empty for {row['Name']}")
    role = {
      "role": row[f"{team} Role"],
      "team": team,
      "lead": isLead(row[f"{team} Role"]),
    }
    member['roles'].append(role)
  return member

def renameImage(row):
  """
  Renames the image file associated with a given row in the team list.

  Args:
    row (dict): A dictionary representing a row in the team list.

  Returns:
    None
  """
  email = row["Email"]
  username = email.split("@")[0]
  oldImage = row["Image"].split("/")[-1].replace("%20", " ")
  fileExists = os.path.exists(
    f"./images/{oldImage}"
  )
  if not fileExists:
    print(f"Image {oldImage} does not exist for {row['Name']}")

  if oldImage != "" and fileExists:
    suffix = oldImage.split(".")[-1]
    newImage = f"{username}.{suffix.lower()}"
    os.rename(
      f"./images/{oldImage}",
      f"./images/{newImage}"
    )
    row["Image"] = newImage

def isLead(role):
  """
  Checks if the given role is a lead role.

  Args:
    role (str): The role to check.

  Returns:
    bool: True if the role is a lead role, False otherwise.
  """
  if isinstance(role, str) and "Head of" in role:
    return True
  return False

def gitClone(repository: str) -> None:
  """
  Clones the given git repository into the repository directory
  
  Params:
    repository: The GitHub repository HTTP address
  """

  print("Cloning the repository...")

  # git clone the given repository
  os.system(f"git clone --depth 1 {repository} repository")

  # Check if the repository was cloned successfully
  if not os.path.exists("repository"):
    print("Error: Repository not cloned successfully")
    return
  
  print("Repository cloned successfully")
  print("Updating team details...")

  # Move the contents of the images folder to the images folder in the repository
  imageDir = os.path.join("repository", "src", "content", "images")
  os.makedirs(imageDir, exist_ok=True)
  shutil.move("images", os.path.join("repository", "src", "content", "images"))

  # Move the team_details.json file to the repository
  try:
    # Add the changes to the repository
    subprocess.run(["git", "add", "."])

    # Commit the changes
    subprocess.run(["git", "commit", "-m", "Updated team details"])

    # Push the changes to the repository
    subprocess.run(["git", "push"])

    print("Changes pushed successfully")
    print("Deleting the repository...")
  except Exception as e:
    print("Error occurred while pushing changes:", str(e))

  # Change directory back to the original directory
  os.chdir("..")

  # Remove the repository directory
  os.system("rm -rf repository")

  print("Repository deleted successfully")

if __name__ == "__main__":
  main()
