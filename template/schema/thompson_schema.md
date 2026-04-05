# Thompson Indicator Fields Specification

Universal indicator fields for cross-dataset normalization. Modeled after Panther SIEM's `p_any_*` fields.

## Standard Fields (every document)

| Field | Type | Description |
|-------|------|-------------|
| `t_log_type` | string | Pipeline/dataset ID (discriminator) |
| `t_row_id` | string | Unique entity ID |
| `t_event_time` | timestamp | Source event time |
| `t_parse_time` | timestamp | Pipeline processing time (UTC) |
| `t_source_label` | string | Human-readable pipeline name |
| `t_schema_version` | int | Schema version |

## Indicator Fields (universal arrays)

| Field | Type | Description |
|-------|------|-------------|
| `t_any_names` | array[string] | All entity names |
| `t_any_people` | array[string] | All people mentioned |
| `t_any_cities` | array[string] | All city names |
| `t_any_states` | array[string] | All state/province names |
| `t_any_counties` | array[string] | All county names |
| `t_any_countries` | array[string] | All country names |
| `t_any_country_codes` | array[string] | ISO 3166-1 alpha-2 codes |
| `t_any_regions` | array[string] | Sub-country regions |
| `t_any_coordinates` | array[map] | lat/lon pairs |
| `t_any_geohashes` | array[string] | Geohash prefixes |
| `t_any_keywords` | array[string] | Searchable terms |
| `t_any_categories` | array[string] | Normalized categories |
| `t_any_urls` | array[string] | Associated URLs |

## Extension Fields

Add domain-specific indicator fields following the `t_any_*` convention.
All values MUST be lowercased for case-insensitive search compatibility.
