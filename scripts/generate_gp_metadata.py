import json
import os
import argparse
import sys
from pathlib import Path

# Force UTF-8 output on Windows to avoid Fastlane encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def generate_metadata(project_root_str):
    project_root = Path(project_root_str).absolute()
    
    # Try multiple common paths for assets-config.json
    config_paths = [
        project_root / 'tools' / 'assets-config.json',
        project_root / 'tools' / 'marketing-tools' / 'assets-config.json',
        project_root / 'assets-config.json'
    ]
    
    config_path = None
    for p in config_paths:
        if p.exists():
            config_path = p
            break

    if not config_path:
        print(f"Config file not found! Checked: {[str(p) for p in config_paths]}")
        return

    config_path_str = str(config_path)
    with open(config_path_str, 'r', encoding='utf-8') as f:
        config = json.load(f)

    locale_mapping = {
        'ko': 'ko-KR',
        'en': 'en-US',
        'ja': 'ja-JP',
        'es': 'es-ES',
        'vi': 'vi'
    }

    base_metadata_path = project_root / 'android' / 'fastlane' / 'metadata' / 'android'
    
    for lang in config['languages']:
        lang_code = lang['code']
        gp_locale = locale_mapping.get(lang_code, lang_code)
        
        path = base_metadata_path / gp_locale
        path.mkdir(parents=True, exist_ok=True)
        
        # Title (limit 50)
        with open(path / 'title.txt', 'w', encoding='utf-8') as f:
            f.write(lang['title'][:50])
            
        # Short description (limit 80)
        with open(path / 'short_description.txt', 'w', encoding='utf-8') as f:
            f.write(lang['shortDescription'][:80])
            
        # Full description (limit 4000)
        with open(path / 'full_description.txt', 'w', encoding='utf-8') as f:
            f.write(lang['fullDescription'])
            
        # Changelog (limit 500)
        changelog = lang.get('changelog', '')
        if changelog:
            changelogs_path = path / 'changelogs'
            changelogs_path.mkdir(exist_ok=True)
            with open(changelogs_path / 'default.txt', 'w', encoding='utf-8') as f:
                f.write(changelog[:500])
            
        print(f"Generated metadata for {gp_locale}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='Project root directory')
    args = parser.parse_args()
    generate_metadata(args.root)
