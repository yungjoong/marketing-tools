# Marketing Tools

A unified toolkit for automating App Store and Google Play marketing assets.

## Features
- **Marketing Dashboard**: HTML/JS dashboard to generate framed screenshots and feature graphics.
- **Metadata Generator**: Python script to generate Google Play metadata from `assets-config.json`.
- **Asset Organizer**: Python script to organize extracted dashboard assets into Fastlane-compatible folders.
- **Fastlane Integration**: Common Fastlane lanes for easy integration into any Flutter/Mobile project.

## Project Structure
- `dashboard/`: The HTML/JS asset generator.
- `scripts/`: Python automation scripts.
- `fastlane/`: Common `Fastfile.common` for shared lanes.

## How to use in your project

### 1. Add as a Submodule
```bash
git submodule add https://github.com/yungjoong/marketing-tools.git tools/marketing-tools
```

### 2. Create `assets-config.json`
Create `tools/assets-config.json` in your project root (see `dashboard/assets-config.sample.json` for reference).

### 3. Integrate with Fastlane
In your project's `android/fastlane/Fastfile`, import the common lanes:

```ruby
import "../../tools/marketing-tools/fastlane/Fastfile.common"

platform :android do
  lane :prepare_assets do
    generate_metadata # From Fastfile.common
  end
  
  lane :organize do |options|
    organize_assets(source: options[:source]) # From Fastfile.common
  end
end
```

### 4. Run Dashboard
```bash
npx serve .
```
Access the dashboard at `http://localhost:3000/tools/marketing-tools/dashboard/MARKETING_DASHBOARD.html`
