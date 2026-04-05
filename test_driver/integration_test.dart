import 'dart:io';
import 'package:integration_test/integration_test_driver_extended.dart';

Future<void> main() async {
  await integrationDriver(
    onScreenshot: (String screenshotName, List<int> screenshotBytes, [Map<String, Object?>? args]) async {
      // screenshotName format: {langCode}_{scenarioKey}_{suffix}
      final device = Platform.environment['DEVICE'] ?? 'phone';

      final parts = screenshotName.split('_');
      final langCode = parts[0];
      final scenarioKey = parts[1];
      final suffix = parts[2];

      final fileName = '${device}_${langCode}_${scenarioKey}_$suffix.png';
      final File image = await File('store-assets/screenshots/$device/$fileName').create(recursive: true);
      await image.writeAsBytes(screenshotBytes);
      return true;
    },
  );
}
