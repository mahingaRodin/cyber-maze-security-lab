#!/usr/bin/env python3
"""
Cyber Maze - COMPLETE CLEANUP TOOL
Removes ALL traces of the backdoor from the victim's system
Run this as Administrator for best results
"""
import os
import shutil
import sys
import time
import subprocess
import winreg
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
LOG_FILE = "cleanup_log.txt"
ATTACKER_IP = "192.168.56.1"  # Will search for connections to this IP

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def log_message(message):
    """Log message to file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def run_as_admin():
    """Check if running as admin and restart if not"""
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            print("⚠️  Not running as Administrator!")
            print("Some items may not be removed.")
            response = input("Restart as Administrator? (y/N): ")
            if response.lower() == 'y':
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit()
            return False
    except:
        return False

# ============================================================
# CLEANUP FUNCTIONS
# ============================================================
def kill_processes():
    """Kill all related processes"""
    log_message("\n[1/9] Killing processes...")
    
    processes = [
        "WindowsUpdate.exe",
        "CyberMaze.exe", 
        "python.exe",
        "pythonw.exe",
        "svchost.exe",  # Fake svchost
        "winsvc.exe",
        "winupdate.exe"
    ]
    
    killed = 0
    for proc in processes:
        try:
            result = subprocess.run(
                f'taskkill /f /im {proc} 2>nul',
                shell=True,
                capture_output=True
            )
            if result.returncode == 0:
                log_message(f"  ✅ Killed: {proc}")
                killed += 1
        except:
            pass
    
    if killed == 0:
        log_message("  ℹ️  No malicious processes found")
    
    time.sleep(2)

def kill_network_connections():
    """Kill network connections to attacker"""
    log_message("\n[2/9] Killing network connections...")
    
    try:
        # Find connections to attacker IP on port 4444
        result = subprocess.run(
            f'netstat -ano | findstr {ATTACKER_IP}:4444',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        subprocess.run(f'taskkill /f /pid {pid} 2>nul', shell=True)
                        log_message(f"  ✅ Killed connection (PID: {pid})")
                    except:
                        pass
        else:
            log_message("  ℹ️  No active connections found")
    except Exception as e:
        log_message(f"  ❌ Error: {e}")

def remove_registry_entries():
    """Remove all persistence entries from registry"""
    log_message("\n[3/9] Cleaning registry...")
    
    registry_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunServices"),
    ]
    
    value_names = [
        "WindowsUpdateSvc",
        "WindowsUpdate", 
        "CyberMaze",
        "SecurityUpdate",
        "SystemService",
        "svchost",
        "winsvc"
    ]
    
    removed = 0
    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
            
            # List all values first
            i = 0
            values_to_delete = []
            while True:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    for bad_name in value_names:
                        if bad_name.lower() in value_name.lower():
                            values_to_delete.append(value_name)
                            break
                    i += 1
                except WindowsError:
                    break
            
            # Delete bad values
            for value_name in values_to_delete:
                try:
                    winreg.DeleteValue(key, value_name)
                    log_message(f"  ✅ Removed: {path}\\{value_name}")
                    removed += 1
                except:
                    pass
            
            winreg.CloseKey(key)
        except:
            pass
    
    if removed == 0:
        log_message("  ℹ️  No malicious registry entries found")

def remove_scheduled_tasks():
    """Remove all scheduled tasks"""
    log_message("\n[4/9] Removing scheduled tasks...")
    
    tasks = [
        "WindowsUpdateTask",
        "CyberMazeTask",
        "SecurityScan",
        "SystemCheck",
        "UpdateTask",
        "GoogleUpdateTask",
        "AdobeUpdateTask"
    ]
    
    removed = 0
    for task in tasks:
        try:
            # Check if task exists
            check = subprocess.run(
                f'schtasks /query /tn "{task}" 2>nul',
                shell=True,
                capture_output=True
            )
            
            if check.returncode == 0:
                result = subprocess.run(
                    f'schtasks /delete /tn "{task}" /f 2>nul',
                    shell=True,
                    capture_output=True
                )
                if result.returncode == 0:
                    log_message(f"  ✅ Removed task: {task}")
                    removed += 1
        except:
            pass
    
    if removed == 0:
        log_message("  ℹ️  No malicious scheduled tasks found")

def delete_files():
    """Delete all backdoor files from system"""
    log_message("\n[5/9] Searching for and deleting malicious files...")
    
    # Files to search for and delete
    file_patterns = [
        "WindowsUpdate.exe",
        "CyberMaze.exe",
        "svchost.exe",
        "winsvc.exe",
        "winupdate.exe",
        "~spoolsv.log",
        "~msupdate.log",
        "attacker_activity.log",
        "shell_log.txt",
        "winsvc.py",
        "winsvc.vbs",
        "winsvc.bat",
        "launcher.vbs",
        "persistent_shell.py",
        "client_agent.py"
    ]
    
    # Directories to search
    search_dirs = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\AppData\\Local\\Temp"),
        os.path.expanduser("~\\AppData\\Local\\Temp\\*"),
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Caches"),
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
        "C:\\Windows\\Temp",
        "C:\\ProgramData\\Microsoft\\Windows\\Caches",
        "C:\\",
        os.getcwd()
    ]
    
    deleted = 0
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
            
        for pattern in file_patterns:
            try:
                # Use dir command to find files
                result = subprocess.run(
                    f'dir /s /b "{search_dir}\\{pattern}" 2>nul',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    files = result.stdout.strip().split('\n')
                    for file_path in files:
                        if file_path and os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                                log_message(f"  ✅ Deleted: {file_path}")
                                deleted += 1
                            except:
                                try:
                                    # Try with force
                                    subprocess.run(f'del /f /q "{file_path}" 2>nul', shell=True)
                                    log_message(f"  ✅ Force deleted: {file_path}")
                                    deleted += 1
                                except:
                                    log_message(f"  ❌ Could not delete: {file_path}")
            except:
                pass
    
    # Also delete any .pyc files
    try:
        result = subprocess.run(
            'dir /s /b "*.pyc" 2>nul',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            files = result.stdout.strip().split('\n')
            for file_path in files:
                if "__pycache__" in file_path:
                    try:
                        os.remove(file_path)
                    except:
                        pass
    except:
        pass
    
    if deleted == 0:
        log_message("  ℹ️  No malicious files found")
    else:
        log_message(f"  ✅ Total files deleted: {deleted}")

def remove_startup_folder():
    """Clean startup folder"""
    log_message("\n[6/9] Cleaning startup folder...")
    
    startup = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    if os.path.exists(startup):
        files = os.listdir(startup)
        suspicious = [f for f in files if any(x in f.lower() for x in 
                     ['update', 'cyber', 'svchost', 'win', 'service', 'task'])]
        
        if suspicious:
            for file in suspicious:
                file_path = os.path.join(startup, file)
                try:
                    os.remove(file_path)
                    log_message(f"  ✅ Removed from startup: {file}")
                except:
                    log_message(f"  ❌ Could not remove: {file}")
        else:
            log_message("  ℹ️  No suspicious files in startup folder")

def clean_temp_files():
    """Clean temporary files and folders"""
    log_message("\n[7/9] Cleaning temporary files...")
    
    temp_dirs = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
        "C:\\Windows\\Temp"
    ]
    
    # Create a list of suspicious temp folders
    suspicious_folders = [
        "winsvc",
        "pycache",
        "_MEI*",  # PyInstaller temp folders
    ]
    
    for temp_dir in temp_dirs:
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Find and delete suspicious folders
                for pattern in suspicious_folders:
                    result = subprocess.run(
                        f'dir /b "{temp_dir}\\{pattern}" 2>nul',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        folders = result.stdout.strip().split('\n')
                        for folder in folders:
                            folder_path = os.path.join(temp_dir, folder)
                            if os.path.isdir(folder_path):
                                try:
                                    shutil.rmtree(folder_path)
                                    log_message(f"  ✅ Removed temp folder: {folder}")
                                except:
                                    log_message(f"  ❌ Could not remove: {folder}")
            except:
                pass

def reset_hosts_file():
    """Check and reset hosts file if modified"""
    log_message("\n[8/9] Checking hosts file...")
    
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    backup_path = r"C:\Windows\System32\drivers\etc\hosts.backup"
    
    try:
        if os.path.exists(hosts_path):
            with open(hosts_path, 'r') as f:
                content = f.read()
            
            # Check for suspicious entries
            suspicious = False
            if "192.168.56.1" in content or "10.11.73.46" in content:
                suspicious = True
            
            if suspicious:
                log_message("  ⚠️  Suspicious hosts file entries found!")
                
                # Create backup
                shutil.copy2(hosts_path, backup_path)
                log_message(f"  ✅ Backup created: {backup_path}")
                
                # Restore default hosts file
                default_hosts = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost
"""
                with open(hosts_path, 'w') as f:
                    f.write(default_hosts)
                log_message("  ✅ Hosts file restored to default")
            else:
                log_message("  ✅ Hosts file appears clean")
    except Exception as e:
        log_message(f"  ❌ Error checking hosts file: {e}")

def final_scan():
    """Perform final scan for any remaining traces"""
    log_message("\n[9/9] Performing final security scan...")
    
    issues = []
    
    # Check running processes
    proc_check = subprocess.run(
        'tasklist | findstr /i "update cyber svchost python"',
        shell=True,
        capture_output=True,
        text=True
    )
    if proc_check.stdout:
        issues.append("Suspicious processes still running")
    
    # Check registry
    reg_check = subprocess.run(
        'reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | findstr /i "update svc"',
        shell=True,
        capture_output=True,
        text=True
    )
    if reg_check.stdout:
        issues.append("Suspicious registry entries remain")
    
    # Check scheduled tasks
    task_check = subprocess.run(
        'schtasks /query | findstr /i "update task"',
        shell=True,
        capture_output=True,
        text=True
    )
    if task_check.stdout:
        issues.append("Suspicious scheduled tasks remain")
    
    # Check network connections
    net_check = subprocess.run(
        f'netstat -an | findstr {ATTACKER_IP}',
        shell=True,
        capture_output=True,
        text=True
    )
    if net_check.stdout:
        issues.append(f"Active connections to {ATTACKER_IP} found")
    
    if not issues:
        log_message("\n  ✅ SYSTEM IS CLEAN! No traces found.")
        return True
    else:
        log_message("\n  ⚠️  Issues detected:")
        for issue in issues:
            log_message(f"     • {issue}")
        return False

# ============================================================
# MAIN FUNCTION
# ============================================================
def main():
    """Main cleanup function"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 80)
    print("🧹  CYBER MAZE - COMPLETE SYSTEM CLEANUP TOOL  🧹")
    print("=" * 80)
    print("This tool will remove ALL traces of the backdoor including:")
    print("  • Malicious processes")
    print("  • Network connections to attacker")
    print("  • Registry persistence entries")
    print("  • Scheduled tasks")
    print("  • Hidden files and executables")
    print("  • Startup folder items")
    print("  • Temporary files")
    print("  • Modified hosts file")
    print("=" * 80)
    print()
    
    # Check admin rights
    is_admin = run_as_admin()
    if not is_admin:
        print("\n⚠️  Continuing with limited privileges...")
    else:
        print("✅ Running with Administrator privileges")
    
    print()
    response = input("Proceed with complete system cleanup? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    start_time = time.time()
    
    # Run all cleanup functions
    kill_processes()
    kill_network_connections()
    remove_registry_entries()
    remove_scheduled_tasks()
    delete_files()
    remove_startup_folder()
    clean_temp_files()
    reset_hosts_file()
    clean = final_scan()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    if clean:
        print("✅  CLEANUP COMPLETE! System is now clean.")
    else:
        print("⚠️  CLEANUP COMPLETE with warnings. Review log above.")
    print(f"⏱️  Time elapsed: {elapsed:.1f} seconds")
    print(f"📄 Log saved to: {os.path.abspath(LOG_FILE)}")
    print("=" * 80)
    
    print("\nRecommended next steps:")
    print("  1. Restart your computer")
    print("  2. Run a full antivirus scan")
    print("  3. Change any passwords used on this system")
    print()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCleanup interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")