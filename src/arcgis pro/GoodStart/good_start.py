from projCreator_utils import create_project

def get_project_details_and_create():
    print("Enter Excel Spreadsheet Path:")
    excel_path = input().replace('"', '')  # Remove double quotes
    print("Enter Sheet Name (optional):")
    sheet_name = input()
    print("Enter Project Name:")
    project_name = input()

    print("Do you want to create the project? (yes/no)")
    consent = input()
    # Check if the user wants to create the project using yes/no or y/n

    if consent.lower() in ["yes", "y"]:
        create_project(excel_path, sheet_name, project_name)
    else:
        print("Project creation canceled.")
        

if __name__ == "__main__":
    get_project_details_and_create()