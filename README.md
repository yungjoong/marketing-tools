# Marketing Tools

App Store 및 Google Play 마케팅 자산을 자동화하기 위한 통합 툴킷입니다.

## 주요 기능
- **Marketing Dashboard**: `assets-config.json`을 기반으로 프레임이 씌워진 스크린샷과 피처 그래픽을 생성하는 HTML/JS 대시보드.
- **Metadata Generator**: `assets-config.json`에서 Google Play 메타데이터(제목, 설명, 변경사항 등)를 자동 생성하는 Python 스크립트.
- **Asset Organizer**: 대시보드에서 추출한 자산을 Fastlane 호환 폴더 구조로 정리하는 Python 스크립트.
- **Fastlane Integration**: 모바일 프로젝트에 쉽게 통합할 수 있는 공용 Fastlane Lane 제공 (`Fastfile.common`, `Appfile.shared`).

---

## 프로젝트 구조
- `dashboard/`: 자산 생성 대시보드 (HTML/JS).
- `scripts/`: 자동화 스크립트 (Python).
- `fastlane/`: 공유 설정 및 Lane 모음.
- `test_driver/`: 스크린샷 자동화를 위한 통합 테스트 샘플.

---

## 사용 방법

### 1. 설정 파일 생성 (`assets-config.json`)
마케팅 자산의 **Single Source of Truth**입니다. 프로젝트의 `apps/mobile/tools/` 폴더에 생성하는 것을 권장합니다.
(탐색 우선순위: `tools/`, `./`, `tools/marketing-tools/`)

> **참고**: `dashboard/assets-config.sample.json`에 상세한 주석이 포함된 템플릿이 있습니다.

### 2. 마케팅 대시보드 실행
대시보드를 통해 스크린샷과 피처 그래픽을 미리보고 다운로드할 수 있습니다.

```bash
# 프로젝트 루트(jubjub-app)에서 실행
npx serve .
```
접속 주소: `http://localhost:3000/apps/mobile/tools/marketing-tools/dashboard/`

### 3. Google Play 메타데이터 생성
`assets-config.json`의 내용을 바탕으로 `android/fastlane/metadata` 폴더에 텍스트 파일들을 생성합니다.

```bash
# marketing-tools 폴더 진입 후
python scripts/generate_gp_metadata.py --root ../../../
```

---

## 📸 스크린샷 및 자산 규칙

### 시나리오(Scenarios) 설정
Google Play는 기기당 4~8개의 스크린샷을 허용합니다. `assets-config.json`에서 이를 정의합니다.
- `name`: 스크린샷 위에 덮어씌워질 **마케팅 슬로건**.
- `desc`: 스크린샷을 찍을 때 앱의 상태를 설명하는 **가이드**. (마케팅 문구가 아닌 캡처 지시서)

### 파일명 패턴
설정 파일의 `screenshotPathPattern`에 정의된 규칙을 따릅니다.
예: `store-assets/screenshots/{device}/{device}_{lang}_{num}_{suffix}.png`

---

## 🚀 Fastlane 통합 (Android)

### `android/fastlane/Appfile` 설정
```ruby
eval(File.read("../../apps/mobile/tools/marketing-tools/fastlane/Appfile.shared"))
package_name("com.yungjoong.jubjub")
```

### `android/fastlane/Fastfile` 설정
```ruby
import "../../apps/mobile/tools/marketing-tools/fastlane/Fastfile.common"

platform :android do
  # 사용 가능한 주요 Lane:
  # fastlane android generate_metadata      -> Play Store 텍스트 메타데이터 생성
  # fastlane android prepare_marketing_assets -> 전체 자산 파이프라인 실행 (스크립트 포함)
end
```

---
💡 **Tip:** 모든 언어의 자산을 한 번에 관리하려면 대시보드 하단의 "모든 언어 통합 패키지 다운로드" 기능을 사용하세요.
