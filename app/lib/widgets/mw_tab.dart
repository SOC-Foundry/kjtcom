import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';

/// Middleware (MW) tab - replaces Gotcha tab (v9.49).
/// Displays component registry, resolved gotchas, agent roster, pipeline overview.
class MwTab extends StatefulWidget {
  const MwTab({super.key});

  @override
  State<MwTab> createState() => _MwTabState();
}

class _MwTabState extends State<MwTab> {
  Map<String, dynamic>? _registry;
  List<dynamic>? _gotchas;
  String? _error;
  String _gotchaFilter = 'all';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final regJson = await rootBundle.loadString('assets/middleware_registry.json');
      final gotchaJson = await rootBundle.loadString('assets/gotcha_archive.json');
      setState(() {
        _registry = json.decode(regJson) as Map<String, dynamic>;
        final gotchaData = json.decode(gotchaJson) as Map<String, dynamic>;
        _gotchas = gotchaData['resolved_gotchas'] as List<dynamic>? ?? [];
      });
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Center(
        child: Text('Error loading middleware data: $_error',
            style: const TextStyle(color: Tokens.accentRed)),
      );
    }
    if (_registry == null) {
      return const Center(child: CircularProgressIndicator(color: Tokens.accentGreen));
    }

    return ListView(
      padding: const EdgeInsets.all(Tokens.space4),
      children: [
        _buildOverviewCard(),
        const SizedBox(height: Tokens.space4),
        _buildSectionTitle('Component Registry'),
        const SizedBox(height: Tokens.space2),
        _buildComponentList(),
        const SizedBox(height: Tokens.space4),
        _buildSectionTitle('Resolved Gotchas'),
        const SizedBox(height: Tokens.space2),
        _buildGotchaFilter(),
        const SizedBox(height: Tokens.space2),
        _buildGotchaList(),
        const SizedBox(height: Tokens.space4),
        _buildSectionTitle('Agent Roster'),
        const SizedBox(height: Tokens.space2),
        _buildAgentRoster(),
        const SizedBox(height: Tokens.space4),
        _buildSectionTitle('Pipeline Phases'),
        const SizedBox(height: Tokens.space2),
        _buildPipelinePhases(),
        const SizedBox(height: Tokens.space8),
      ],
    );
  }

  Widget _buildOverviewCard() {
    final meta = _registry!['metadata'] as Map<String, dynamic>? ?? {};
    final scripts = _registry!['scripts'] as List? ?? [];
    final harnesses = _registry!['harnesses'] as List? ?? [];
    final utils = _registry!['utils'] as List? ?? [];
    final templates = _registry!['templates'] as List? ?? [];
    final dataStores = _registry!['data_stores'] as List? ?? [];
    final total = scripts.length + harnesses.length + utils.length + templates.length + dataStores.length;

    return Container(
      padding: const EdgeInsets.all(Tokens.space4),
      decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'kjtcom Middleware',
            style: GoogleFonts.cinzel(
              fontSize: Tokens.size2xl,
              fontWeight: FontWeight.w700,
              color: Tokens.accentGreen,
            ),
          ),
          const SizedBox(height: Tokens.space1),
          Text(
            meta['description'] as String? ?? 'Portable IAO Infrastructure',
            style: const TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeBase,
              color: Tokens.textSecondary,
              height: 1.4,
            ),
          ),
          const SizedBox(height: Tokens.space3),
          _buildMetricRow([
            _Metric('Components', '$total'),
            _Metric('Version', meta['version'] as String? ?? '-'),
            _Metric('Updated', meta['updated'] as String? ?? '-'),
            _Metric('Gotchas', '${_gotchas?.length ?? 0} resolved'),
          ]),
        ],
      ),
    );
  }

  Widget _buildMetricRow(List<_Metric> metrics) {
    return Wrap(
      spacing: Tokens.space4,
      runSpacing: Tokens.space2,
      children: metrics.map((m) => _MetricChip(metric: m)).toList(),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.cinzel(
        fontSize: Tokens.sizeXl,
        fontWeight: FontWeight.w600,
        color: Tokens.textPrimary,
      ),
    );
  }

  Widget _buildComponentList() {
    final sections = <String, List<dynamic>>{
      'Harnesses': _registry!['harnesses'] as List? ?? [],
      'Scripts': _registry!['scripts'] as List? ?? [],
      'Utilities': _registry!['utils'] as List? ?? [],
      'Templates': _registry!['templates'] as List? ?? [],
      'Data Stores': _registry!['data_stores'] as List? ?? [],
      'Services': _registry!['services'] as List? ?? [],
    };

    return Column(
      children: sections.entries
          .where((e) => e.value.isNotEmpty)
          .map((e) => _ComponentSection(title: e.key, items: e.value))
          .toList(),
    );
  }

  Widget _buildGotchaFilter() {
    return Row(
      children: [
        _buildFilterChip('All', 'all'),
        const SizedBox(width: Tokens.space2),
        _buildFilterChip('Environment', 'environment'),
        const SizedBox(width: Tokens.space2),
        _buildFilterChip('Firestore', 'firestore'),
        const SizedBox(width: Tokens.space2),
        _buildFilterChip('LLM', 'llm_config'),
      ],
    );
  }

  Widget _buildFilterChip(String label, String value) {
    final active = _gotchaFilter == value;
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: () => setState(() => _gotchaFilter = value),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: Tokens.space3, vertical: Tokens.space1),
          decoration: BoxDecoration(
            color: active ? Tokens.surfaceElevated : Colors.transparent,
            border: Border.all(color: active ? Tokens.accentGreen : const Color(0x4D4ADE80)),
            borderRadius: BorderRadius.circular(Tokens.radiusMd),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeSm,
              color: active ? Tokens.accentGreen : Tokens.textSecondary,
              fontWeight: active ? FontWeight.w500 : FontWeight.w400,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGotchaList() {
    final filtered = _gotchaFilter == 'all'
        ? _gotchas!
        : _gotchas!.where((g) => (g as Map)['root_cause'] == _gotchaFilter).toList();

    if (filtered.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(Tokens.space4),
        child: Text('No gotchas match filter.', style: TextStyle(color: Tokens.textMuted)),
      );
    }

    return Column(
      children: filtered.map((g) => _GotchaCard(gotcha: g as Map<String, dynamic>)).toList(),
    );
  }

  Widget _buildAgentRoster() {
    const agents = [
      {'name': 'Claude Code', 'engine': 'Claude API', 'role': 'Primary executor (when leading)'},
      {'name': 'Gemini CLI', 'engine': 'Gemini API', 'role': 'Pipeline executor, may lead iterations'},
      {'name': 'Qwen3.5-9B', 'engine': 'Ollama local', 'role': 'Evaluation (schema-validated v9.49+)'},
      {'name': 'Nemotron Mini 4B', 'engine': 'Ollama local', 'role': 'Fast triage'},
      {'name': 'GLM-4.6V-Flash', 'engine': 'Ollama local', 'role': 'Vision'},
      {'name': 'nomic-embed-text', 'engine': 'Ollama local', 'role': 'Embeddings only'},
      {'name': 'Gemini Flash', 'engine': 'Gemini API (litellm)', 'role': 'Intent routing, synthesis'},
    ];

    return Container(
      decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
      child: Column(
        children: [
          _buildTableHeader(['Agent', 'Engine', 'Role']),
          ...agents.map((a) => _buildTableRow([a['name']!, a['engine']!, a['role']!])),
        ],
      ),
    );
  }

  Widget _buildPipelinePhases() {
    const phases = [
      {'phase': '1', 'name': 'Acquire', 'tool': 'yt-dlp'},
      {'phase': '2', 'name': 'Transcribe', 'tool': 'faster-whisper (CUDA)'},
      {'phase': '3', 'name': 'Extract', 'tool': 'Gemini Flash API'},
      {'phase': '4', 'name': 'Normalize', 'tool': 'Thompson Schema'},
      {'phase': '5', 'name': 'Geocode', 'tool': 'Nominatim (OSM)'},
      {'phase': '6', 'name': 'Enrich', 'tool': 'Google Places API'},
      {'phase': '7', 'name': 'Load', 'tool': 'Firebase Admin SDK'},
    ];

    return Container(
      decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
      child: Column(
        children: [
          _buildTableHeader(['Phase', 'Name', 'Tool']),
          ...phases.map((p) => _buildTableRow([p['phase']!, p['name']!, p['tool']!])),
        ],
      ),
    );
  }

  Widget _buildTableHeader(List<String> cols) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Tokens.space4, vertical: Tokens.space2),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Tokens.borderDefault)),
      ),
      child: Row(
        children: cols.asMap().entries.map((e) {
          final flex = e.key == cols.length - 1 ? 2 : 1;
          return Expanded(
            flex: flex,
            child: Text(
              e.value,
              style: GoogleFonts.cinzel(
                fontSize: Tokens.sizeSm,
                fontWeight: FontWeight.w600,
                color: Tokens.accentGreen,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildTableRow(List<String> cols) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Tokens.space4, vertical: Tokens.space2),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
      ),
      child: Row(
        children: cols.asMap().entries.map((e) {
          final flex = e.key == cols.length - 1 ? 2 : 1;
          return Expanded(
            flex: flex,
            child: Text(
              e.value,
              style: TextStyle(
                fontFamily: e.key == 0 ? Tokens.fontMono : Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: e.key == 0 ? Tokens.accentBlue : Tokens.textSecondary,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _Metric {
  final String label;
  final String value;
  const _Metric(this.label, this.value);
}

class _MetricChip extends StatelessWidget {
  final _Metric metric;
  const _MetricChip({required this.metric});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Tokens.space3, vertical: Tokens.space1),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0x4D4ADE80)),
        borderRadius: BorderRadius.circular(Tokens.radiusMd),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            metric.label,
            style: const TextStyle(
              fontFamily: Tokens.fontSans,
              fontSize: Tokens.sizeXs,
              color: Tokens.textMuted,
            ),
          ),
          Text(
            metric.value,
            style: const TextStyle(
              fontFamily: Tokens.fontMono,
              fontSize: Tokens.sizeMd,
              color: Tokens.accentGreen,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _ComponentSection extends StatelessWidget {
  final String title;
  final List<dynamic> items;
  const _ComponentSection({required this.title, required this.items});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space3),
      child: Container(
        decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
        child: ExpansionTile(
          initiallyExpanded: false,
          collapsedIconColor: Tokens.textMuted,
          iconColor: Tokens.accentGreen,
          title: Row(
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontFamily: Tokens.fontSans,
                  fontSize: Tokens.sizeMd,
                  fontWeight: FontWeight.w500,
                  color: Tokens.textPrimary,
                ),
              ),
              const SizedBox(width: Tokens.space2),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  border: Border.all(color: Tokens.accentGreen),
                  borderRadius: BorderRadius.circular(Tokens.radiusSm),
                ),
                child: Text(
                  '${items.length}',
                  style: const TextStyle(
                    fontFamily: Tokens.fontMono,
                    fontSize: Tokens.sizeXs,
                    color: Tokens.accentGreen,
                  ),
                ),
              ),
            ],
          ),
          children: items.map((item) {
            final m = item as Map<String, dynamic>;
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: Tokens.space4, vertical: Tokens.space2),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Tokens.borderSubtle)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      m['name'] as String? ?? '-',
                      style: const TextStyle(
                        fontFamily: Tokens.fontMono,
                        fontSize: Tokens.sizeSm,
                        color: Tokens.accentBlue,
                      ),
                    ),
                  ),
                  const SizedBox(width: Tokens.space2),
                  if (m['version'] != null)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                      decoration: BoxDecoration(
                        border: Border.all(color: Tokens.textMuted),
                        borderRadius: BorderRadius.circular(Tokens.radiusSm),
                      ),
                      child: Text(
                        m['version'] as String,
                        style: const TextStyle(
                          fontFamily: Tokens.fontMono,
                          fontSize: Tokens.sizeXs,
                          color: Tokens.textMuted,
                        ),
                      ),
                    ),
                  const SizedBox(width: Tokens.space2),
                  Expanded(
                    flex: 2,
                    child: Text(
                      m['description'] as String? ?? m['type'] as String? ?? '-',
                      style: const TextStyle(
                        fontFamily: Tokens.fontSans,
                        fontSize: Tokens.sizeXs,
                        color: Tokens.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}

class _GotchaCard extends StatelessWidget {
  final Map<String, dynamic> gotcha;
  const _GotchaCard({required this.gotcha});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space3),
      child: Container(
        padding: const EdgeInsets.all(Tokens.space4),
        decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: Tokens.space2, vertical: 2),
                  decoration: BoxDecoration(
                    border: Border.all(color: Tokens.textMuted),
                    borderRadius: BorderRadius.circular(Tokens.radiusSm),
                  ),
                  child: Text(
                    gotcha['id'] as String? ?? '?',
                    style: GoogleFonts.cinzel(
                      fontSize: Tokens.sizeSm,
                      fontWeight: FontWeight.w700,
                      color: Tokens.textMuted,
                    ),
                  ),
                ),
                const SizedBox(width: Tokens.space3),
                Expanded(
                  child: Text(
                    gotcha['description'] as String? ?? '-',
                    style: const TextStyle(
                      fontFamily: Tokens.fontSans,
                      fontSize: Tokens.sizeMd,
                      fontWeight: FontWeight.w500,
                      color: Tokens.textPrimary,
                    ),
                  ),
                ),
                const SizedBox(width: Tokens.space2),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    border: Border.all(color: Tokens.textMuted),
                    borderRadius: BorderRadius.circular(Tokens.radiusSm),
                  ),
                  child: Text(
                    gotcha['iteration_resolved'] as String? ?? '-',
                    style: const TextStyle(
                      fontFamily: Tokens.fontMono,
                      fontSize: Tokens.sizeXs,
                      color: Tokens.textMuted,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: Tokens.space2),
            Container(
              height: 1,
              decoration: const BoxDecoration(
                gradient: LinearGradient(colors: [Color(0x4D4ADE80), Colors.transparent]),
              ),
            ),
            const SizedBox(height: Tokens.space2),
            Text(
              gotcha['resolution'] as String? ?? '-',
              style: const TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: Tokens.textSecondary,
                height: 1.4,
              ),
            ),
            if (gotcha['root_cause'] != null) ...[
              const SizedBox(height: Tokens.space1),
              Text(
                'Root cause: ${gotcha['root_cause']}',
                style: const TextStyle(
                  fontFamily: Tokens.fontMono,
                  fontSize: Tokens.sizeXs,
                  color: Tokens.textMuted,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
