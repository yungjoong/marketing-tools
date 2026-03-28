import os
import shutil
import json
import argparse
import sys
from pathlib import Path

# Force UTF-8 output on Windows to avoid Fastlane encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def organize_assets(source_dir, project_root_str):
    project_root = Path(project_root_str).absolute()
    metadata_root = project_root / 'android' / 'fastlane' / 'metadata' / 'android'
    
    device_map = {
        'phone': 'phoneScreenshots',
        'tablet7': 'sevenInchScreenshots',
        'tablet10': 'tenInchScreenshots'
    }

    lang_mapping = {
        'ko': 'ko-KR',
        'en': 'en-US',
        'ja': 'ja-JP',
        'de': 'de-DE',
        'ru': 'ru-RU',
        'es': 'es-ES',
        'zh': 'zh-CN',
        'fr': 'fr-FR',
        'pt': 'pt-BR',
        'vi': 'vi'
    }

    source_path = Path(source_dir)
    if not source_path.is_absolute():
        source_path = project_root / source_dir
    
    if not source_path.exists():
        print(f"Source directory not found: {source_path}")
        return

    print(f"Scanning source directory: {source_path}")
    
    # Use os.walk for recursive search (supports lang/device structure)
    for root, dirs, files in os.walk(str(source_path)):
        for file in files:
            if not file.endswith('.png'):
                continue
            
            # Pattern check: {device}_{lang}_{num}_{suffix}.png
            # Example: phone_en_01_main.png or phone_en_01.png
            parts = file.replace('.png', '').split('_')
            
            # Special case: Icon and Feature Graphic
            if file == 'app_icon.png':
                # Copy to all supported languages by default (or just ko-KR for now)
                # GP requires icon.png in [lang]/images/icon.png
                for lang_code, gp_lang in lang_mapping.items():
                    target_path = metadata_root / gp_lang / 'images'
                    os.makedirs(target_path, exist_ok=True)
                    shutil.copy2(os.path.join(root, file), target_path / 'icon.png')
                print(f"  [Match] {file} -> icon.png (All languages)")
                continue

            if file.startswith('feature_graphic_'):
                lang_code = file.replace('feature_graphic_', '').replace('.png', '')
                gp_lang = lang_mapping.get(lang_code, lang_code)
                target_path = metadata_root / str(gp_lang) / 'images'
                os.makedirs(target_path, exist_ok=True)
                shutil.copy2(os.path.join(root, file), target_path / 'featureGraphic.png')
                print(f"  [Match] {file} -> {gp_lang}/featureGraphic.png")
                continue

            if len(parts) < 3:
                continue
                
            # Heuristic: device is usually the first part
            device_candidates = ['phone', 'tablet7', 'tablet10']
            device_type = None
            for cand in device_candidates:
                if parts[0].startswith(cand):
                    device_type = cand
                    break
            
            if not device_type:
                continue

            lang_code = parts[1]
            num = parts[2]
            
            gp_lang = lang_mapping.get(lang_code, lang_code)
            target_device_type = device_map.get(device_type)
            
            if not gp_lang or not target_device_type:
                continue
                
            lang_target = metadata_root / str(gp_lang) / 'images'
            target_dev_path = lang_target / str(target_device_type)
            
            os.makedirs(target_dev_path, exist_ok=True)
            
            # Fastlane expects [num].png for screenshots
            if num.isdigit():
                target_file_name = f"{int(num)}.png"
            else:
                target_file_name = f"{num}.png"
                
            try:
                shutil.copy2(os.path.join(root, file), target_dev_path / target_file_name)
                print(f"  [Match] {file} -> {gp_lang}/{target_device_type}/{target_file_name}")
            except Exception as e:
                print(f"  [Error] Failed to copy {file} to {target_dev_path / target_file_name}: {e}")
                raise

    print("\nDone! Assets organized in android/fastlane/metadata/android/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Directory where the dashboard ZIP was extracted.')
    parser.add_argument('--root', default='.', help='Project root directory')
    args = parser.parse_args()
    organize_assets(args.source, args.root)
