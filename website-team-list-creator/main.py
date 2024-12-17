from createJson import createJSON, readJSON
from git import syncData
import sys


def main():
  """
  Reads data from an Excel file, processes it, and generates a JSON file with team details.

  This function reads data from the 'Website-Content.xlsx' file located in the './website-team-list-creator/' directory.
  It processes the data, creates a dictionary of team details, and saves it as 'team_details.json' in the same directory.

  Returns:
    None
  """
  repository, excelFilePath = getArguments()
  data = readJSON()
  createJSON(excelFilePath, data)
  syncData(repository)


def getArguments():
  """
  Retrieves the repository HTTPS and Excel file path from the program arguments.

  Returns:
    tuple: A tuple containing the repository HTTPS and Excel file path.
    
  Raises:
    IndexError: If the repository HTTPS or Excel file path is not provided or is in an invalid format.
  """
  # Get the repository HTTPS from the program arguments
  try:
    repository = sys.argv[1]
    if not repository.startswith("https://github.com/"):
      raise IndexError
  except IndexError:
    print("Please provide the repository HTTPS as the first command line argument.")
    print("Your arguments:")
    print(sys.argv)
    sys.exit(1)

  # Get the Excel file path from the program arguments
  try:
    excelFilePath = sys.argv[2]
    if not excelFilePath.endswith(".xlsx"):
      raise IndexError
  except IndexError:
    print("Please provide the Excel file path as the second command line argument.")
    print("Your arguments:")
    print(sys.argv)
    sys.exit(1)
  
  return repository, excelFilePath


if __name__ == "__main__":
  main()

#python C:\Users\Jamie\Documents\GitHub\Utilities\website-team-list-creator\main.py "https://github.com/Bath-Biodevices-Without-Borders/Website.git" "C:\Users\Jamie\OneDrive - University of Bath\Software\Website\WebsiteContent.xlsx"