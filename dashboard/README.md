# App Store Assets Generator (v4.0)

HTML/JS 기반의 앱 스토어 마케팅 자산(스크린샷, 피처 그래픽) 자동 생성 도구입니다.
이제 `assets-config.json` 파일을 통해 여러 프로젝트에서 공용으로 사용할 수 있습니다.

## 📁 폴더 구조
- `MARKETING_DASHBOARD.html`: 메인 대시보드 (자산 생성 및 다운로드)
- `assets-config.sample.json`: 설정 파일 샘플
- `templates/`
  - `marketing_template.html`: 스크린샷 템플릿
  - `google_play_feature_graphic.html`: 구글 플레이 피처 그래픽 템플릿

## 🚀 사용법 (프로젝트 적용 방법)

### 1. 도구 추가
이 저장소를 프로젝트의 서브디렉토리(예: `tools/assets-generator`)에 `git submodule`로 추가하거나 소스 코드를 복사합니다.

```bash
git submodule add https://github.com/yungjoong/app-store-assets-generator.git tools/assets-generator
```

### 2. 설정 파일 생성
도구의 한 단계 상위 폴더(예: `tools/assets-config.json`)에 `assets-config.json` 파일을 생성합니다. 
(서브모듈로 사용 시 프로젝트 루트가 아닌 `tools/` 폴더에 두는 것이 관리상 깔끔하며, 도구가 기본적으로 `../assets-config.json` 경로를 탐색합니다.)

`assets-config.sample.json`의 내용을 복사하여 수정하세요.

**주요 설정 항목:**
- `appName`: 앱 이름
- `theme`: 브랜드 색상 및 그라데이션
- `assets`: 아이콘 경로 및 스크린샷 파일명 패턴
  - `screenshotPathPattern`: `{device}`, `{lang}`, `{num}`, `{suffix}` 변수를 사용할 수 있습니다.
- `languages`: 지원하는 언어별 텍스트 및 스크린샷 문구

### 3. 실행
터미널에서 프로젝트 루트 기준으로 로컬 서버를 실행합니다.

```bash
# root 폴더에서 실행
npx serve .
```

브라우저에서 대시보드에 접속합니다. (경로는 도구를 설치한 위치에 따라 다릅니다.)
`http://localhost:3000/tools/assets-generator/MARKETING_DASHBOARD.html`

설정 파일이 다른 위치에 있다면 `config` 파라미터로 지정할 수 있습니다.
`.../MARKETING_DASHBOARD.html?config=../../my-custom-config.json`

## 📸 스크린샷 파일 규칙
설정 파일의 `screenshotPathPattern`에 정의된 규칙을 따릅니다.
예: `store-assets/screenshots/{device}/{device}_{lang}_{num}.png`

파일이 없는 경우 자동으로 영문(en) 버전으로 대체(fallback)를 시도합니다.

---
💡 **Tip:** 모든 언어의 자산을 한 번에 관리하려면 대시보드 하단의 "모든 언어 통합 패키지 다운로드"를 사용하세요.
