"""
Author: Yusuf Emir Sezgin
Date: 2025-02-01
Description: This script allows you to resize and reformat videos without cropping. 
It maintains the correct aspect ratio by adding black padding when necessary.

License: MIT License
a. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction.
b. The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability.
c. The software is free to use, modify, and distribute, subject to the above license terms.
"""

import os
import subprocess
import time
import sys
import platform

# ANSI color codes
class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Aspect ratio mapping for common formats
aspect_ratios = {
    "16:9": (1920, 1080),
    "4:3": (1440, 1080),
    "21:9": (2560, 1080),
    "1:1": (1080, 1080),
    "9:16": (1080, 1920),
    "3:4": (1080, 1440)
}

def clear_terminal():
    """Clears the terminal screen depending on the OS."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_welcome_message():
    """Displays the welcome box with developer info and usage instructions."""
    welcome_text = "WELCOME TO THE VIDEO EDIT SYSTEM"
    box_width = 70  # Adjust width for a clean layout

    info = [
        f"Developed by: Yusuf Emir Sezgin",
        f"Description: This tool allows you to resize and reformat videos",
        f"without cropping. It maintains the correct aspect ratio by",
        f"adding black padding when necessary.",
        "",
        f"Usage:",
        f"1. Run the script and enter the name of the video to edit.",
        f"2. Choose an output filename (it will be saved to Desktop).",
        f"3. Select the target aspect ratio from the list.",
        f"4. Wait while the video is processed.",
        f"5. Once done, you can choose to continue or exit.",
        "",
        f"Required Packages:",
        f"- FFmpeg (Ensure it's installed and added to system PATH).",
        "",
        f"To install FFmpeg:",
        f"- Mac/Linux: `brew install ffmpeg` or `sudo apt install ffmpeg`",
        f"- Windows: Download from https://ffmpeg.org and add to PATH.",
        "",
        f"Press Enter to Begin..."
    ]

    # Print the top border
    print(f"{TerminalColors.HEADER}#{'#' * (box_width - 2)}#{TerminalColors.ENDC}")

    # Print the welcome text centered
    print(f"{TerminalColors.HEADER}# {welcome_text.center(box_width - 4)} #")

    # Print a separator
    print(f"{TerminalColors.HEADER}#{'#' * (box_width - 2)}#{TerminalColors.ENDC}")

    # Print the info inside the box
    for line in info:
        print(f"{TerminalColors.HEADER}# {line.ljust(box_width - 4)} #")

    # Print the bottom border
    print(f"{TerminalColors.HEADER}#{'#' * (box_width - 2)}#{TerminalColors.ENDC}")


def change_video_ratio(input_path, output_path, target_ratio):
    """Converts any video to the desired aspect ratio by resizing and adding black bars."""
    print(f"{TerminalColors.OKBLUE}Processing Started!{TerminalColors.ENDC}")
    if target_ratio not in aspect_ratios:
        print(f"{TerminalColors.FAIL}Unsupported aspect ratio: {target_ratio}{TerminalColors.ENDC}")
        return
    
    # Get video dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", input_path],
        capture_output=True, text=True
    )
    width, height = map(int, probe.stdout.strip().split(","))
    
    # Get target dimensions from aspect_ratios dictionary
    target_width, target_height = aspect_ratios[target_ratio]
    
    # Determine scaling factors and calculate new width/height
    if width / height > target_width / target_height:  # Landscape video
        scale_width = target_width
        scale_height = int(target_width * height / width)
    else:  # Portrait or square video
        scale_height = target_height
        scale_width = int(target_height * width / height)
    
    # Apply scaling and padding to ensure target aspect ratio
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path, "-vf",
        f"scale={scale_width}:{scale_height},pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:a", "copy", output_path
    ]
    
    # Run the ffmpeg command and suppress output
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Display the loading bar
    while True:
        output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Look for progress information (time) in ffmpeg stderr
            if "time=" in output:
                try:
                    # Extract time value from the output (e.g., time=00:00:15.02)
                    time_str = output.split("time=")[1].split()[0]
                    hours, minutes, seconds = map(float, time_str.split(":"))
                    elapsed_time = hours * 3600 + minutes * 60 + seconds

                    # Get video duration
                    probe_duration = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", input_path],
                        capture_output=True, text=True
                    )
                    total_duration = float(probe_duration.stdout.strip())

                    # Calculate progress as percentage
                    progress = int((elapsed_time / total_duration) * 100)
                    print(f"\r{TerminalColors.OKGREEN}Processing: [{'=' * (progress // 2)}{' ' * (50 - progress // 2)}] {progress}% Complete{TerminalColors.ENDC}", end="")
                except ValueError:
                    # Ignore lines that do not contain time values
                    pass
        time.sleep(0.1)

    print(f"\n{TerminalColors.OKBLUE}Processing complete!{TerminalColors.ENDC}")

def user_input():
    """Handles the user input for video name, output name, and aspect ratio selection."""
    input_video = input(f"{TerminalColors.OKBLUE}SELECT VIDEO TO EDIT (just video name): {TerminalColors.ENDC}")
    input_path, video_ext = find_video(input_video)
    
    if not input_path:
        print(f"{TerminalColors.FAIL}Video not found!{TerminalColors.ENDC}")
        return

    output_video = input(f"{TerminalColors.OKBLUE}SELECT EDITED VIDEO NAME TO SAVE: {TerminalColors.ENDC}")
    user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(user_desktop, f"{output_video}{video_ext}")    # Keep the same extension and save to Desktop

    target_ratio = select_aspect_ratio()
    time.sleep(0.5)
    clear_terminal()
    change_video_ratio(input_path, output_path, target_ratio)

def find_video(video_name):
    """Finds the video file by searching for common extensions."""
    common_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"]
    
    for root, dirs, files in os.walk(os.getcwd()):
        for ext in common_extensions:
            if f"{video_name}{ext}" in files:
                return os.path.join(root, f"{video_name}{ext}"), ext  # Return full path and extension
    return None, None  # Video not found


def select_aspect_ratio():
    """Displays the aspect ratio options and allows the user to select one."""
    print(f"\n{TerminalColors.WARNING}Select the aspect ratio:{TerminalColors.ENDC}")
    for ratio in aspect_ratios.keys():
        print(f" {TerminalColors.OKGREEN}- {ratio}{TerminalColors.ENDC}")
    
    target_ratio = input(f"\n{TerminalColors.OKBLUE}Enter your choice (e.g., 16:9, 4:3): {TerminalColors.ENDC}")
    
    if target_ratio not in aspect_ratios:
        print(f"{TerminalColors.FAIL}Invalid choice. Defaulting to 16:9.{TerminalColors.ENDC}")
        target_ratio = "16:9"
    
    return target_ratio

def continue_prompt():
    """Handles the continue prompt after editing."""
    clear_terminal()  # Clear after process completion
    continue_choice = input(f"{TerminalColors.OKGREEN}CONTINUE? (Press Enter to restart, Q to quit): {TerminalColors.ENDC}")
    if continue_choice.lower() == 'q':
        sys.exit(0)

def main():
    clear_terminal()  # Clear terminal before the program starts
    print_welcome_message()
    input()  # Wait for user to press Enter to begin

    while True:
        clear_terminal()  # Clear after welcome message
        user_input()
        continue_prompt()

if __name__ == "__main__":
    main()
