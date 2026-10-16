import os
import sys
import json
import argparse
import re
from pathlib import Path
import urllib.parse

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from google.oauth2 import service_account
    import google.auth.transport.requests
    import requests
except ImportError:
    print("[ERROR] Required Python packages not found.")
    print("Please install them using: pip install google-auth requests")
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


def load_env(project_root):
    env_vars = {}
    for env_file in ['.env', '.env.local']:
        p = project_root / env_file
        if p.exists():
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip().strip('\'"')
    return env_vars


def detect_package_name(project_root):
    # 1. Check app.json (Expo / React Native)
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

    # 2. Check build.gradle (Native Android / Flutter / Capacitor)
    build_gradle = project_root / 'android' / 'app' / 'build.gradle'
    if build_gradle.exists():
        try:
            with open(build_gradle, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check applicationId
                m = re.search(r'applicationId\s+["\']([^"\']+)["\']', content)
                if m:
                    return m.group(1)
                # Check namespace
                m = re.search(r'namespace\s+["\']([^"\']+)["\']', content)
                if m:
                    return m.group(1)
        except Exception:
            pass

    return None


def clean_bucket_name(raw_bucket):
    if not raw_bucket:
        return None
    bucket = raw_bucket.strip()
    if bucket.startswith('gs://'):
        bucket = bucket[5:]
    if '/' in bucket:
        bucket = bucket.split('/')[0]
    return bucket


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


def fetch_play_store_stats(root_arg='.', bucket_arg=None, package_arg=None, key_file_arg=None, output_arg=None):
    project_root = find_project_root(root_arg)
    env = load_env(project_root)

    # 1. Bucket
    raw_bucket = (
        bucket_arg
        or env.get('PLAY_STORE_STATS_BUCKET')
        or os.environ.get('PLAY_STORE_STATS_BUCKET')
        or env.get('GCS_STATS_BUCKET')
    )
    bucket = clean_bucket_name(raw_bucket)
    if not bucket:
        print("[ERROR] Cloud Storage Bucket not configured.")
        print("Set PLAY_STORE_STATS_BUCKET=pubsite_prod_... in your .env file or pass --bucket.")
        sys.exit(1)

    # 2. Package Name
    package_name = (
        package_arg
        or env.get('PLAY_STORE_PACKAGE_NAME')
        or env.get('PACKAGE_NAME')
        or detect_package_name(project_root)
    )
    if not package_name:
        print("[ERROR] Android package name could not be detected.")
        print("Please pass --package <com.example.app> or set PACKAGE_NAME in .env.")
        sys.exit(1)

    # 3. Key file
    key_file = find_key_file(project_root, key_file_arg or env.get('GOOGLE_APPLICATION_CREDENTIALS'))
    if not key_file:
        print(f"[ERROR] Service account key file not found in {project_root}.")
        print("Ensure 'google-service-account.json' exists in your project root or pass --key-file.")
        sys.exit(1)

    # 4. Output Directory
    out_dir = Path(output_arg) if output_arg else (project_root / 'stats_data')
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Project Root: {project_root}")
    print(f"Bucket: {bucket}")
    print(f"Target Package: {package_name}")
    print(f"Key File: {key_file.name}")
    print(f"Output Directory: {out_dir}")

    creds = service_account.Credentials.from_service_account_file(
        str(key_file),
        scopes=['https://www.googleapis.com/auth/devstorage.read_only']
    )
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    headers = {'Authorization': f'Bearer {creds.token}'}

    print("\nQuerying Google Cloud Storage for reports...")
    url = f'https://storage.googleapis.com/storage/v1/b/{bucket}/o'
    page_token = None
    all_files = []
    while True:
        params = {}
        if page_token:
            params['pageToken'] = page_token
        resp = requests.get(url, headers=headers, params=params).json()
        for item in resp.get('items', []):
            if package_name in item['name']:
                all_files.append(item['name'])
        page_token = resp.get('nextPageToken')
        if not page_token:
            break

    print(f"Found {len(all_files)} report files for {package_name}.")
    if not all_files:
        print("Note: No report files found for this package yet. Play Store generates daily reports once traffic occurs.")
        return

    for fpath in all_files:
        encoded_path = urllib.parse.quote(fpath, safe='')
        download_url = f'https://storage.googleapis.com/storage/v1/b/{bucket}/o/{encoded_path}?alt=media'
        r = requests.get(download_url, headers=headers)
        
        rel_path = out_dir / fpath
        rel_path.parent.mkdir(parents=True, exist_ok=True)
        with open(rel_path, 'wb') as f:
            f.write(r.content)
        print(f"  ✓ {fpath} ({len(r.content)} bytes)")

    print(f"\n[SUCCESS] All statistics downloaded to: {out_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch Google Play Store stats from Cloud Storage bucket.")
    parser.add_argument('--root', default='.', help="Project root directory")
    parser.add_argument('--bucket', help="GCS Bucket name or gs://... URI (reads PLAY_STORE_STATS_BUCKET from .env by default)")
    parser.add_argument('--package', help="Android package name (auto-detected by default)")
    parser.add_argument('--key-file', help="Path to google-service-account.json")
    parser.add_argument('--output', help="Output directory for CSV files (default: stats_data/)")
    args = parser.parse_args()

    fetch_play_store_stats(
        root_arg=args.root,
        bucket_arg=args.bucket,
        package_arg=args.package,
        key_file_arg=args.key_file,
        output_arg=args.output
    )
