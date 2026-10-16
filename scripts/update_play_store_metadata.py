import os
import sys
import json
import argparse
import re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("[ERROR] Required Python packages not found.")
    print("Please install them using: pip install google-api-python-client google-auth")
    sys.exit(1)


def find_project_root(start_path='.'):
    current = Path(start_path).resolve()
    for _ in range(5):
        if (current / 'package.json').exists() or (current / 'pubspec.yaml').exists() or (current / 'app.json').exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return Path('.').resolve()


def detect_package_name(project_root):
    app_json = project_root / 'app.json'
    if app_json.exists():
        try:
            with open(app_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pkg = data.get('expo', {}).get('android', {}).get('package')
                if pkg:
                    return pkg
        except Exception:
            pass

    build_gradle = project_root / 'android' / 'app' / 'build.gradle'
    if build_gradle.exists():
        try:
            with open(build_gradle, 'r', encoding='utf-8') as f:
                content = f.read()
                m = re.search(r'applicationId\s+["\']([^"\']+)["\']', content)
                if m:
                    return m.group(1)
                m = re.search(r'namespace\s+["\']([^"\']+)["\']', content)
                if m:
                    return m.group(1)
        except Exception:
            pass
    return None


def find_key_file(project_root, custom_path=None):
    if custom_path and os.path.exists(custom_path):
        return Path(custom_path)
    candidates = [
        project_root / 'google-service-account.json',
        project_root / 'tools' / 'google-service-account.json',
        project_root / 'android' / 'google-service-account.json',
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def find_config_file(project_root, custom_path=None):
    if custom_path and os.path.exists(custom_path):
        return Path(custom_path)
    candidates = [
        project_root / 'tools' / 'assets-config.json',
        project_root / 'tools' / 'marketing-tools' / 'assets-config.json',
        project_root / 'assets-config.json',
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


LOCALE_MAP = {
    'ko': 'ko-KR',
    'en': 'en-US',
    'ja': 'ja-JP',
    'zh': 'zh-CN',
    'ru': 'ru-RU',
    'es': 'es-ES',
    'vi': 'vi'
}


def update_play_store_metadata(root_arg='.', package_arg=None, key_file_arg=None, config_arg=None):
    project_root = find_project_root(root_arg)

    package_name = package_arg or detect_package_name(project_root)
    if not package_name:
        print("[ERROR] Android package name could not be detected. Pass --package <name>.")
        sys.exit(1)

    key_file = find_key_file(project_root, key_file_arg)
    if not key_file:
        print(f"[ERROR] Service account key not found in {project_root}. Pass --key-file.")
        sys.exit(1)

    config_file = find_config_file(project_root, config_arg)
    if not config_file:
        print(f"[ERROR] assets-config.json not found in {project_root}. Pass --config.")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    print(f"Project Root: {project_root}")
    print(f"Target Package: {package_name}")
    print(f"Key File: {key_file.name}")
    print(f"Config File: {config_file.name}")

    print("\n[1/4] Authenticating with Google Play Developer API...")
    creds = service_account.Credentials.from_service_account_file(
        str(key_file),
        scopes=['https://www.googleapis.com/auth/androidpublisher']
    )
    service = build('androidpublisher', 'v3', credentials=creds)

    print(f"[2/4] Creating new edit session for {package_name}...")
    edit = service.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit['id']
    print(f"       Edit ID: {edit_id}")

    try:
        print("\n[3/4] Updating store listings from config...")
        for lang_info in config.get('languages', []):
            code = lang_info['code']
            locale = LOCALE_MAP.get(code, code)

            title = lang_info['title'][:30]
            short_desc = lang_info['shortDescription'][:80]
            full_desc = lang_info['fullDescription'][:4000]

            print(f"\n--- [{locale}] ---")
            print(f"Title ({len(title)} chars): {title}")
            print(f"Short Desc ({len(short_desc)} chars): {short_desc}")

            body = {
                'language': locale,
                'title': title,
                'shortDescription': short_desc,
                'fullDescription': full_desc
            }

            service.edits().listings().update(
                packageName=package_name,
                editId=edit_id,
                language=locale,
                body=body
            ).execute()
            print(f"✓ Listing updated for {locale}")

        print("\n[4/4] Committing edit session to Google Play Console...")
        commit_res = service.edits().commit(packageName=package_name, editId=edit_id).execute()
        print("\n[SUCCESS] Successfully committed changes to Google Play Store!")
        print(f"Commit ID: {commit_res.get('id')}")

    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        print("Rolling back edit session...")
        try:
            service.edits().delete(packageName=package_name, editId=edit_id).execute()
        except Exception:
            pass
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upload text metadata to Google Play Console.")
    parser.add_argument('--root', default='.', help="Project root directory")
    parser.add_argument('--package', help="Android package name (auto-detected by default)")
    parser.add_argument('--key-file', help="Path to google-service-account.json")
    parser.add_argument('--config', help="Path to assets-config.json")
    args = parser.parse_args()

    update_play_store_metadata(
        root_arg=args.root,
        package_arg=args.package,
        key_file_arg=args.key_file,
        config_arg=args.config
    )
