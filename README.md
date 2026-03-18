# Cyber Maze Backdoor Lab

## Files Structure
- `/game` - Game source files (for building EXE)
- `/server` - Listener script (run on attacker machine)
- `/tools` - Utility scripts
- `/docs` - Documentation
- `/dist` - Generated EXE (created after build)

## Usage
1. Update IP in `game/client_agent.py`
2. Build EXE: `cd game && build_exe.bat`
3. Start listener: `python server/listener.py`
4. Run EXE on victim PC