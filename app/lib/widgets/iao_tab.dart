import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/tokens.dart';

/// IAO Pillar tab - trident SVG + 10 pillar cards + stats footer.
/// All pillar texts VERBATIM from the design doc.
class IaoTab extends StatelessWidget {
  const IaoTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(Tokens.space4),
      children: [
        // Trident graphic
        const _TridentGraphic(),
        const SizedBox(height: Tokens.space6),

        // 10 Pillar cards
        ..._pillars.map((p) => _PillarCard(pillar: p)),

        // Stats footer
        const SizedBox(height: Tokens.space6),
        const _StatsFooter(),
        const SizedBox(height: Tokens.space8),
      ],
    );
  }
}

/// Trident SVG rendered as a custom Flutter widget.
class _TridentGraphic extends StatelessWidget {
  const _TridentGraphic();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Tokens.space6),
      decoration: Tokens.gothicCardDecoration(radius: Tokens.radiusXl),
      child: Column(
        children: [
          // Three prongs
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildProng('\u25C6 Minimal cost'),
              _buildProng('\u25C6 Speed of delivery'),
              _buildProng('\u25C6 Optimized performance'),
            ],
          ),
          const SizedBox(height: Tokens.space3),
          // Connecting lines (visual)
          SizedBox(
            height: 32,
            child: CustomPaint(
              size: const Size(double.infinity, 32),
              painter: _TridentPainter(),
            ),
          ),
          const SizedBox(height: Tokens.space3),
          // Central shaft
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: Tokens.space6,
              vertical: Tokens.space3,
            ),
            decoration: BoxDecoration(
              color: Tokens.teal,
              borderRadius: BorderRadius.circular(Tokens.radiusMd),
            ),
            child: Text(
              'I A O',
              style: GoogleFonts.cinzel(
                fontSize: 24,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                letterSpacing: 4,
              ),
            ),
          ),
          const SizedBox(height: Tokens.space2),
          Text(
            'Iterative Agentic Orchestration',
            style: GoogleFonts.cinzel(
              fontSize: Tokens.sizeLg,
              fontWeight: FontWeight.w500,
              color: Tokens.teal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProng(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: Tokens.space3,
        vertical: Tokens.space2,
      ),
      decoration: BoxDecoration(
        color: Tokens.surfaceElevated,
        border: Border.all(color: Tokens.accentGreen),
        borderRadius: BorderRadius.circular(Tokens.radiusMd),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontFamily: Tokens.fontSans,
          fontSize: Tokens.sizeSm,
          color: Tokens.accentGreen,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

class _TridentPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Tokens.teal
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final centerX = size.width / 2;
    final leftX = size.width * 0.167;
    final rightX = size.width * 0.833;

    // Left prong to center
    canvas.drawLine(
      Offset(leftX, 0),
      Offset(centerX, size.height),
      paint,
    );
    // Center prong to center
    canvas.drawLine(
      Offset(centerX, 0),
      Offset(centerX, size.height),
      paint,
    );
    // Right prong to center
    canvas.drawLine(
      Offset(rightX, 0),
      Offset(centerX, size.height),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _PillarCard extends StatefulWidget {
  final _Pillar pillar;
  const _PillarCard({required this.pillar});

  @override
  State<_PillarCard> createState() => _PillarCardState();
}

class _PillarCardState extends State<_PillarCard> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: Tokens.space3),
      child: MouseRegion(
        onEnter: (_) => setState(() => _hovering = true),
        onExit: (_) => setState(() => _hovering = false),
        child: AnimatedContainer(
          duration: Tokens.rowHighlight,
          padding: const EdgeInsets.all(Tokens.space4),
          decoration: Tokens.gothicCardDecoration(
            radius: Tokens.radiusXl,
          ).copyWith(
            boxShadow: _hovering ? Tokens.glowGreen : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    'P${widget.pillar.number}',
                    style: GoogleFonts.cinzel(
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                      color: Tokens.accentGreen,
                    ),
                  ),
                  const SizedBox(width: Tokens.space3),
                  Expanded(
                    child: Text(
                      widget.pillar.title,
                      style: GoogleFonts.cinzel(
                        fontSize: Tokens.sizeXl,
                        fontWeight: FontWeight.w600,
                        color: Tokens.textPrimary,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: Tokens.space2),
              // Corner accent divider
              Container(
                height: 1,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Color(0x4D4ADE80),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
              const SizedBox(height: Tokens.space3),
              Text(
                widget.pillar.description,
                style: const TextStyle(
                  fontFamily: Tokens.fontSans,
                  fontSize: Tokens.sizeMd,
                  color: Tokens.textSecondary,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatsFooter extends StatelessWidget {
  const _StatsFooter();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(Tokens.space4),
      decoration: Tokens.gothicCardDecoration(),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _stat('6,181', 'Entities'),
          _divider(),
          _stat('3', 'Pipelines'),
          _divider(),
          _stat('27', 'Iterations'),
          _divider(),
          _stat('26', 'Zero-Intervention'),
        ],
      ),
    );
  }

  Widget _stat(String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: GoogleFonts.cinzel(
            fontSize: Tokens.size2xl,
            fontWeight: FontWeight.w700,
            color: Tokens.accentGreen,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontFamily: Tokens.fontSans,
            fontSize: Tokens.sizeSm,
            color: Tokens.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _divider() {
    return Container(
      height: 32,
      width: 1,
      color: const Color(0x4D4ADE80),
    );
  }
}

class _Pillar {
  final int number;
  final String title;
  final String description;
  const _Pillar(this.number, this.title, this.description);
}

const _pillars = [
  _Pillar(
    1,
    'The IAO Trident',
    'Every decision is governed by three competing objectives: minimal cost '
        '(free-tier LLMs over paid, API scripts over SaaS add-ons, no '
        'infrastructure that outlives its purpose), optimized performance '
        '(right-size the solution, performance from discovery and '
        'proof-of-value testing, not premature abstraction), and speed of '
        'delivery (code and objectives become stale, P0 ships, P1 ships if '
        'time allows, P2 is post-launch). Cheapest is rarely fastest. '
        'Fastest is rarely most optimized. The methodology finds the '
        "triangle's center of gravity for each decision.",
  ),
  _Pillar(
    2,
    'Artifact Loop',
    'Every iteration produces four artifacts: design doc (living '
        'architecture), plan (execution steps), build log (session '
        'transcript), report (metrics + recommendation). Previous artifacts '
        'archive to docs/archive/. Agents never see outdated instructions. '
        'If an artifact has no consumer, it should not exist.',
  ),
  _Pillar(
    3,
    'Diligence',
    'The methodology does not work if you do not read. Before any iteration '
        'touches code, the plan goes through revision - often several '
        'revisions. Diligence is investing 30 minutes in plan revision to '
        'save 3 hours of misdirected agent execution. The fastest path is '
        "the one that doesn't require rework.",
  ),
  _Pillar(
    4,
    'Pre-Flight Verification',
    'Before execution begins, validate: previous docs archived, new design '
        '+ plan in place, agent instructions updated, git clean, API keys '
        'set, build tools verified. Pre-flight failures are the cheapest '
        'failures.',
  ),
  _Pillar(
    5,
    'Agentic Harness Orchestration',
    'The primary agent (Claude Code or Gemini CLI) orchestrates LLMs, MCP '
        'servers, scripts, APIs, and sub-agents within a structured harness. '
        'Agent instructions are system prompts (CLAUDE.md / GEMINI.md). '
        'Pipeline scripts are tools. Gotchas are middleware. Agents CAN '
        'build and deploy. Agents CANNOT git commit or sudo. The human '
        'commits at phase boundaries.',
  ),
  _Pillar(
    6,
    'Zero-Intervention Target',
    'Every question the agent asks during execution is a failure in the '
        'plan document. Pre-answer every decision point. Execute agents in '
        'YOLO mode, trust but verify. Measure plan quality by counting '
        'interventions - zero is the floor.',
  ),
  _Pillar(
    7,
    'Self-Healing Execution',
    'Errors are inevitable. Diagnose -> fix -> re-run. Max 3 attempts per '
        'error, then log and skip. Checkpoint after every completed step for '
        'crash recovery. Gotcha registry documents known failure patterns so '
        'the same error never causes an intervention twice.',
  ),
  _Pillar(
    8,
    'Phase Graduation',
    'Four iterative phases progressively harden the pipeline harness until '
        'production requires zero agent intervention. The agent built the '
        'harness; the harness runs the work.',
  ),
  _Pillar(
    9,
    'Post-Flight Functional Testing',
    'Three tiers: Tier 1 (app bootstraps, console clean, artifacts '
        'produced), Tier 2 (iteration-specific playbook), Tier 3 (hardening '
        'audit - Lighthouse, security headers, browser compat).',
  ),
  _Pillar(
    10,
    'Continuous Improvement',
    'The methodology evolves alongside the project. Retrospectives, gotcha '
        'registry reviews, tool efficacy reports, trident rebalancing. '
        'Static processes atrophy.',
  ),
];
