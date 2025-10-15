import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    """Create a professional desktop shortcut for the app."""
    
    project_dir = Path(__file__).parent.resolve()
    desktop = Path.home() / "Desktop"
    
    # Create a batch file that runs the app
    batch_content = f'''@echo off
title CRM Lab
echo.
echo Launching CRM Lab...
echo Keep this window open while using the application.
echo.
cd /d "{project_dir}"
python "Run-app-V1.py"
echo.
echo Application closed. Press any key to exit...
pause >nul
'''
    
    batch_path = desktop / "CRM Lab.bat"
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    # Try to create a proper shortcut with icon (optional)
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = desktop / "CRM Lab.lnk"
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(batch_path)
        shortcut.WorkingDirectory = str(project_dir)
        
        # Use custom icon if available, otherwise use default
        icon_path = project_dir / "icon.ico"
        if icon_path.exists():
            shortcut.IconLocation = str(icon_path) + ",0"
        else:
            shortcut.IconLocation = "python.exe,0"  # Default Python icon
            
        shortcut.save()
        
        print("✅ Professional shortcut created!")
        print(f"📁 Desktop shortcut: CRM Lab.lnk")
        print(f"🔧 Batch file: CRM Lab.bat")
        
    except ImportError:
        print("✅ Batch file created!")
        print(f"📁 File: {batch_path}")
        print("💡 To install icon support: pip install pywin32")

if __name__ == "__main__":
    create_desktop_shortcut()
    