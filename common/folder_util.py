import subprocess


def delete_folder(folder_name):
    subprocess.run(f"rm -rf {folder_name}", shell=True)