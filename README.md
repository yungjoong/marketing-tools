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
- `fastlane/`: Common `Fastfile.common` and `Appfile.shared` for shared configurations.
- `test_driver/`: Generic `integration_test.dart` for screenshot automation.

## How to use in your project

### 1. Add as a Submodule
```bash
git submodule add https://github.com/yungjoong/marketing-tools.git tools/marketing-tools
git submodule update --init --recursive
```

### 2. Fastlane Integration (Android/iOS)

#### Appfile
In your project's `android/fastlane/Appfile`, import the shared settings:
```ruby
eval(File.read("../../tools/marketing-tools/fastlane/Appfile.shared"))
package_name("com.your.app.id")
```

#### Fastfile
In your `android/fastlane/Fastfile`, import the common lanes:
```ruby
import "../../tools/marketing-tools/fastlane/Fastfile.common"

platform :android do
  # You can now use lanes like:
  # fastlane android prepare_marketing_assets
  # fastlane android capture_all_screenshots
end
```

### 3. Integrated Screenshot Test Driver
In your project's `test_driver/integration_test.dart`, use the shared implementation:
```dart
import '../tools/marketing-tools/test_driver/integration_test.dart' as shared;

Future<void> main() => shared.main();
```

### 4. Create `assets-config.json`
Create `tools/assets-config.json` in your project root to configure languages and target devices (see `dashboard/assets-config.sample.json` for reference).

### 5. Run Dashboard (Optional)
```bash
npx serve .
```
Access the dashboard at `http://localhost:3000/tools/marketing-tools/dashboard/MARKETING_DASHBOARD.html`
