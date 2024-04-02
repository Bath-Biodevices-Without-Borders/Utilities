import pandas as pd
import json
import os

def main():
  """
  Reads data from an Excel file, processes it, and generates a JSON file with team details.

  This function reads data from the 'Website-Content.xlsx' file located in the './website-team-list-creator/' directory.
  It processes the data, creates a dictionary of team details, and saves it as 'team_details.json' in the same directory.

  Returns:
    None
  """
  createJSON()

def createJSON():
    df = pd.read_excel("./Website-Content.xlsx")

    jsonData = {
    "Management": [],
    "Hardware": [],
    "Sensors": [],
    "Software": [],
    "Finance": [],
    "Outreach": [],
    "Social": []
  }

    df.fillna("", inplace=True)

    counter = 0
    for index, row in df.iterrows():
      renameImage(row)
      teams = getMemberTeams(row)
      for team in teams:
        member = createMember(row, idCounter=counter)
        counter += 1
        jsonData[team].append(member)

    with open("./team_details.json", "w") as jsonFile:
      json.dump(jsonData, jsonFile, indent=4)


def getMemberTeams(row):
  teams = row["Teams"]
  teams = teams.split(";")
  return teams

def createMember(row, idCounter):
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
    "id": idCounter,
    "name": row["Name"],
    "email": row["Email"],
    "course": row["Course"],
    "link": row["Link"],
    "description": row["Description"],
    "image": row["Image"],
    "startDate": str(row["Join Date"]),
    "endDate": str(row["Leave Date"]),
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


if __name__ == "__main__":
  main()
