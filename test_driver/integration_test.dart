import 'dart:io';
import 'package:integration_test/integration_test_driver_extended.dart';

/// Generic integration test driver that saves screenshots to the host machine.
/// This file is shared across projects via the marketing-tools submodule.
Future<void> main() {
  final String device = Platform.environment['SCREENSHOT_DEVICE'] ?? 'phone';
  final String locale = Platform.environment['SCREENSHOT_LOCALE'] ?? 'ko';

  return integrationDriver(
    onScreenshot: (String name, List<int> image, [Map<String, Object?>? args]) async {
      // Standard path for marketing assets: store-assets/screenshots/{device}/
      final File screenshot = await File('store-assets/screenshots/$device/${device}_${locale}_$name.png').create(recursive: true);
      await screenshot.writeAsBytes(image);
      print('Screenshot saved: ${screenshot.path}');
      return true;
    },
  );
}
