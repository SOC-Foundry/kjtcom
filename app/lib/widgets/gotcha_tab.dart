import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';

class _Gotcha {
  final String id;
  final String title;
  final String prevention;
  final String status; // 'active', 'resolved', 'documented'
  final String? resolvedIn;

  const _Gotcha({
    required this.id,
    required this.title,
    required this.prevention,
    required this.status,
    this.resolvedIn,
  });
}

const _gotchaRegistry = [
  _Gotcha(
    id: 'G1',
    title: 'Heredocs in fish shell',
    prevention: 'Use printf blocks, never heredocs',
    status: 'active',
  ),
  _Gotcha(
    id: 'G2',
    title: 'CUDA LD_LIBRARY_PATH',
    prevention: 'source ~/.config/fish/config.fish before transcription',
    status: 'resolved',
    resolvedIn: 'v3.10',
  ),
  _Gotcha(
    id: 'G11',
    title: 'API key leaks in catted files',
    prevention: 'NEVER cat config.fish or SA JSON files. grep only.',
    status: 'active',
  ),
  _Gotcha(
    id: 'G18',
    title: 'Gemini 5-minute command timeout',
    prevention: 'Use background job execution',
    status: 'active',
  ),
  _Gotcha(
    id: 'G19',
    title: 'Gemini runs bash by default',
    prevention: 'Wrap in fish -c',
    status: 'active',
  ),
  _Gotcha(
    id: 'G20',
    title: 'Config.fish contains API keys',
    prevention: 'grep only, never cat',
    status: 'active',
  ),
  _Gotcha(
    id: 'G21',
    title: 'CUDA OOM on simultaneous transcription',
    prevention: 'Sequential processing, graduated timeouts',
    status: 'active',
  ),
  _Gotcha(
    id: 'G22',
    title: 'Fish ls color codes',
    prevention: 'Use command ls',
    status: 'active',
  ),
  _Gotcha(
    id: 'G23',
    title: 'LD_LIBRARY_PATH CUDA path',
    prevention: 'Set in config.fish',
    status: 'resolved',
    resolvedIn: 'v3.10 (by G2)',
  ),
  _Gotcha(
    id: 'G24',
    title: 'Checkpoint staleness on re-extraction',
    prevention: 'Reset checkpoints for new prompts',
    status: 'active',
  ),
  _Gotcha(
    id: 'G30',
    title: 'Cross-project SA permissions',
    prevention: 'Verify both SA files before migration',
    status: 'active',
  ),
  _Gotcha(
    id: 'G31',
    title: 'TripleDB schema drift',
    prevention: 'Inspect actual data before migration',
    status: 'resolved',
    resolvedIn: 'v7.21',
  ),
  _Gotcha(
    id: 'G32',
    title: 'Production Firestore rules',
    prevention: 'Admin SDK bypasses rules, verify IAM',
    status: 'active',
  ),
  _Gotcha(
    id: 'G33',
    title: 'Duplicate entity IDs',
    prevention: 'Deterministic t_row_id, check before write',
    status: 'active',
  ),
  _Gotcha(
    id: 'G34',
    title: 'Firestore single array-contains limit',
    prevention: 'One per query, client-side for additional',
    status: 'active',
  ),
  _Gotcha(
    id: 'G35',
    title: 'Production write safety',
    prevention: '--dry-run before full run',
    status: 'active',
  ),
  _Gotcha(
    id: 'G36',
    title: 'Case-sensitive arrayContains',
    prevention: 'All data + input lowercased',
    status: 'resolved',
    resolvedIn: 'v8.23',
  ),
  _Gotcha(
    id: 'G37',
    title: 't_any_shows inconsistent casing',
    prevention: 'All lowercased',
    status: 'resolved',
    resolvedIn: 'v8.23',
  ),
  _Gotcha(
    id: 'G38',
    title: 'Firebase deploy auth expiry',
    prevention: 'firebase login --reauth, deploy from repo root',
    status: 'active',
  ),
  _Gotcha(
    id: 'G39',
    title: 'Detail panel provider chain',
    prevention: 'Must be in widget tree at all viewports',
    status: 'resolved',
    resolvedIn: 'v8.24',
  ),
  _Gotcha(
    id: 'G40',
    title: 'Compound country names',
    prevention: 'Manual split required, 6 unmapped',
    status: 'documented',
  ),
  _Gotcha(
    id: 'G41',
    title: 'Rebuild-triggered event handlers',
    prevention: 'Dedup + guard flag',
    status: 'resolved',
    resolvedIn: 'v8.25',
  ),
  _Gotcha(
    id: 'G42',
    title: 'Rotating queries overwrite input',
    prevention: 'Removed rotation',
    status: 'resolved',
    resolvedIn: 'v8.26',
  ),
  _Gotcha(
    id: 'G43',
    title: 'Flutter Web map tile CORS',
    prevention: 'Test CanvasKit + HTML renderer for OSM tiles',
    status: 'active',
  ),
  _Gotcha(
    id: 'G44',
    title: 'flutter_map version compatibility',
    prevention: 'Check pub.dev for Flutter SDK compat',
    status: 'active',
  ),
];

class GotchaTab extends StatefulWidget {
  const GotchaTab({super.key});

  @override
  State<GotchaTab> createState() => _GotchaTabState();
}

class _GotchaTabState extends State<GotchaTab> {
  String _filter = 'all'; // 'all', 'active', 'resolved'

  List<_Gotcha> get _filtered {
    if (_filter == 'all') return _gotchaRegistry;
    return _gotchaRegistry.where((g) => g.status == _filter).toList();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(Tokens.space4),
      children: [
        // Header
        Text(
          'Gotcha Registry',
          style: GoogleFonts.cinzel(
            fontSize: Tokens.size2xl,
            fontWeight: FontWeight.w700,
            color: Tokens.accentGreen,
          ),
        ),
        const SizedBox(height: Tokens.space1),
        const Text(
          'Failure patterns documented across 28 iterations. '
          'Each gotcha prevented at least one intervention.',
          style: TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeBase,
            color: Tokens.textSecondary,
            height: 1.4,
          ),
        ),
        const SizedBox(height: Tokens.space4),
        // Filter toggle
        _buildFilterRow(),
        const SizedBox(height: Tokens.space4),
        // Gotcha cards
        ..._filtered.map((g) => _GotchaCard(gotcha: g)),
        const SizedBox(height: Tokens.space8),
      ],
    );
  }

  Widget _buildFilterRow() {
    return Row(
      children: [
        _FilterChip(
          label: 'All',
          active: _filter == 'all',
          onTap: () => setState(() => _filter = 'all'),
        ),
        const SizedBox(width: Tokens.space2),
        _FilterChip(
          label: 'Active',
          active: _filter == 'active',
          onTap: () => setState(() => _filter = 'active'),
        ),
        const SizedBox(width: Tokens.space2),
        _FilterChip(
          label: 'Resolved',
          active: _filter == 'resolved',
          onTap: () => setState(() => _filter = 'resolved'),
        ),
      ],
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _FilterChip({
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: Tokens.space3,
            vertical: Tokens.space1,
          ),
          decoration: BoxDecoration(
            color: active ? Tokens.surfaceElevated : Colors.transparent,
            border: Border.all(
              color: active
                  ? Tokens.accentGreen
                  : const Color(0x4D4ADE80),
            ),
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
}

class _GotchaCard extends StatelessWidget {
  final _Gotcha gotcha;
  const _GotchaCard({required this.gotcha});

  @override
  Widget build(BuildContext context) {
    final isResolved = gotcha.status == 'resolved';

    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space3),
      child: Container(
        padding: const EdgeInsets.all(Tokens.space4),
        decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ID badge
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: Tokens.space2,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    border: Border.all(color: Tokens.accentGreen),
                    borderRadius: BorderRadius.circular(Tokens.radiusSm),
                  ),
                  child: Text(
                    gotcha.id,
                    style: GoogleFonts.cinzel(
                      fontSize: Tokens.sizeSm,
                      fontWeight: FontWeight.w700,
                      color: Tokens.accentGreen,
                    ),
                  ),
                ),
                const SizedBox(width: Tokens.space3),
                // Title
                Expanded(
                  child: Text(
                    gotcha.title,
                    style: TextStyle(
                      fontFamily: Tokens.fontSans,
                      fontSize: Tokens.sizeMd,
                      fontWeight: FontWeight.w500,
                      color: isResolved
                          ? Tokens.textMuted
                          : Tokens.textPrimary,
                      decoration: isResolved
                          ? TextDecoration.lineThrough
                          : null,
                    ),
                  ),
                ),
                const SizedBox(width: Tokens.space2),
                // Status badge
                _StatusBadge(
                  status: gotcha.status,
                  resolvedIn: gotcha.resolvedIn,
                ),
              ],
            ),
            const SizedBox(height: Tokens.space2),
            // Corner accent divider
            Container(
              height: 1,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0x4D4ADE80), Colors.transparent],
                ),
              ),
            ),
            const SizedBox(height: Tokens.space2),
            // Prevention text
            Text(
              gotcha.prevention,
              style: TextStyle(
                fontFamily: Tokens.fontSans,
                fontSize: Tokens.sizeBase,
                color: isResolved
                    ? Tokens.textMuted
                    : Tokens.textSecondary,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;
  final String? resolvedIn;

  const _StatusBadge({required this.status, this.resolvedIn});

  @override
  Widget build(BuildContext context) {
    final Color borderColor;
    final Color textColor;
    final String label;

    switch (status) {
      case 'active':
        borderColor = Tokens.accentGreen;
        textColor = Tokens.accentGreen;
        label = 'ACTIVE';
      case 'resolved':
        borderColor = Tokens.textMuted;
        textColor = Tokens.textMuted;
        label = resolvedIn != null ? 'RESOLVED $resolvedIn' : 'RESOLVED';
      case 'documented':
        borderColor = Tokens.accentOrange;
        textColor = Tokens.accentOrange;
        label = 'DOCUMENTED';
      default:
        borderColor = Tokens.textMuted;
        textColor = Tokens.textMuted;
        label = status.toUpperCase();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(Tokens.radiusSm),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontFamily: Tokens.fontMono,
          fontSize: Tokens.sizeXs,
          color: textColor,
        ),
      ),
    );
  }
}
