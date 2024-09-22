import os
import csv
import shutil
import argparse

# Usage Examples:
# python script.py list --group-size 23
# python script.py view
# python script.py copy 1
# python script.py name "My Backup"

# Define the command line argument parser
def parse_args():
    parser = argparse.ArgumentParser(description="Manage file groups and backup operations.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Command to list and group files
    list_parser = subparsers.add_parser('list', help='List and group files in the current directory')
    list_parser.add_argument('--group-size', type=int, default=23, help='Maximum size of each group in GB')
    # copy_parser.add_argument('--all', action='store_true', help='Copy all groups if specified')


    # Command to view groups
    view_parser = subparsers.add_parser('view', help='View groups in the file info directory')

    # Command to copy group
    copy_parser = subparsers.add_parser('copy', help='Copy specified group to a backup directory')
    copy_parser.add_argument('group_number', type=int, help='Group number to copy')

    # Command to name the backup
    name_parser = subparsers.add_parser('name', help='Name the backup for easier identification')
    name_parser.add_argument('backup_name', type=str, help='Provide a name for the backup')

    return parser.parse_args()


# Function to list files and handle oversized files
def list_files(directory, max_size_gb):
    max_size_bytes = max_size_gb * 1024**3
    file_list = []
    oversized_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), start=directory)
            file_size = os.path.getsize(os.path.join(root, file))
            if file_size > max_size_bytes:
                oversized_files.append((file_path, file_size))
            else:
                file_list.append((file_path, file_size))
    return file_list, oversized_files

# Function to divide files by size into groups
def divide_files_by_size(file_list, max_size_gb):
    max_size_bytes = max_size_gb * 1024**3  # Convert GB to bytes
    grouped_files = []
    current_group = []
    current_size = 0

    for file_path, file_size in file_list:
        if current_size + file_size > max_size_bytes:
            if current_group:
                grouped_files.append(current_group)
            current_group = []
            current_size = 0
        current_group.append((file_path, file_size))
        current_size += file_size

    if current_group:
        grouped_files.append(current_group)

    return grouped_files

# Function to save groups to a CSV file
def save_groups_to_csv(groups, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(['Group Number', 'File Path', 'File Size (bytes)'])
        for group_number, group in enumerate(groups, start=1):
            for file_path, file_size in group:
                writer.writerow([group_number, file_path, file_size])

# Function to read groups from a CSV file
def read_groups_from_csv(input_file):
    groups = {}
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')
        next(reader)  # Skip header
        for row in reader:
            group_number = int(row[0])
            file_path = row[1]
            file_size = int(row[2])
            if group_number not in groups:
                groups[group_number] = []
            groups[group_number].append((file_path, file_size))
    return groups

def copy_files_of_group(input_csv, group_number, destination_folder, backup_name="Backup"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    total_size = 0
    num_files = 0
    script_path = os.path.realpath(__file__)
    destination_script_path = os.path.realpath(os.path.join(destination_folder, os.path.basename(script_path)))
    
    with open(input_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')
        headers = next(reader, None)  # Attempt to read the header safely
        if not headers:
            print("CSV file is empty or malformed.")
            return

        for row in reader:
            current_group_number = int(row[0])
            if current_group_number == group_number:
                file_path = row[1]
                full_file_path = os.path.realpath(os.path.join(os.getcwd(), file_path))
                destination_file_path = os.path.realpath(os.path.join(destination_folder, file_path))
                os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
                
                if full_file_path != destination_file_path:  # Check if paths are truly different
                    os.link(full_file_path, destination_file_path)
                    print(f"Created symlink from '{full_file_path}' to '{destination_file_path}'")
                total_size += int(row[2])
                num_files += 1

    # Create info.txt file and copy it
    info_path = os.path.join(destination_folder, "info.txt")
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"Backup Name: {backup_name}\n")
        f.write(f"Group Number: {group_number}\n")
        f.write(f"Number of Files: {num_files}\n")
        f.write(f"Total Size: {total_size / 1024**3:.2f} GB\n")

    # # Check paths and copy the script if they are different
    # if script_path != destination_script_path:
    #     shutil.copy(script_path, destination_script_path)
    #     print(f"Copied script to {destination_script_path}")
    # else:
    #     print("Script copy skipped as source and destination are the same.")

    # Copy the .file_info directory
    destination_file_info_path = os.path.join(destination_folder, '.file_info')
    if not os.path.exists(destination_file_info_path):
        shutil.copytree('.file_info', destination_file_info_path)
    else:
        print("File info directory copy skipped as it already exists.")

    print(f"Backup information, script, and metadata copied to {destination_folder}")

# Function to set the backup name
def set_backup_name(file_info_path, backup_name):
    with open(os.path.join(file_info_path, 'backup_name.txt'), 'w') as file:
        file.write(backup_name)

def main():
    args = parse_args()
    current_directory = os.getcwd()
    file_info_path = os.path.join(current_directory, '.file_info')

    if args.command == 'list':
        if not os.path.exists(file_info_path):
            os.makedirs(file_info_path)
        file_list, oversized_files = list_files(current_directory, args.group_size)
        grouped_files = divide_files_by_size(file_list, args.group_size)
        save_groups_to_csv(grouped_files, os.path.join(file_info_path, 'groups.csv'))
        if oversized_files:
            print("Oversized files excluded from groups:")
            for path, size in oversized_files:
                print(f"{path} - {size / 1024**3:.2f} GB")
        print(f"File groups saved to {os.path.join(file_info_path, 'groups.csv')}")

    elif args.command == 'view':
        if os.path.exists(os.path.join(file_info_path, 'groups.csv')):
            groups = read_groups_from_csv(os.path.join(file_info_path, 'groups.csv'))
            for group_number, files in groups.items():
                total_size = sum(file_size for _, file_size in files) / 1024**3
                print(f"Group {group_number}: {len(files)} files, Total size: {total_size:.2f} GB")
        else:
            print("No group information available.")

    elif args.command == 'copy':
        destination_folder = os.path.join('./.backup_files', f'group_{args.group_number}')
        backup_name = open(os.path.join(file_info_path, 'backup_name.txt')).read().strip() if os.path.exists(os.path.join(file_info_path, 'backup_name.txt')) else "Unnamed Backup"
        copy_files_of_group(os.path.join(file_info_path, 'groups.csv'), args.group_number, destination_folder, backup_name)
        print(f"Group {args.group_number} and associated data copied to {destination_folder}")

    elif args.command == 'name':
        if not os.path.exists(file_info_path):
            os.makedirs(file_info_path)
        set_backup_name(file_info_path, args.backup_name)
        print(f"Backup name set to '{args.backup_name}'")

if __name__ == '__main__':
    main()

