"""Query assessment part 2 - example queries and case issues."""

from google.cloud import firestore

db = firestore.Client(project="kjtcom-c78cd")
col = db.collection("locations")

# Check t_any_shows case issue
q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "California's Gold"))
results = list(q.stream())
print(f"t_any_shows title case 'California's Gold': {len(results)}")

q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "california's gold"))
results = list(q.stream())
print(f"t_any_shows lowercase 'california's gold': {len(results)}")

q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "Rick Steves' Europe"))
results = list(q.stream())
print(f"t_any_shows title case 'Rick Steves' Europe': {len(results)}")

q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "rick steves' europe"))
results = list(q.stream())
print(f"t_any_shows lowercase 'rick steves' europe': {len(results)}")

# Check gelato and landmark
q = col.where(filter=firestore.FieldFilter("t_any_dishes", "array_contains", "gelato"))
results = list(q.stream())
print(f"t_any_dishes gelato: {len(results)}")

q = col.where(filter=firestore.FieldFilter("t_any_categories", "array_contains", "landmark"))
results = list(q.stream())
print(f"t_any_categories landmark: {len(results)}")

print()
print("=== FLUTTER EXAMPLE QUERY SIMULATION ===")
print()

# Example 1: t_any_cuisines contains "French" + t_any_shows == "Rick Steves' Europe"
# Server: arrayContains(t_any_cuisines, "French") -> 0 (case-sensitive!)
q = col.where(filter=firestore.FieldFilter("t_any_cuisines", "array_contains", "French")).limit(200)
results = list(q.stream())
print(f'Ex1 "French" cuisine (server): {len(results)} -> app shows 0 results')

# Example 2: t_any_actors contains "Huell Howser" + t_any_states contains "ca"
q = col.where(filter=firestore.FieldFilter("t_any_actors", "array_contains", "Huell Howser")).limit(200)
results = list(q.stream())
print(f'Ex2 "Huell Howser" (server): {len(results)} -> app shows 0 results')

# Example 3: t_any_dishes contains "gelato" + t_any_continents == "Europe"
q = col.where(filter=firestore.FieldFilter("t_any_dishes", "array_contains", "gelato")).limit(200)
results = list(q.stream())
if results:
    filtered = [r for r in results if "europe" in [c.lower() for c in r.to_dict().get("t_any_continents", [])]]
    print(f'Ex3 "gelato" server={len(results)}, client-filtered (Europe): {len(filtered)}')
else:
    print(f'Ex3 "gelato" server={len(results)} -> app shows 0 results')

# Example 4: t_any_categories contains "landmark" + t_any_countries == "France"
q = col.where(filter=firestore.FieldFilter("t_any_categories", "array_contains", "landmark")).limit(200)
results = list(q.stream())
filtered = [r for r in results if "france" in [c.lower() for c in r.to_dict().get("t_any_countries", [])]]
print(f'Ex4 "landmark" server={len(results)}, client-filtered (France): {len(filtered)}')

# Example 5: t_any_keywords contains "medieval" + t_any_eras contains "roman"
q = col.where(filter=firestore.FieldFilter("t_any_keywords", "array_contains", "medieval")).limit(200)
results = list(q.stream())
filtered = [r for r in results if "roman" in [e.lower() for e in r.to_dict().get("t_any_eras", [])]]
print(f'Ex5 "medieval" server={len(results)}, client-filtered (roman eras): {len(filtered)}')

# Check how many total results are truncated by the 200 limit
print()
print("=== LIMIT TRUNCATION CHECK ===")
q_unlimited = col.where(filter=firestore.FieldFilter("t_any_keywords", "array_contains", "medieval"))
all_results = list(q_unlimited.stream())
print(f"medieval (no limit): {len(all_results)}, (limit 200): {min(200, len(all_results))}")
print(f"Truncated: {'YES' if len(all_results) > 200 else 'NO'} ({len(all_results) - 200 if len(all_results) > 200 else 0} hidden)")

q_unlimited = col.where(filter=firestore.FieldFilter("t_any_countries", "array_contains", "france"))
all_results = list(q_unlimited.stream())
print(f"france (no limit): {len(all_results)}, (limit 200): {min(200, len(all_results))}")
print(f"Truncated: {'YES' if len(all_results) > 200 else 'NO'} ({len(all_results) - 200 if len(all_results) > 200 else 0} hidden)")
