#!/usr/bin/env python3
"""
Installer for .webapp launcher system
Sets up dependencies and registers file type
"""

import sys
import os
import subprocess
import platform


def check_python():
    """Verify Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required (you have {version.major}.{version.minor})")
        return False
    print(f"✓ Python {version.major}.{version.minor}")
    return True


def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python packages...")
    
    packages = ['PyQt6', 'PyQt6-WebEngine']
    
    for package in packages:
        print(f"  Installing {package}...", end=" ")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓")
        else:
            print("✗")
            print(f"    Error: {result.stderr}")
            return False
    
    return True


def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system()
    
    if system == "Linux":
        print("\n🐧 Installing Linux dependencies...")
        distro = _detect_distro()
        
        if distro == "debian":
            packages = [
                'libqt6webenginecore6',
                'libqt6gui6',
                'libqt6core6'
            ]
            cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
        elif distro == "fedora":
            packages = ['qt6-webengine', 'qt6-qtbase']
            cmd = ['sudo', 'dnf', 'install', '-y'] + packages
        elif distro == "arch":
            packages = ['qt6-webengine', 'qt6-base']
            cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
        else:
            print("⚠ Unknown Linux distro. Install Qt6 WebEngine manually.")
            return True
        
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            print("✓ System dependencies installed")
            return True
        else:
            print("✗ Failed to install system dependencies")
            print("  You may need to run manually with sudo")
            return False
    
    elif system == "Darwin":
        print("\n🍎 macOS detected")
        print("  Checking for Homebrew...")
        result = subprocess.run(['which', 'brew'], capture_output=True)
        if result.returncode == 0:
            print("  Installing Qt6 via Homebrew...")
            subprocess.run(['brew', 'install', 'qt@6'])
            return True
        else:
            print("  Install Homebrew: /bin/bash -c \"$(curl -fsSL ...)\"\n"
                  "  Then: brew install qt@6")
            return True
    
    elif system == "Windows":
        print("\n🪟 Windows detected (no additional system dependencies needed)")
        return True
    
    return True


def _detect_distro():
    """Detect Linux distribution"""
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read().lower()
            if 'ubuntu' in content or 'debian' in content:
                return 'debian'
            elif 'fedora' in content or 'rhel' in content:
                return 'fedora'
            elif 'arch' in content:
                return 'arch'
    except:
        pass
    return 'unknown'


def verify_installation():
    """Verify all dependencies are working"""
    print("\n✔ Verifying installation...")
    
    try:
        import PyQt6
        print("  ✓ PyQt6 installed")
    except ImportError:
        print("  ✗ PyQt6 not found")
        return False
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("  ✓ PyQt6-WebEngine installed")
    except ImportError:
        print("  ✗ PyQt6-WebEngine not found")
        return False
    
    return True


def setup_file_type():
    """Register file type"""
    print("\n📋 Setting up file type registration...")
    
    launcher_path = os.path.abspath('webapp_launcher.py')
    
    if not os.path.exists(launcher_path):
        print("  ⚠ webapp_launcher.py not found in current directory")
        print("  Run: python3 install.py from the webapp directory")
        return False
    
    try:
        from webapp_launcher import register_file_type
        register_file_type()
        print("  ✓ File type registered")
        return True
    except Exception as e:
        print(f"  ⚠ Could not register file type: {e}")
        print("  You can register later with: python3 webapp_launcher.py --register")
        return True


def main():
    """Run installation"""
    print("🚀 .webapp Launcher Installation\n")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Install Python packages
    if not install_dependencies():
        print("\n❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Verify
    if not verify_installation():
        print("\n❌ Installation verification failed")
        sys.exit(1)
    
    # Setup file type
    setup_file_type()
    
    print("\n" + "=" * 50)
    print("✨ Installation complete!\n")
    print("Next steps:")
    print("  1. Create your app directory with index.html")
    print("  2. Package it: python3 package_webapp.py myapp/ myapp.webapp")
    print("  3. Run it: python3 webapp_launcher.py myapp.webapp\n")
    print("Example:")
    print("  python3 package_webapp.py sample_app/ sample.webapp")
    print("  python3 webapp_launcher.py sample.webapp\n")
    print("See QUICKSTART.md for more details!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Installation cancelled")
        sys.exit(1)
