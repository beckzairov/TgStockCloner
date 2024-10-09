import os
import subprocess
import rarfile  # Requires 'rarfile' library, install using: pip install rarfile
import shutil
import glob

# Configuration
links_file = "25acc.txt"  # Your file with URLs
base_clone_folder = "Telegram"  # Path to your example Telegram folder template
output_folder = "downloads"  # Temporary folder for downloaded zip files
clone_base_path = "D:\\Tgs\\Abd\\25acc-13Sep"  # Where all the Telegram clones will be stored
megatools_path = "C:\\Program Files\\megatools-1.11.1.20230212-win32\\megatools.exe"  # Replace with the actual path to the megatools executable
progress_file = "progress.txt"  # File to store the progress of completed clones

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(clone_base_path, exist_ok=True)

# Read the links from the file, ignoring empty lines or spaces
with open(links_file, 'r') as f:
    links = [line.strip() for line in f if line.strip()]

# Read completed clones from the progress file
if os.path.exists(progress_file):
    with open(progress_file, 'r') as f:
        completed_clones = set(line.strip() for line in f if line.strip())
else:
    completed_clones = set()

# Function to download a file using megatools
def download_with_megatools(url, output_folder):
    print(f"Downloading from {url} using megatools...")
    try:
        # Run the megatools command
        subprocess.run([megatools_path, 'dl', url, '--path', output_folder], check=True)
        print(f"Downloaded to {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e}")
        return False
    except FileNotFoundError:
        print(f"Error: The megatools executable was not found at {megatools_path}.")
        return False
    return True

# Main process
all_completed = True
for idx, link in enumerate(links):
    # Define paths for the current clone
    clone_folder_name = f"Telegram{idx + 1}" if idx > 0 else "Telegram"
    clone_path = os.path.join(clone_base_path, clone_folder_name)
    extract_path = ""  # Initialize extract_path

    # Check if this clone has already been completed
    if clone_folder_name in completed_clones:
        print(f"Skipping {clone_folder_name} as it is already completed.")
        continue

    try:
        # Download the rar file using megatools
        success = download_with_megatools(link, output_folder)
        if not success:
            all_completed = False
            break

        # Find the downloaded .rar file in the output folder
        downloaded_rar_files = glob.glob(os.path.join(output_folder, "*.rar"))
        if not downloaded_rar_files:
            print(f"No .rar file found after downloading from {link}.")
            all_completed = False
            break
        
        download_path = downloaded_rar_files[0]  # Take the first .rar file found
        print(f"Extracting {download_path}...")

        # Unrar and locate the tdata folder and twoFA.txt inside the downloaded content
        extract_path = os.path.join(output_folder, f"extracted_{idx + 1}")
        with rarfile.RarFile(download_path, 'r') as rar_ref:
            rar_ref.extractall(extract_path)

        # Locate the folder containing `tdata` and `twoFA.txt` (assuming the folder name is numerical)
        extracted_dirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
        if len(extracted_dirs) != 1:
            print(f"Error: Expected exactly one extracted folder, found {len(extracted_dirs)}.")
            all_completed = False
            break
        extracted_content_path = os.path.join(extract_path, extracted_dirs[0])
        tdata_folder = os.path.join(extracted_content_path, "tdata")
        twoFA_file = os.path.join(extracted_content_path, "twoFA.txt")

        # Check if `tdata` and `twoFA.txt` exist in the extracted folder
        if not os.path.exists(tdata_folder) or not os.path.isfile(twoFA_file):
            print(f"Error: tdata folder or twoFA.txt not found in {extracted_content_path}.")
            all_completed = False
            break

        # Copy the base Telegram folder template to create a new clone
        print(f"Copying base template to {clone_path}...")
        shutil.copytree(base_clone_folder, clone_path)

        # Copy the `tdata` folder into the new clone's directory
        destination_tdata_path = os.path.join(clone_path, "tdata")
        shutil.copytree(tdata_folder, destination_tdata_path)

        # Copy the `twoFA.txt` file into the new clone's directory
        destination_twoFA_path = os.path.join(clone_path, "twoFA.txt")
        shutil.copy2(twoFA_file, destination_twoFA_path)

        print(f"Copied tdata and twoFA.txt to {clone_path}")

        # Mark this clone as completed
        with open(progress_file, 'a') as f:
            f.write(f"{clone_folder_name}\n")

    except Exception as e:
        print(f"An error occurred for {link}: {e}")
        all_completed = False
        break

    finally:
        # Clean up the downloaded and extracted files
        if downloaded_rar_files:
            for rar_file in downloaded_rar_files:
                os.remove(rar_file)
        if extract_path and os.path.exists(extract_path):
            shutil.rmtree(extract_path)

    print(f"Setup complete for {clone_folder_name}")

# If all links processed successfully, remove the progress file and clean temporary storage
if all_completed:
    print("All clones processed successfully. Cleaning up progress file and temporary storage.")
    if os.path.exists(progress_file):
        os.remove(progress_file)
    shutil.rmtree(output_folder)
else:
    print("Process was interrupted or encountered errors. Progress has been saved.")

print("Process completed for all links.")
