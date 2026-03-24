import os
import shutil
import json
import argparse
from pathlib import Path

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
        'ja': 'ja-JP'
    }

    if not os.path.exists(source_dir):
        print(f"Source directory not found: {source_dir}")
        return

    # Iterate through device directories (phone, tablet7, tablet10)
    for device_dir_name in os.listdir(source_dir):
        device_path = os.path.join(source_dir, device_dir_name)
        if not os.path.isdir(device_path):
            continue
            
        print(f"Processing device directory: {device_dir_name}")
        
        # Iterate through files in the device directory
        for file in os.listdir(device_path):
            if not file.endswith('.png'):
                continue
            
            # Pattern: {device}_{lang}_{num}_{suffix}.png
            # Example: phone_en_01_main.png
            parts = file.split('_')
            if len(parts) < 3:
                print(f"  [Skip] Invalid filename format: {file}")
                continue
                
            device_type = parts[0]
            lang_code = parts[1]
            num = parts[2]
            
            gp_lang = lang_mapping.get(lang_code, lang_code)
            target_device_type = device_map.get(device_type, device_type)
            
            lang_target = metadata_root / gp_lang / 'images'
            target_dev_path = lang_target / target_device_type
            
            os.makedirs(target_dev_path, exist_ok=True)
            
            # Fastlane expects [num].png
            target_file_name = f"{num}.png"
            shutil.copy2(os.path.join(device_path, file), target_dev_path / target_file_name)
            print(f"  [Match] {file} -> {gp_lang}/{target_device_type}/{target_file_name}")

        # Note: Feature Graphic and App Icon logic could be added here if they follow a similar pattern,
        # but for now we focus on the fixed screenshot structure.

    print("\nDone! Assets organized in android/fastlane/metadata/android/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Directory where the dashboard ZIP was extracted.')
    parser.add_argument('--root', default='.', help='Project root directory')
    args = parser.parse_args()
    organize_assets(args.source, args.root)
