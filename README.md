# .webapp Format & PyQt6 Launcher

A complete system for creating portable, single-file web applications that work like native desktop apps.

## Overview

`.webapp` is a custom file format (actually a ZIP archive) that packages a complete web application into a single portable file. The PyQt6 launcher automatically:

1. **Extracts** the `.webapp` file to a temporary directory
2. **Loads** the `index.html` in a `QWebEngineView` (Chromium-based)
3. **Manages** the temporary data (auto-cleanup on close)
4. **Registers** the file type with the OS for seamless opening

## System Architecture

```
user_app.webapp (ZIP archive)
    ├── index.html          (required)
    ├── styles.css          (optional)
    ├── script.js           (optional)
    ├── manifest.json       (recommended)
    ├── icon.svg            (optional, referenced in manifest)
    └── assets/             (optional)
        ├── images/
        └── data/

                    ↓

    Launcher extracts to temporary directory
            (e.g., /tmp/webapp_abc123/)

                    ↓

    QWebEngineView loads index.html
    (Full Chromium engine with all web APIs)

                    ↓

    On close: Temporary directory automatically deleted
    (Zero persistent files left behind)
```

## Installation

### Prerequisites

```bash
pip install PyQt6 PyQt6-WebEngine
```

On Linux, you may need additional dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install libqt6webenginecore6

# Fedora
sudo dnf install qt6-webengine

# Arch
sudo pacman -S qt6-webengine
```

### Setup

1. **Make launcher executable:**
   ```bash
   chmod +x webapp_launcher.py
   chmod +x package_webapp.py
   ```

2. **Register file type (optional, for double-click opening):**
   ```bash
   python3 webapp_launcher.py --register
   ```

## Usage

### Creating a .webapp Package

#### Option 1: Using the packager script

```bash
python3 package_webapp.py /path/to/app output.webapp
```

This creates a `.webapp` file from your app directory. The packager will:
- Verify `index.html` exists
- Create `manifest.json` if missing
- Compress all files into a ZIP archive

#### Option 2: Manual packaging

```bash
cd your_app_directory
zip -r ../your_app.webapp *
```

### Running a .webapp App

```bash
# Method 1: Command line
python3 webapp_launcher.py your_app.webapp

# Method 2: Double-click (after registration)
# Just double-click the .webapp file in your file manager

# Method 3: From Python
import subprocess
subprocess.run(['python3', 'webapp_launcher.py', 'your_app.webapp'])
```

## manifest.json Reference

The `manifest.json` file configures how your app appears and behaves:

```json
{
  "name": "My App",
  "version": "1.0.0",
  "description": "A brief description",
  "author": "Your Name",
  "width": 1024,
  "height": 768,
  "icon": "icon.svg",
  "minWidth": 800,
  "minHeight": 600
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | "Web App" | Window title |
| `version` | string | "1.0.0" | App version (informational) |
| `description` | string | - | App description |
| `author` | string | - | Developer name |
| `width` | number | 1024 | Initial window width (px) |
| `height` | number | 768 | Initial window height (px) |
| `icon` | string | - | Relative path to icon file (SVG/PNG) |
| `minWidth` | number | - | Minimum window width |
| `minHeight` | number | - | Minimum window height |

## Web APIs Available

Since `.webapp` apps run in a full Chromium engine via QWebEngineView, you have access to:

### ✅ Fully Supported

- **DOM/HTML5 APIs**: querySelector, createElement, etc.
- **CSS**: All modern CSS including Grid, Flexbox, Animations
- **JavaScript**: ES2020+ features, async/await, fetch API
- **LocalStorage**: Persistent data within the app
- **WebWorkers**: Multi-threading
- **Canvas/WebGL**: Graphics rendering
- **Audio/Video**: HTML5 media elements
- **Geolocation**: If permissions are granted
- **Notifications**: Desktop notifications
- **FileReader API**: Read local files (with user consent)
- **Clipboard API**: Copy/paste operations
- **IndexedDB**: Local database

### ⚠️ Limited/Restricted

- **File System Access**: Limited to app's extracted directory
- **Network**: Full network access (but no cross-origin without CORS)
- **Plugins**: Flash, Java not available
- **Camera/Microphone**: Requires explicit permissions

### ❌ Not Available

- **Node.js APIs**: No `fs`, `path`, etc. (use IPC if needed)
- **Native Libraries**: Can't directly call system libraries
- **System Commands**: No shell access

## Example: Todo App

The included `sample_app/` demonstrates a complete `.webapp` application:

```
sample_app/
├── index.html          - HTML structure
├── styles.css          - Styling (gradient background, modern UI)
├── script.js           - Vue-like app logic with localStorage
├── manifest.json       - Configuration
└── icon.svg           - App icon
```

### Features:

- ✅ Add/remove todos
- ✅ Mark complete/incomplete
- ✅ localStorage persistence
- ✅ Responsive design
- ✅ Modern ES6+ JavaScript
- ✅ Works offline completely

### Package the sample:

```bash
python3 package_webapp.py sample_app/ todo.webapp
python3 webapp_launcher.py todo.webapp
```

## Advanced Usage

### Custom File Type Registration

**Windows:**
```python
from webapp_launcher import register_file_type
register_file_type()  # Uses registry
```

**Linux:**
```bash
# Automatic via --register flag
python3 webapp_launcher.py --register
# Creates ~/.local/share/applications/webapp-launcher.desktop
# Registers MIME type application/x-webapp
```

**macOS:**
```bash
# Requires creating a .app bundle (use Platypus or similar)
# Or manually associate with this Python script
```

### Building Multi-Page Apps

Your `.webapp` can contain multiple HTML files. Use relative links:

```
app.webapp
├── index.html
├── about.html
├── contact.html
└── styles/
    └── main.css
```

In `index.html`:
```html
<nav>
  <a href="about.html">About</a>
  <a href="contact.html">Contact</a>
</nav>
```

### Using IPC for Native Features

Create a Python wrapper that enhances the webapp:

```python
# launcher_extended.py
from PyQt6.QtWebEngineCore import QWebEngineProfile

profile = launcher.web_view.page().profile()

# Create a script to expose Python functions
# (Advanced usage - requires QWebChannel)
```

## Temporary Directory Handling

The launcher uses Python's `tempfile.TemporaryDirectory()`:

- **Location**: System temp folder
  - Linux/macOS: `/tmp/`
  - Windows: `C:\Users\<user>\AppData\Local\Temp`
- **Naming**: `webapp_<random>`
- **Lifecycle**: Created on launch, deleted on close
- **Safety**: Even if app crashes, OS cleanup removes temp files

## Performance Tips

1. **Minimize Bundle Size**
   - Compress images with `ImageOptim` or similar
   - Minify CSS/JavaScript
   - Use gzip compression where possible

2. **Optimize Web Content**
   - Lazy load images
   - Code-split large JavaScript
   - Use modern image formats (WebP)

3. **Caching**
   - Use Service Workers for offline support
   - Leverage browser caching headers
   - Store computed data in localStorage

## Troubleshooting

### "index.html not found"
Ensure your `.webapp` file contains `index.html` in the root.

### App won't load
1. Check temp directory exists: `/tmp/webapp_*`
2. Verify `index.html` is valid HTML
3. Check browser console for JavaScript errors (F12)
4. Ensure all relative asset paths are correct

### Temp directory not cleaning up
The launcher attempts cleanup on close. If it fails:
```bash
# Manually clean old temp files
rm -rf /tmp/webapp_*  # Linux/macOS
REM Windows PowerShell
Remove-Item C:\Users\*\AppData\Local\Temp\webapp_* -Recurse
```

### File type registration not working
- **Linux**: Run `update-mime-database` and `update-desktop-database`
- **Windows**: Ensure running with appropriate permissions
- **macOS**: Requires app bundle (use Platypus)

## Security Considerations

- ⚠️ `.webapp` files are ZIP archives - they're not encrypted
- ⚠️ All code is visible - don't ship secrets in JavaScript
- ⚠️ localStorage is accessible - don't store sensitive data unencrypted
- ✅ Apps run in isolated Chromium sandbox
- ✅ No file system access outside extracted directory
- ✅ Same-origin policy applies

## Distribution

### Creating Distributable Apps

1. **Package your app:**
   ```bash
   python3 package_webapp.py myapp/ myapp.webapp
   ```

2. **Add version info to manifest:**
   ```json
   {
     "version": "1.0.0",
     "updateUrl": "https://example.com/check-updates"
   }
   ```

3. **Share the `.webapp` file:**
   - No installation required
   - No dependencies (except Python + PyQt6)
   - Users can run: `python3 webapp_launcher.py app.webapp`
   - Or double-click after registration

### Bundling with Python

For complete portability, create a standalone executable using `PyInstaller`:

```bash
pip install PyInstaller
pyinstaller --onefile --add-data "webapp_launcher.py:." launcher.py
```

Then distribute the single `.exe` (Windows) or binary (Linux/macOS).

## File Format Specification

### .webapp File Structure

A `.webapp` file is a standard ZIP archive with this structure:

```
Content-Type: application/x-webapp (ZIP)
Compression: DEFLATE recommended

Required:
  - index.html (entry point)

Optional:
  - manifest.json (configuration)
  - Any HTML/CSS/JS files
  - Assets directory
  - Images, fonts, data files
```

### Minimal Example

```bash
mkdir minimal_app
cd minimal_app

# Create minimal HTML
echo '<h1>Hello!</h1>' > index.html

# Package
zip hello.webapp index.html

# Run
python3 webapp_launcher.py hello.webapp
```

## Advanced Features

### localStorage Example

```javascript
// Persist user data
localStorage.setItem('user_theme', 'dark');
const theme = localStorage.getItem('user_theme');
localStorage.removeItem('user_theme');
```

### Service Workers for Offline Support

```javascript
// In your HTML
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
```

```javascript
// sw.js - Service worker
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('v1').then((cache) => {
      return cache.addAll(['index.html', 'styles.css', 'script.js']);
    })
  );
});
```

## Contributing & Extending

You can extend the launcher with:

- Auto-update checking
- Custom protocols (webapp://)
- Plugin system
- Debugging tools
- Analytics/telemetry

See the source code comments for extension points.

## License

Provided as-is for personal/commercial use. Modify as needed for your projects.

## Summary

| Feature | Details |
|---------|---------|
| **Format** | ZIP archive with .webapp extension |
| **Execution** | PyQt6 + QWebEngineView (Chromium) |
| **Storage** | Temporary extraction, auto-cleanup |
| **Registration** | Cross-platform file type registration |
| **Dependencies** | Python 3.8+, PyQt6, PyQt6-WebEngine |
| **Size** | Minimal overhead (~100KB for empty app) |
| **Portability** | Single file, cross-platform capable |
| **Security** | Chromium sandbox, no file system access |

Enjoy creating portable web apps! 🚀
