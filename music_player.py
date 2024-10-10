import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os

# Function to show error message
def show_error(title, message):
    print(f"Error: {title} - {message}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()

try:
    import pygame
    from mutagen import File
    import yt_dlp as youtube_dl
    import urllib.request
    import urllib.parse
except ImportError as e:
    show_error("Import Error", f"Failed to import required module: {str(e)}\n"
               "Please ensure you have installed all required libraries.")
    sys.exit(1)

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("rblx-dev's music player")
        self.root.geometry("600x400")

        try:
            pygame.mixer.init()
        except pygame.error as e:
            show_error("Pygame Initialization Error", f"Failed to initialize Pygame mixer: {str(e)}")
            sys.exit(1)

        self.playlist = []
        self.current_track = 0
        self.paused = False
        self.paused_position = 0

        # Supported file types
        self.file_types = [
            ("Audio Files", "*.mp3 *.ogg *.wav"),
            ("MP3 Files", "*.mp3"),
            ("OGG Files", "*.ogg"),
            ("WAV Files", "*.wav"),
        ]

        # Create custom style for the volume slider
        self.style = ttk.Style()
        self.style.configure("Black.Vertical.TScale", background="black", troughcolor="gray")

        # Create UI elements
        self.create_ui()

        # Bind spacebar to play/pause
        self.root.bind("<space>", self.toggle_play_pause)

    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for playlist and controls
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Playlist
        self.playlist_box = tk.Listbox(left_frame, width=50, height=10)
        self.playlist_box.pack(pady=10)

        # Control buttons
        control_frame = tk.Frame(left_frame)
        control_frame.pack()

        play_btn = tk.Button(control_frame, text="Play", command=self.play)
        pause_btn = tk.Button(control_frame, text="Pause", command=self.pause)
        stop_btn = tk.Button(control_frame, text="Stop", command=self.stop)
        next_btn = tk.Button(control_frame, text="Next", command=self.next_track)
        prev_btn = tk.Button(control_frame, text="Previous", command=self.prev_track)

        play_btn.grid(row=0, column=0, padx=5)
        pause_btn.grid(row=0, column=1, padx=5)
        stop_btn.grid(row=0, column=2, padx=5)
        next_btn.grid(row=0, column=3, padx=5)
        prev_btn.grid(row=0, column=4, padx=5)

        # Add song buttons
        add_local_btn = tk.Button(left_frame, text="Add Local Song", command=self.add_local_song)
        add_local_btn.pack(pady=5)

        # Online song entry and button
        online_frame = tk.Frame(left_frame)
        online_frame.pack(pady=5)

        self.online_entry = tk.Entry(online_frame, width=40)
        self.online_entry.grid(row=0, column=0, padx=5)

        add_online_btn = tk.Button(online_frame, text="Add Online Song", command=self.add_online_song)
        add_online_btn.grid(row=0, column=1, padx=5)

        # Right frame for volume control
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Volume label
        volume_label = tk.Label(right_frame, text="Volume")
        volume_label.pack(pady=5)

        # Volume bar (black color)
        self.volume_scale = ttk.Scale(right_frame, from_=100, to=0, orient=tk.VERTICAL, 
                                      length=200, command=self.set_volume, 
                                      style="Black.Vertical.TScale")
        self.volume_scale.set(70)  # Set default volume to 70%
        self.volume_scale.pack()

        # Set initial volume
        self.set_volume(70)

    def add_local_song(self):
        songs = filedialog.askopenfilenames(filetypes=self.file_types)
        for song in songs:
            self.playlist.append({"type": "local", "path": song})
            song_name = os.path.basename(song)
            self.playlist_box.insert(tk.END, song_name)

    def add_online_song(self):
        url = self.online_entry.get()
        if url:
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info['title']
                    url = info['url']
                self.playlist.append({"type": "online", "url": url, "title": title})
                self.playlist_box.insert(tk.END, title)
                self.online_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot add the online song: {str(e)}")

    def play(self):
        if self.playlist:
            try:
                if self.paused:
                    pygame.mixer.music.unpause()
                    self.paused = False
                else:
                    track = self.playlist[self.current_track]
                    if track["type"] == "local":
                        pygame.mixer.music.load(track["path"])
                    else:  # online
                        pygame.mixer.music.load(track["url"])
                    pygame.mixer.music.play(start=self.paused_position)
                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.selection_set(self.current_track)
            except pygame.error as e:
                self.handle_playback_error(e)

    def handle_playback_error(self, error):
        messagebox.showerror("Error", f"Cannot play the song: {str(error)}")
        print(f"Debug - Error details: {error}")
        self.next_track()  # Skip to the next track if we can't play this one

    def pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.paused_position = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds

    def stop(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.paused_position = 0

    def next_track(self):
        if self.playlist:
            self.current_track = (self.current_track + 1) % len(self.playlist)
            self.paused = False
            self.paused_position = 0
            self.play()

    def prev_track(self):
        if self.playlist:
            self.current_track = (self.current_track - 1) % len(self.playlist)
            self.paused = False
            self.paused_position = 0
            self.play()

    def set_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)

    def toggle_play_pause(self, event=None):
        if self.paused or not pygame.mixer.music.get_busy():
            self.play()
        else:
            self.pause()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MusicPlayer(root)
        root.mainloop()
    except Exception as e:
        show_error("Unexpected Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)