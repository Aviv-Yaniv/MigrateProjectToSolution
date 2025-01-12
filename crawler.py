import os
import re
import subprocess
from collections import deque

PROJECT_FILE_PATH = r'PROJECT_TO_MIGRATE_PATH.csproj'
SOLUTION_FILE_PATH = r'DESTINATION_MIGRATION_SOLUTION_PATH.sln'
DESTINATION_FILE_NAME = 'projects_to_add.txt'

def convert_relative_to_absolute_path(origin_path, relative_path):
    base_dir = os.path.dirname(origin_path)
    return os.path.abspath(os.path.join(base_dir, relative_path))

def find_project_paths_in_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    pattern = r'<ProjectReference Include="([^"]+\.csproj)"'
    matches = re.findall(pattern, file_content)
    absolute_paths = [convert_relative_to_absolute_path(file_path, match) for match in matches]
    return absolute_paths

def crawl(project_file_path, existing_projects):
    projects_to_add = set()
    files_queue = deque(find_project_paths_in_file(project_file_path))
    while files_queue:
        current_project_file_path = files_queue.popleft()
        print(f'Scanning: {current_project_file_path}')
        if current_project_file_path not in existing_projects:
            projects_to_add.add(current_project_file_path)
            files_queue.extend(find_project_paths_in_file(current_project_file_path))
    return projects_to_add

def fetch_existing_projects(solution_file_path):
    pattern = r'\"([^\"]+\.csproj)\"'
    with open(solution_file_path, 'r') as file:
        file_content = file.read()
    matches = re.findall(pattern, file_content)
    return set([convert_relative_to_absolute_path(solution_file_path, match) for match in matches])

def scan(solution_file_path, project_file_path, projects_to_add_file_path):
    existing_projects = fetch_existing_projects(solution_file_path)
    projects_to_add=crawl(project_file_path, existing_projects)
    with open(projects_to_add_file_path, "w") as file:
        file.writelines(line + '\n' for line in projects_to_add)

def add_to_solution(projects_to_add_file_path, solution_file_path):
    with open(projects_to_add_file_path, "r") as file:
        projects_to_add=file.readlines()
    for project_path in projects_to_add:
        command = f'dotnet sln {solution_file_path} add {project_path}'
        result = subprocess.check_output(command, shell=True, text=True)
        print(result)

scan(solution_file_path=SOLUTION_FILE_PATH, project_file_path=PROJECT_FILE_PATH, projects_to_add_file_path=DESTINATION_FILE_NAME)
add_to_solution(projects_to_add_file_path=DESTINATION_FILE_NAME, solution_file_path=SOLUTION_FILE_PATH)
