import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
import '../theme/tokens.dart';
import '../providers/firestore_provider.dart';
import '../providers/selection_provider.dart';

/// Map tab - renders entities on OpenStreetMap via flutter_map.
/// Pipeline-colored markers, tap to open detail panel.
class MapTab extends ConsumerWidget {
  const MapTab({super.key});

  static const _defaultCenter = LatLng(48.0, 10.0); // Europe center
  static const _defaultZoom = 3.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResult = ref.watch(queryResultProvider);

    return asyncResult.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: Tokens.accentGreen),
      ),
      error: (err, _) => Center(
        child: Text(
          'Map error: $err',
          style: const TextStyle(color: Tokens.accentRed),
        ),
      ),
      data: (queryResult) {
        final entities = queryResult.entities
            .where((e) => e.coordinates != null)
            .toList();

        final markers = entities.map((entity) {
          final coords = entity.coordinates!;
          return Marker(
            point: LatLng(coords.$1, coords.$2),
            width: 18,
            height: 18,
            child: GestureDetector(
              onTap: () {
                ref.read(selectedEntityProvider.notifier).select(entity);
              },
              child: Container(
                decoration: BoxDecoration(
                  color: Tokens.pipelineColor(entity.logType),
                  shape: BoxShape.circle,
                  border: Border.all(color: Tokens.surfaceBase, width: 1.5),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x40000000),
                      blurRadius: 3,
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList();

        return Stack(
          children: [
            FlutterMap(
              options: MapOptions(
                initialCenter: _defaultCenter,
                initialZoom: _defaultZoom,
                minZoom: 2,
                maxZoom: 18,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.kjtcom.app',
                ),
                MarkerLayer(markers: markers),
              ],
            ),
            // Entity count overlay
            Positioned(
              top: Tokens.space2,
              left: Tokens.space2,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: Tokens.space3,
                  vertical: Tokens.space1,
                ),
                decoration: BoxDecoration(
                  color: const Color(0xDD0D1117),
                  borderRadius: BorderRadius.circular(Tokens.radiusMd),
                  border: Border.all(color: const Color(0x4D4ADE80)),
                ),
                child: Text(
                  '${entities.length} mapped of ${queryResult.entities.length} results',
                  style: const TextStyle(
                    fontFamily: Tokens.fontMono,
                    fontSize: Tokens.sizeSm,
                    color: Tokens.textSecondary,
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
