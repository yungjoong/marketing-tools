# Marketing Tools

A unified toolkit for automating App Store and Google Play marketing assets.

## Features
- **Marketing Dashboard**: HTML/JS dashboard to generate framed screenshots and feature graphics.
- **Metadata Generator**: Python script to generate Google Play metadata from `assets-config.json`.
- **Asset Organizer**: Python script to organize extracted dashboard assets into Fastlane-compatible folders.
- **Fastlane Integration**: Common Fastlane lanes for easy integration into any Mobile project.

## Project Structure
- `dashboard/`: The HTML/JS asset generator dashboard.
- `scripts/`: Python automation scripts.
- `fastlane/`: Common `Fastfile.common` and `Appfile.shared` for shared configurations.
- `test_driver/`: Generic `integration_test.dart` for screenshot automation.

---

## How to use in your project

### 1. Add as a Submodule
```bash
git submodule add https://github.com/yungjoong/marketing-tools.git tools/marketing-tools
git submodule update --init --recursive
```

### 2. Create `tools/assets-config.json`

This is the **single source of truth** for all marketing assets.  
Create `tools/assets-config.json` at your project root.

> **Reference**: See `tools/marketing-tools/dashboard/assets-config.sample.json` for a fully annotated template.  
> The sample file contains `_INSTRUCTIONS_FOR_AI` and `_*_note` fields that explain every rule — remove them in your actual config.

#### Field-by-field guide

---

##### `scenarios` — Screenshot capture plan

Google Play allows **4 to 8 screenshots** per device type. Define exactly as many scenarios as your project needs.

Each scenario has two fields with **distinct purposes**:

| Field | Purpose | Example |
|---|---|---|
| `name` | **Marketing slogan** — Short, catchy headline printed as overlay text ON the screenshot image in the dashboard template. Must be compelling, NOT a feature label. | `"Think Ahead, Win Big!"` ✅ / `"Game Board"` ❌ |
| `desc` | **Screenshot capture guide** — Describes EXACTLY what state the app must be in when the screenshot is taken. Used by the person or automation tool taking the screenshot. NOT a marketing description. | `"Open AI vs Player game, Hard difficulty, 8x8 board, mid-game with 20+ stones placed."` |

```json
"scenarios": {
  "01": {
    "name": "Think Ahead, Win Big!",
    "desc": "Navigate to the main menu screen. Both 'VS AI' and '2P' buttons visible. No dialogs open."
  },
  "02": {
    "name": "Challenge a Powerful AI",
    "desc": "Open game setup dialog with '1P vs AI' mode, Hard difficulty, 8x8 board selected."
  },
  "03": {
    "name": "Every Move Matters",
    "desc": "AI vs Player game in progress. Mid-game state: 8x8 board with 24+ stones. Score: Black 14, White 12."
  },
  "04": {
    "name": "Play With Friends",
    "desc": "Local 2-player game in progress. 8x8 board with stones placed, both player scores visible."
  }
}
```

> ⚠️ The number of entries in `scenarios` must match the length of the `screens` array in each language entry.  
> `assets.suffixes` must also have the same keys.

---

##### `languages[].screens` — Screenshot overlay texts

The `screens` array contains the **translated marketing slogans** for each screenshot, in the same order as `scenarios`.  
The length of `screens` **must equal** the number of scenarios defined.

```json
"screens": [
  "Think Ahead, Win Big!",         // → overlay for screenshot 01
  "Challenge a Powerful AI",       // → overlay for screenshot 02
  "Every Move Matters",            // → overlay for screenshot 03
  "Play With Friends"              // → overlay for screenshot 04
]
```

---

##### `languages[].fullDescription` — ASO-optimized store description

Write as an **ASO (App Store Optimization) description**, not just a plain feature list:

1. **Open with the app name + category keyword** (most important for search ranking)
2. **List key features** as bullet points (✔ or •)
3. **Include relevant search keywords** naturally within the text
4. **Mention unique differentiators** (e.g., board size options, offline play, no ads)
5. **Aim for 300+ characters minimum** — short descriptions hurt ASO ranking
6. Max 4000 characters

**Bad example** ❌:
```
"Enjoy the traditional Reversi game on your mobile device."
```

**Good example** ✅:
```
"리버시(오델로) — 클래식 전략 보드게임을 스마트폰에서!\n\n✔ 3단계 AI 난이도 (연습/보통/고수)\n✔ 4x4, 6x6, 8x8 세 가지 보드 크기\n✔ 로컬 2인 대전 지원\n✔ 타이머 설정 (1분/3분/5분)\n✔ 무르기(Undo) 기능\n✔ 한국어, 영어, 일본어, 스페인어, 프랑스어 지원\n\n리버시는 간단한 규칙이지만 깊은 전략이 필요한 보드게임입니다..."
```

---

##### `languages[].title` — Store listing title

- Max **30 characters**
- No promotional words: ~~Free~~, ~~Best~~, ~~No Ads~~, ~~#1~~
- Include the primary keyword (app name / game genre)

---

##### `languages[].shortDescription` — One-liner

- Max **80 characters**
- Should contain the primary keyword and a clear value proposition

---

### 3. Fastlane Integration (Android)

#### Appfile
```ruby
eval(File.read("../../tools/marketing-tools/fastlane/Appfile.shared"))
package_name("com.your.app.id")
```

#### Fastfile
```ruby
import "../../tools/marketing-tools/fastlane/Fastfile.common"

platform :android do
  # Available lanes from Fastfile.common:
  #   fastlane android generate_metadata      → Generate Play Store text metadata
  #   fastlane android capture_all_screenshots → Capture screenshots (requires emulators)
  #   fastlane android prepare_marketing_assets → Full asset pipeline
end
```

---

### 4. Run the Marketing Dashboard

```bash
# From project root
npx serve .
```
Access the dashboard at `http://localhost:3000/tools/marketing-tools/dashboard/`

The dashboard reads `tools/assets-config.json` automatically and lets you:
- Preview framed screenshots per language
- Generate and download feature graphics
- Download all marketing assets as a ZIP

---

### 5. Screenshot Count Validation

When updating `assets-config.json`, always verify consistency:

| Field | Required |
|---|---|
| `scenarios` | 4–8 entries |
| `assets.suffixes` | Same keys as `scenarios` |
| Each `language[].screens` | Same length as `scenarios` count |

**Example with 6 screenshots:**
```json
"scenarios": { "01": {...}, "02": {...}, "03": {...}, "04": {...}, "05": {...}, "06": {...} },
"assets": { "suffixes": { "01": "main", "02": "gameplay", "03": "setup", "04": "multiplayer", "05": "settings", "06": "result" } },
"languages": [
  { "screens": ["Slogan 1", "Slogan 2", "Slogan 3", "Slogan 4", "Slogan 5", "Slogan 6"] }
]
```
