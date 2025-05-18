import os
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import sys
import subprocess


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} ...")
        install(package)
    else:
        print(f"{package} + .")


# Function to create a safe filename for paths only, NOT for video titles
def safe_path(title):
    # Remove invalid characters for paths only
    #safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    return title

# Function to check if a video is already downloaded
def is_already_downloaded(video_title, output_path):
    # Check if the directory exists
    if not os.path.exists(output_path):
        return False
    
    # Check if any file in the directory contains the video title
    for file in os.listdir(output_path):
        if video_title in file and file.endswith(".mp4"):
            print(f"Skipping (already downloaded): {video_title}")
            return True
    
    return False

# Function to download a single YouTube video
def download_video(url, output_path):
    try:
        # Create YouTube object
        yt = YouTube(url, on_progress_callback=on_progress)
        
        # Check if video already exists
        if is_already_downloaded(yt.title, output_path):
            return
        
        # Get the highest resolution stream
        ys = yt.streams.get_highest_resolution()
        print(f"Downloading: {yt.title}")
        # Download with original title (no filename modification)
        ys.download(output_path)
        print(f"Downloaded: {yt.title}")
        
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

# Function to download a YouTube playlist
def download_playlist(playlist_url, downloads_dir):
    try:
        # Create Playlist object
        playlist = Playlist(playlist_url)
        
        # Create output directory with playlist title - use safe_path for the folder name only
        #playlist_dir_name = safe_path(playlist.title)
        #playlist_dir = os.path.join(downloads_dir, playlist_dir_name)
        playlist_dir = downloads_dir
        os.makedirs(playlist_dir, exist_ok=True)
        
        print(f"Downloading playlist: {playlist.title}")
        print(f"Number of videos: {len(playlist.video_urls)}")
        
        # Download each video in the playlist
        downloaded_count = 0
        skipped_count = 0
        
        for index, video_url in enumerate(playlist.video_urls):
            print(f"Video {index+1}/{len(playlist.video_urls)}")
            
            # Try to get video info first to check if it exists
            try:
                yt = YouTube(video_url)
                if is_already_downloaded(yt.title, playlist_dir):
                    skipped_count += 1
                    continue
            except Exception as e:
                print(f"Error checking video: {str(e)}")
                continue
                
            download_video(video_url, playlist_dir)
            downloaded_count += 1
            
        print(f"\nPlaylist download completed!")
        print(f"Downloaded: {downloaded_count}, Skipped: {skipped_count}")
        print(f"Saved to: {playlist_dir}")
        
    except Exception as e:
        print(f"Error with playlist {playlist_url}: {str(e)}")

# Function to handle URL (detect if it's a playlist or single video)
def handle_url(url, downloads_dir):
    if "playlist" in url:
        download_playlist(url, downloads_dir)
    else:
        # For single videos, create a "Singles" folder
        singles_dir = os.path.join(downloads_dir, "Singles")
        os.makedirs(singles_dir, exist_ok=True)
        download_video(url, singles_dir)

# Main function to read links from file and download
def main():
    check_and_install('pytubefix') 
    # Set downloads directory relative to script location or executable location
    if getattr(sys, 'frozen', False):
        # If running as executable
        script_dir = os.path.dirname(sys.executable)
    else:
        # If running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    downloads_dir = os.path.join(script_dir, "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Path to the links file
    links_file = os.path.join(script_dir, "video_links.txt")
    
    # Check if the file exists
    if not os.path.exists(links_file):
        print(f"Error: {links_file} not found!")
        print("Please create a file named 'video_links.txt' with your YouTube links.")
        input("Press Enter to exit...")
        return
    
    # Read links from file
    with open(links_file, 'r') as file:
        links = [line.strip() for line in file if line.strip()]
    
    if not links:
        print("No links found in video_links.txt. Please add some YouTube links.")
        input("Press Enter to exit...")
        return
    
    print(f"Found {len(links)} links in {links_file}")
    
    # Process each link
    for i, link in enumerate(links):
        print(f"\nProcessing link {i+1}/{len(links)}: {link}")
        handle_url(link, downloads_dir)
    
    print("\nAll downloads completed!")
    print("Downloaded videos are saved in the 'downloads' folder.")
    input("Press Enter to exit...")

# Run the main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        input("Press Enter to exit...")

# Note: Before using this script, you need to install pytubefix  using:
