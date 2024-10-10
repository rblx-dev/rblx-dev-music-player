import sys
import os
import ctypes
import subprocess

def run_invisible(cmd):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    process = subprocess.Popen(cmd, startupinfo=startupinfo, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               stdin=subprocess.PIPE)
    return process

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "music_player.py")
    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
    
    # Hide the console window of the current process
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Run the main script invisibly
    run_invisible([pythonw_path, main_script])
