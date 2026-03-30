import re

with open('README.md', 'r') as f:
    content = f.read()

# 1. Rename 'Thompson Schema' to 'Thompson Indicator Fields'
content = content.replace('Thompson Schema', 'Thompson Indicator Fields')

# 2. Add Data Architecture section
architecture_section = """## Data Architecture

kjtcom utilizes a **single-collection Firestore design** where all entities from all pipelines live together in a single `locations` collection. This allows for unified, cross-dataset search.

- **Discriminator**: The `t_log_type` field acts as the discriminator to filter by pipeline (e.g., `calgold`, `ricksteves`).
- **Querying**: Extensive use of `array-contains` queries enables searching across multiple attributes (keywords, categories, regions) without rigid schemas.
- **Indexes**: Composite indexes are defined in `firestore.indexes.json` to support multi-field filtering and sorting.
- **Environments**: A multi-database setup (`(default)` for production, `staging` for pipeline runs) safely separates work in progress.
- **Pricing**: Powered by the Firebase Blaze plan to support Cloud Functions and multi-database architectures.
- **Enforcement**: The field convention is enforced purely by the pipeline scripts (specifically `phase4_normalize.py`), not by the database itself.

---

## Thompson Indicator Fields (`t_any_*`)"""

content = re.sub(r'## Thompson Indicator Fields \(`t_any_\*`\)', architecture_section, content)

# 3. Show all 4 pipelines in the Pipelines table
pipelines_table = """| Pipeline (`t_log_type`) | Source | Entity Type | Videos | Entities | Status |
|-------------------------|--------|-------------|--------|----------|--------|
| `calgold` | California's Gold (Huell Howser) | landmark | 431 | 300 | Phase 4 Validation (Schema v3) |
| `ricksteves` | Rick Steves' Europe | destination | 1,865 | 669 | Phase 4 Validation (Schema v3) |
| `tripledb` | Diners, Drive-Ins and Dives | restaurant | 805 | - | Migration candidate |
| `bourdain` | Anthony Bourdain: Parts Unknown | destination | 104 | - | Pending onboarding |"""

content = re.sub(r'\| Pipeline \| Source \| Entity Type \| Videos \| Entities \| Status \|\n\|---\|---\|---\|---\|---\|---\|\n(?:\|.*?\|\n)*', pipelines_table + '\n', content)

# 4. Add Examples column to the indicator fields table
def update_table(match):
    rows = match.group(1).strip().split('\n')
    examples = {
        '`t_any_names`': '`["eiffel tower", "la tour eiffel"]`',
        '`t_any_people`': '`["rick steves", "huell howser"]`',
        '`t_any_cities`': '`["paris", "los angeles"]`',
        '`t_any_states`': '`["ca", "ny"]`',
        '`t_any_counties`': '`["los angeles county"]`',
        '`t_any_countries`': '`["france", "us"]`',
        '`t_any_regions`': '`["bavaria", "tuscany"]`',
        '`t_any_coordinates`': '`[{"lat": 48.85, "lon": 2.29}]`',
        '`t_any_geohashes`': '`["u09t", "u09tv"]`',
        '`t_any_keywords`': '`["gothic", "museum", "art"]`',
        '`t_any_categories`': '`["landmark", "restaurant"]`',
        '`t_any_actors`': '`["local guide", "chef"]`',
        '`t_any_roles`': '`["host", "historian"]`',
        '`t_any_cuisines`': '`["french", "italian"]`',
        '`t_any_dishes`': '`["croissant", "paella"]`',
        '`t_any_eras`': '`["medieval", "roman"]`',
        '`t_any_continents`': '`["europe", "asia"]`',
        '`t_any_urls`': '`["https://example.com"]`',
        '`t_any_video_ids`': '`["dQw4w9WgXcQ"]`',
    }
    
    new_rows = ['| Field | Type | Description | Examples |', '|-------|------|-------------|----------|']
    for row in rows:
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 3:
            field = parts[0]
            example = examples.get(field, '`[...]`')
            new_rows.append(f'| {field} | {parts[1]} | {parts[2]} | {example} |')
            
    return '\n'.join(new_rows) + '\n'

content_parts = content.split('**Indicator Fields** (universal cross-pipeline arrays):\n\n')
if len(content_parts) == 2:
    table_and_rest = content_parts[1].split('\n\n', 1)
    if len(table_and_rest) == 2:
        new_table = update_table(re.match(r'\| Field \| Type \| Description \|\n\|[-|\s]+\|\n(.*)', table_and_rest[0], re.DOTALL))
        if new_table.strip():
            content = content_parts[0] + '**Indicator Fields** (universal cross-pipeline arrays):\n\n' + new_table + '\n' + table_and_rest[1]

with open('README.md', 'w') as f:
    f.write(content)
