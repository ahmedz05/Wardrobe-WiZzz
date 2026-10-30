import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:wardrobe_wizzz/core/api_client.dart';
import 'package:wardrobe_wizzz/core/resource_controller.dart';

void main() {
  test('newer results win when requests finish out of order', () async {
    final state = ResourceController<String>();
    addTearDown(state.dispose);
    final first = Completer<String>();
    final pending = state.load(() => first.future);
    await state.load(() async => 'new');
    first.complete('old');
    await pending;
    expect(state.value, 'new');
    expect(state.status, LoadStatus.ready);
  });
  test(
    'failed requests expose retryable errors and remove previous data',
    () async {
      final state = ResourceController<String>();
      addTearDown(state.dispose);
      await state.load(() async => 'private data');
      await state.load(() async => throw const ApiException('Unavailable'));
      expect(state.value, isNull);
      expect(state.status, LoadStatus.failed);
      expect(state.error, 'Unavailable');
      await state.load(() async => 'recovered');
      expect(state.value, 'recovered');
    },
  );
  test('disposed screens ignore late responses', () async {
    final state = ResourceController<String>();
    final response = Completer<String>();
    final pending = state.load(() => response.future);
    state.dispose();
    response.complete('old account data');
    await pending;
    expect(state.value, isNull);
  });
}
