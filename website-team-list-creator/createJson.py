import os
import json
import pandas as pd
import datetime
from PIL import Image

def main():
  """
  Reads data from an Excel file, processes it, and generates a JSON file with team details.

  This function reads data from the 'Website-Content.xlsx' file located in the './website-team-list-creator/' directory.
  It processes the data, creates a dictionary of team details, and saves it as 'team_details.json' in the same directory.

  Returns:
    None
  """
  # Read the team details from the 'team_details.json' file
  data = readJSON()
  createJSON(data)

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

def createJSON(excelFileName: str, prevMembers: dict = None):
    df = pd.read_excel(excelFileName)
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

def renameImage(row):
  """
  Renames the image file associated with a given row in the team list.

  Args:
    row (dict): A dictionary representing a row in the team list.

  Returns:
    None
  """

  oldImage = row["Image"]
  if oldImage == "":
    return
  

  oldImage = row["Image"].split("/")[-1].replace("%20", " ")
  oldImageExists = os.path.exists(f"./images/{oldImage}")

  email = row["Email"]
  username = email.split("@")[0]
  newImage = f"{username}.png"
  newImageExists = os.path.exists(f"./images/{newImage}")

  if (not oldImageExists) and (not newImageExists):
    raise FileNotFoundError(f"Image {oldImage} does not exist for {row['Name']}")
  elif newImageExists:
    row["Image"] = newImage
    return
  else:
    # Load the image
    # Load the image
    img = Image.open(f"./images/{oldImage}")

    # Scale the image down
    max_dimension = 720
    width, height = img.size
    if width > height:
      new_width = max_dimension
      new_height = int(height * (max_dimension / width))
    else:
      new_height = max_dimension
      new_width = int(width * (max_dimension / height))
    img = img.resize((new_width, new_height))
    
    # Save the image with the new name
    img.save(f"./images/{newImage}", "PNG")
    # Update the image name in the row
    row["Image"] = newImage
    # Remove the old image file
    os.remove(f"./images/{oldImage}")

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
  teams = teams.split(";")[:-1]

  for team in teams:
    if row[f"{team} Role"] == "":
      raise ValueError(f"Role for {team} is empty for {row['Name']}")
    role = {
      "role": row[f"{team} Role"],
      "team": team,
      "lead": isLead(row[f"{team} Role"], team),
    }
    member['roles'].append(role)
  return member

def isLead(role, teamName):
  """
  Checks if the given role is a lead role.

  Args:
    role (str): The role to check.

  Returns:
    bool: True if the role is a lead role, False otherwise.
  """
  if isinstance(role, str) and "Head of" in role:
    return True
  
  if isinstance(role, str) and "Director" in role:
    return True
  
  if isinstance(role, str) and "Lead" in role and teamName != "Management":
    return True
  
  return False

def addPreviousMembers(prevMembers, members, memberEmails):
    if prevMembers is not None:
      for prevMember in prevMembers:
        email = prevMember.get('email', '')
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

if __name__ == "__main__":
  main()