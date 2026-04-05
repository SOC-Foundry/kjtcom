#!/usr/bin/env python3
"""Build architecture.html from architecture.mmd using Mermaid JS CDN.

Reads docs/kjtcom-architecture.mmd, strips comment lines (%%),
injects into dark-themed HTML template, outputs to app/web/architecture.html.
"""
import os
import sys

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MMD_PATH = os.path.join(PROJECT_DIR, 'docs', 'kjtcom-architecture.mmd')
OUTPUT_PATH = os.path.join(PROJECT_DIR, 'app', 'web', 'architecture.html')

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kjtcom Architecture</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            background: #0D1117;
            color: #4ADE80;
            font-family: 'Geist Sans', system-ui, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            font-family: 'Cinzel', serif;
            color: #4ADE80;
            border-bottom: 1px solid #4ADE80;
            padding-bottom: 10px;
        }}
        .mermaid {{
            width: 100%;
            max-width: 1400px;
        }}
        .meta {{
            color: #6B7280;
            font-size: 0.85rem;
            margin-bottom: 20px;
        }}
        a {{
            color: #4ADE80;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .back-link {{
            margin-top: 20px;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>kjtcom Architecture</h1>
    <div class="meta">Living document - updated every iteration | Phase 9 {iteration}</div>
    <div class="mermaid">
{mermaid_content}
    </div>
    <div class="back-link"><a href="/">Back to kjtcom</a></div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#161B22',
                primaryTextColor: '#4ADE80',
                primaryBorderColor: '#4ADE80',
                lineColor: '#4ADE80',
                secondaryColor: '#0D9488',
                tertiaryColor: '#161B22'
            }}
        }});
    </script>
</body>
</html>"""


def build():
    iteration = os.environ.get('IAO_ITERATION', 'v9.43')

    if not os.path.exists(MMD_PATH):
        print(f"ERROR: {MMD_PATH} not found")
        sys.exit(1)

    with open(MMD_PATH) as f:
        lines = f.readlines()

    # Strip %% comment lines
    mermaid_lines = [line for line in lines if not line.strip().startswith('%%')]
    mermaid_content = ''.join(mermaid_lines).strip()

    html = HTML_TEMPLATE.format(
        iteration=iteration,
        mermaid_content=mermaid_content
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        f.write(html)

    print(f"Built: {OUTPUT_PATH}")
    print(f"  Source: {MMD_PATH}")
    print(f"  Lines: {len(mermaid_lines)} (stripped {len(lines) - len(mermaid_lines)} comments)")


if __name__ == '__main__':
    build()
