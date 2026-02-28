# Quick Start Guide: .webapp Format

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install PyQt6 PyQt6-WebEngine
```

### 2. Create Your First App

**Option A: Use the sample todo app**
```bash
python3 package_webapp.py sample_app/ my_app.webapp
python3 webapp_launcher.py my_app.webapp
```

**Option B: Create a minimal app**
```bash
mkdir my_web_app
cd my_web_app

# Create index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        h1 { color: #667eea; }
    </style>
</head>
<body>
    <h1>🚀 My First Web App</h1>
    <p>Running as a portable .webapp file!</p>
</body>
</html>
EOF

# Create manifest
cat > manifest.json << 'EOF'
{
  "name": "My App",
  "version": "1.0.0",
  "width": 600,
  "height": 400
}
EOF

# Package it
cd ..
python3 package_webapp.py my_web_app/ my_app.webapp

# Run it
python3 webapp_launcher.py my_app.webapp
```

## Project Structure

Your app directory should look like:

```
my_app/
├── index.html          ← REQUIRED: Main HTML file
├── manifest.json       ← OPTIONAL: App configuration
├── styles.css          ← OPTIONAL: Stylesheets
├── script.js           ← OPTIONAL: JavaScript
├── icon.svg            ← OPTIONAL: Window icon
└── assets/             ← OPTIONAL: Images, data, etc.
```

## manifest.json Essentials

```json
{
  "name": "My App Name",
  "version": "1.0.0",
  "width": 800,
  "height": 600,
  "icon": "icon.svg"
}
```

## What You Get

✅ Single `.webapp` file (ZIP archive)
✅ Works on Windows, Mac, Linux
✅ No installation required
✅ Full web APIs (localStorage, canvas, etc.)
✅ Chromium rendering engine
✅ Auto-cleanup (temporary files deleted on close)
✅ Portable (share the .webapp file easily)

## Examples Included

### 1. Todo App (`sample_app/`)
- Add/delete todos
- localStorage persistence
- Beautiful gradient UI
- Full responsive design

```bash
python3 package_webapp.py sample_app/ todo.webapp
python3 webapp_launcher.py todo.webapp
```

## File Type Registration (Optional)

Double-click your `.webapp` files directly:

```bash
# One-time setup
python3 webapp_launcher.py --register

# Then just double-click .webapp files!
```

## Distribution

To share your app:

1. Package it: `python3 package_webapp.py myapp/ myapp.webapp`
2. Share the `myapp.webapp` file (it's just a ZIP!)
3. Users run: `python3 webapp_launcher.py myapp.webapp`

That's it! No installer needed.

## Keyboard Shortcuts

- **F12**: Open developer tools
- **Ctrl+Shift+I**: Inspector
- **Ctrl+R**: Reload page
- **Ctrl+W**: Close app

## Debugging

```javascript
// In your JavaScript
console.log('Debug message');

// Press F12 to open dev tools and see console output
```

## Common Patterns

### Add a Button
```html
<button onclick="alert('Clicked!')">Click Me</button>
```

### Save Data Locally
```javascript
// Save
localStorage.setItem('myData', JSON.stringify({name: 'John'}));

// Load
const data = JSON.parse(localStorage.getItem('myData'));
```

### Fetch Data from Web
```javascript
fetch('https://api.example.com/data')
  .then(r => r.json())
  .then(data => console.log(data));
```

### Add CSS
```html
<link rel="stylesheet" href="styles.css">
```

### Add JavaScript
```html
<script src="script.js"></script>
```

## Next Steps

1. Explore the `sample_app/` code
2. Modify it to create your own app
3. Use `package_webapp.py` to create `.webapp` files
4. Share with others - just send the .webapp file!

## Need Help?

Check `README.md` for detailed documentation including:
- Complete manifest.json reference
- Available Web APIs
- Advanced features (Service Workers, etc.)
- Troubleshooting
- Security considerations

Happy app building! 🎉
