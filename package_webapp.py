#!/usr/bin/env python3
"""
Webapp Packager - Create .webapp packages from web application directories

Usage:
    python package_webapp.py <source_dir> <output.webapp> [--icon=path/to/icon.png]
"""

import sys
import json
import zipfile
import argparse
from pathlib import Path


def create_webapp(source_dir: Path, output_file: Path, icon_path: Path = None) -> bool:
    """
    Create a .webapp package from a directory
    
    Args:
        source_dir: Directory containing index.html and other assets
        output_file: Path to output .webapp file
        icon_path: Optional path to icon file to include
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate source directory
        source_dir = Path(source_dir)
        if not source_dir.is_dir():
            print(f"Error: Source directory not found: {source_dir}")
            return False
        
        # Check for index.html
        index_html = source_dir / "index.html"
        if not index_html.exists():
            print(f"Error: index.html not found in {source_dir}")
            return False
        
        # Create or update manifest.json
        manifest_path = source_dir / "manifest.json"
        if manifest_path.exists():
            print(f"Using existing manifest.json")
        else:
            print(f"Creating default manifest.json")
            manifest = {
                "name": source_dir.name,
                "version": "1.0.0",
                "description": "A web application",
                "width": 1024,
                "height": 768
            }
            manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Load and display manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            print(f"App name: {manifest.get('name', 'Unnamed')}")
            print(f"Version: {manifest.get('version', 'unknown')}")
            print(f"Size: {manifest.get('width', 1024)}x{manifest.get('height', 768)}")
        
        # Create zip file
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nPackaging webapp to: {output_file}")
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from source directory
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
                    print(f"  + {arcname}")
        
        file_size_kb = output_file.stat().st_size / 1024
        print(f"\n✓ Successfully created {output_file} ({file_size_kb:.1f} KB)")
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Package a web application into .webapp format'
    )
    parser.add_argument(
        'source',
        help='Source directory containing index.html'
    )
    parser.add_argument(
        'output',
        help='Output .webapp file path'
    )
    parser.add_argument(
        '--icon',
        help='Optional icon file to include in package'
    )
    
    args = parser.parse_args()
    
    icon_path = Path(args.icon) if args.icon else None
    success = create_webapp(Path(args.source), Path(args.output), icon_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
