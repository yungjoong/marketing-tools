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

    if not os.path.exists(source_dir):
        print(f"Source directory not found: {source_dir}")
        return

    for lang in os.listdir(source_dir):
        lang_path = os.path.join(source_dir, lang)
        if not os.path.isdir(lang_path):
            continue
            
        gp_lang = 'ko-KR' if lang == 'ko' else 'en-US' if lang == 'en' else lang
        lang_target = metadata_root / gp_lang / 'images'
        
        print(f"Processing {lang} -> {gp_lang}")
        
        # 1. Feature Graphic
        feature_name = f"feature_graphic_{lang}.png"
        feature_src = os.path.join(lang_path, feature_name)
        if os.path.exists(feature_src):
            os.makedirs(lang_target, exist_ok=True)
            shutil.copy2(feature_src, lang_target / 'featureGraphic.png')
            print(f"  [Match] Feature Graphic")

        # 2. App Icon
        icon_paths = [
            project_root / 'assets' / 'icon' / 'icon.png',
            project_root / 'android' / 'app' / 'src' / 'main' / 'res' / 'mipmap-xxxhdpi' / 'ic_launcher.png'
        ]
        
        icon_src = next((p for p in icon_paths if p.exists()), None)
        if icon_src:
            os.makedirs(lang_target, exist_ok=True)
            shutil.copy2(icon_src, lang_target / 'icon.png')
            print(f"  [Match] App Icon from {icon_src.name}")

        # 3. Screenshots
        for src_dev, target_dev in device_map.items():
            src_dev_path = os.path.join(lang_path, src_dev)
            if not os.path.exists(src_dev_path):
                continue
                
            target_dev_path = lang_target / target_dev
            os.makedirs(target_dev_path, exist_ok=True)
            
            for file in os.listdir(src_dev_path):
                if file.endswith('.png'):
                    parts = file.split('_')
                    num = parts[-1] 
                    shutil.copy2(os.path.join(src_dev_path, file), target_dev_path / num)
                    print(f"  [Match] {src_dev} -> {target_dev}: {num}")

    print("\nDone! Assets organized in android/fastlane/metadata/android/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Directory where the dashboard ZIP was extracted.')
    parser.add_argument('--root', default='.', help='Project root directory')
    args = parser.parse_args()
    organize_assets(args.source, args.root)
