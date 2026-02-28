#!/usr/bin/env python3
"""
.webapp Launcher - A portable web application launcher using PyQt6 and QWebEngineView
Handles file type registration and temporary extraction of .webapp archives
"""

import sys
import os
import json
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon


class WebappLauncher(QMainWindow):
    """Main window for displaying .webapp web applications"""
    
    def __init__(self, webapp_path: str):
        super().__init__()
        
        self.webapp_path = Path(webapp_path)
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self.manifest = {}
        
        # Extract webapp and load manifest
        if not self._extract_webapp():
            self._show_error("Failed to extract webapp file")
            return
        
        # Configure window
        self._setup_window()
        
        # Create web view and load HTML
        self._setup_web_view()
    
    def _extract_webapp(self) -> bool:
        """Extract .webapp (zip) to temporary directory"""
        try:
            self.temp_dir = tempfile.TemporaryDirectory(prefix="webapp_")
            extract_path = self.temp_dir.name
            
            # Verify it's a valid zip
            if not zipfile.is_zipfile(self.webapp_path):
                raise ValueError("File is not a valid ZIP archive")
            
            # Extract contents
            with zipfile.ZipFile(self.webapp_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Check for index.html
            index_html = Path(extract_path) / "index.html"
            if not index_html.exists():
                raise FileNotFoundError("index.html not found in webapp archive")
            
            # Load manifest if present
            manifest_path = Path(extract_path) / "manifest.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        self.manifest = json.load(f)
                except json.JSONDecodeError:
                    print("Warning: manifest.json is not valid JSON")
            
            return True
        
        except Exception as e:
            print(f"Error extracting webapp: {e}")
            return False
    
    def _setup_window(self):
        """Configure main window properties from manifest or defaults"""
        # Get window settings from manifest
        width = self.manifest.get('width', 1024)
        height = self.manifest.get('height', 768)
        title = self.manifest.get('name', 'Web App')
        icon_path = self.manifest.get('icon')
        
        # Set window properties
        self.setWindowTitle(title)
        self.resize(width, height)
        
        # Set icon if available
        if icon_path and self.temp_dir:
            full_icon_path = Path(self.temp_dir.name) / icon_path
            if full_icon_path.exists():
                self.setWindowIcon(QIcon(str(full_icon_path)))
        
        # Center window on screen
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.move(x, y)
    
    def _setup_web_view(self):
        """Create and configure QWebEngineView"""
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.setCentralWidget(central_widget)
        
        # Load index.html
        if self.temp_dir:
            index_path = Path(self.temp_dir.name) / "index.html"
            file_url = QUrl.fromLocalFile(str(index_path))
            self.web_view.load(file_url)
    
    def _show_error(self, message: str):
        """Display error message"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
        layout.addWidget(error_label)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Error")
        self.resize(400, 200)
    
    def closeEvent(self, event):
        """Cleanup temporary directory on close"""
        if self.temp_dir:
            try:
                self.temp_dir.cleanup()
            except Exception as e:
                print(f"Warning: Could not cleanup temp directory: {e}")
        event.accept()


def register_file_type():
    """Register .webapp file type (platform-specific)"""
    system = sys.platform
    
    if system == 'win32':
        _register_windows()
    elif system == 'darwin':
        _register_macos()
    elif system == 'linux':
        _register_linux()


def _register_windows():
    """Register .webapp file type on Windows"""
    try:
        import winreg
        
        # Get the path to this script
        launcher_path = os.path.abspath(__file__)
        
        # Create registry entries
        key = r'Software\Classes\.webapp'
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, key)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, '', 0, winreg.REG_SZ, 'webapp')
        
        # Register the application
        key = r'Software\Classes\webapp\shell\open\command'
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, key)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_WRITE) as k:
            cmd = f'"{sys.executable}" "{launcher_path}" "%1"'
            winreg.SetValueEx(k, '', 0, winreg.REG_SZ, cmd)
        
        print("✓ .webapp file type registered for Windows")
    
    except Exception as e:
        print(f"Warning: Could not register file type on Windows: {e}")


def _register_linux():
    """Register .webapp file type on Linux"""
    try:
        home = Path.home()
        apps_dir = home / '.local/share/applications'
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the path to this script
        launcher_path = os.path.abspath(__file__)
        
        # Create .desktop file
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Web App Launcher
Exec={sys.executable} {launcher_path} %F
MimeType=application/x-webapp
Categories=Utility;
NoDisplay=true
"""
        
        desktop_file = apps_dir / 'webapp-launcher.desktop'
        desktop_file.write_text(desktop_content)
        os.chmod(desktop_file, 0o755)
        
        # Register MIME type
        mime_dir = home / '.local/share/mime/packages'
        mime_dir.mkdir(parents=True, exist_ok=True)
        
        mime_content = """<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-webapp">
    <comment>Web App Package</comment>
    <glob pattern="*.webapp"/>
  </mime-type>
</mime-info>
"""
        
        mime_file = mime_dir / 'webapp.xml'
        mime_file.write_text(mime_content)
        
        # Update MIME database
        try:
            subprocess.run(['update-mime-database', str(mime_dir)], 
                         capture_output=True, timeout=5)
            subprocess.run(['update-desktop-database', str(apps_dir)],
                         capture_output=True, timeout=5)
        except Exception as e:
            print(f"Warning: Could not update MIME database: {e}")
        
        print("✓ .webapp file type registered for Linux")
    
    except Exception as e:
        print(f"Warning: Could not register file type on Linux: {e}")


def _register_macos():
    """Register .webapp file type on macOS"""
    try:
        import plistlib
        
        launcher_path = os.path.abspath(__file__)
        app_name = "WebApp Launcher"
        
        # Note: Full macOS integration requires creating a proper .app bundle
        # This is a simplified approach
        print(f"⚠ macOS registration requires manual setup:")
        print(f"  1. Create an app bundle or use Platypus")
        print(f"  2. Set {launcher_path} as the executable")
        print(f"  3. Add UTI for .webapp files")
    
    except Exception as e:
        print(f"Warning: Could not register file type on macOS: {e}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Handle command-line arguments
    if len(sys.argv) > 1:
        webapp_file = sys.argv[1]
        
        # Validate file exists and has .webapp extension
        if not os.path.exists(webapp_file):
            print(f"Error: File not found: {webapp_file}")
            sys.exit(1)
        
        if not webapp_file.endswith('.webapp'):
            print(f"Warning: File does not have .webapp extension")
        
        # Launch the webapp
        launcher = WebappLauncher(webapp_file)
        launcher.show()
    
    else:
        # No file provided - show registration dialog
        print("Webapp Launcher v1.0")
        print("\nUsage:")
        print(f"  {sys.argv[0]} <file.webapp>")
        print("\nTo register file type, run:")
        print(f"  {sys.argv[0]} --register")
        
        if len(sys.argv) > 1 and sys.argv[1] == '--register':
            register_file_type()
        else:
            # Show a simple info window
            window = QMainWindow()
            widget = QWidget()
            layout = QVBoxLayout(widget)
            
            label = QLabel("""
Webapp Launcher

Usage:
  webapp_launcher.py <file.webapp>

To register .webapp file type:
  webapp_launcher.py --register

This launcher extracts .webapp files (ZIP archives) and displays
the contained index.html in a QWebEngineView window.
            """)
            label.setMargin(20)
            layout.addWidget(label)
            window.setCentralWidget(widget)
            window.setWindowTitle("Webapp Launcher")
            window.resize(500, 300)
            window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
