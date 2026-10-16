import os
import sys
import json
import argparse
import csv
import re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


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
    return 'com.example.app'


def read_csv_rows(path):
    if not os.path.exists(path):
        return []
    for enc in ['utf-16', 'utf-16-le', 'utf-8', 'cp949']:
        try:
            with open(path, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception:
            pass
    return []


def analyze_play_store_stats(root_arg='.', package_arg=None, stats_dir_arg=None):
    project_root = find_project_root(root_arg)
    package_name = package_arg or detect_package_name(project_root)

    stats_dir = Path(stats_dir_arg) if stats_dir_arg else (project_root / 'stats_data' / 'stats')
    if not stats_dir.exists():
        print(f"[ERROR] Stats directory not found: {stats_dir}")
        print("Run 'fetch_play_store_stats.py' first to download the reports.")
        sys.exit(1)

    print("=" * 68)
    print(f" 📊 Google Play Store 통계 분석 보고서")
    print(f" 앱 패키지: {package_name}")
    print("=" * 68)

    # 1. Installs Overview
    overview_files = sorted(stats_dir.glob(f"installs/installs_{package_name}_*_overview.csv"))
    if overview_files:
        latest_file = overview_files[-1]
        rows = read_csv_rows(latest_file)
        if rows:
            print("\n[1] 기기 설치 및 활성 현황 (Overview)")
            total_installs = sum(int(r.get('Daily Device Installs', 0) or 0) for r in rows)
            total_uninstalls = sum(int(r.get('Daily Device Uninstalls', 0) or 0) for r in rows)
            total_upgrades = sum(int(r.get('Daily Device Upgrades', 0) or 0) for r in rows)
            latest_active = int(rows[-1].get('Active Device Installs', 0) or 0)
            latest_date = rows[-1].get('Date', '')

            print(f"  • 집계 기간: {rows[0].get('Date', '')} ~ {latest_date}")
            print(f"  • 현재 활성 기기 수 (Active Devices): {latest_active:,}대")
            print(f"  • 기간 내 총 설치 기기 수: {total_installs:,}건")
            print(f"  • 기간 내 삭제(이탈) 기기 수: {total_uninstalls:,}건")
            print(f"  • 기간 내 앱 업데이트 횟수: {total_upgrades:,}건")

    # 2. Devices
    device_files = sorted(stats_dir.glob(f"installs/installs_{package_name}_*_device.csv"))
    if device_files:
        rows = read_csv_rows(device_files[-1])
        devices = set(r.get('Device') for r in rows if r.get('Device'))
        if devices:
            print(f"  • 등록/테스트된 기기 모델: {', '.join(devices)}")

    # 3. Store Performance (Traffic Sources)
    traffic_files = sorted(stats_dir.glob(f"store_performance/store_performance_{package_name}_*_traffic_source.csv"))
    if traffic_files:
        rows = read_csv_rows(traffic_files[-1])
        if rows:
            print("\n[2] 스토어 등록정보 유입 및 전환 (Traffic Performance)")
            total_visitors = sum(int(r.get('Store listing visitors', 0) or 0) for r in rows)
            total_acquisitions = sum(int(r.get('Store listing acquisitions', 0) or 0) for r in rows)
            cr = (total_acquisitions / total_visitors * 100) if total_visitors > 0 else 0.0

            print(f"  • 스토어 총 방문자 수: {total_visitors:,}명")
            print(f"  • 스토어 설치 전환 수: {total_acquisitions:,}건")
            print(f"  • 전체 방문 대비 설치 전환율(CVR): {cr:.2f}%")

            # Group by traffic source
            by_source = {}
            for r in rows:
                src = r.get('Traffic source', 'Other')
                vis = int(r.get('Store listing visitors', 0) or 0)
                acq = int(r.get('Store listing acquisitions', 0) or 0)
                if src not in by_source:
                    by_source[src] = {'visitors': 0, 'acquisitions': 0}
                by_source[src]['visitors'] += vis
                by_source[src]['acquisitions'] += acq

            print("\n  [유입 채널별 상세]")
            for src, data in by_source.items():
                s_cr = (data['acquisitions'] / data['visitors'] * 100) if data['visitors'] > 0 else 0.0
                print(f"   - {src:<20}: 방문자 {data['visitors']}명 | 설치 {data['acquisitions']}건 (전환율 {s_cr:.1f}%)")

    # 4. Country Performance
    country_files = sorted(stats_dir.glob(f"store_performance/store_performance_{package_name}_*_country.csv"))
    if country_files:
        rows = read_csv_rows(country_files[-1])
        if rows:
            by_country = {}
            for r in rows:
                c = r.get('Country / region', 'Other')
                vis = int(r.get('Store listing visitors', 0) or 0)
                acq = int(r.get('Store listing acquisitions', 0) or 0)
                if c not in by_country:
                    by_country[c] = {'visitors': 0, 'acquisitions': 0}
                by_country[c]['visitors'] += vis
                by_country[c]['acquisitions'] += acq

            print("\n[3] 국가별 유입 현황")
            for c, data in by_country.items():
                print(f"   - {c:<10}: 방문자 {data['visitors']}명 | 설치 {data['acquisitions']}건")

    print("\n" + "=" * 68)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analyze Google Play Store stats CSV reports.")
    parser.add_argument('--root', default='.', help="Project root directory")
    parser.add_argument('--package', help="Android package name (auto-detected by default)")
    parser.add_argument('--stats-dir', help="Path to stats directory")
    args = parser.parse_args()

    analyze_play_store_stats(
        root_arg=args.root,
        package_arg=args.package,
        stats_dir_arg=args.stats_dir
    )
