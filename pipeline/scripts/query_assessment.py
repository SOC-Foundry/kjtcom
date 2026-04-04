"""NoSQL Query Assessment - Tests all 6 categories against production Firestore."""

from google.cloud import firestore

db = firestore.Client(project="kjtcom-c78cd")
col = db.collection("locations")


def count_by_type(results):
    types = {}
    for r in results:
        lt = r.to_dict().get("t_log_type", "unknown")
        types[lt] = types.get(lt, 0) + 1
    return types


print("=" * 60)
print("CATEGORY 1: Single field array-contains")
print("=" * 60)
print()

# 1.1
q = col.where(filter=firestore.FieldFilter("t_any_keywords", "array_contains", "barbecue"))
results = list(q.stream())
print(f'1.1 t_any_keywords contains "barbecue": {len(results)} results')
print(f'    Breakdown: {count_by_type(results)}')

# 1.2
q = col.where(filter=firestore.FieldFilter("t_any_countries", "array_contains", "france"))
results = list(q.stream())
print(f'1.2 t_any_countries contains "france": {len(results)} results')
print(f'    Breakdown: {count_by_type(results)}')

# 1.3
q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "california's gold"))
results = list(q.stream())
print(f"1.3 t_any_shows contains \"california's gold\": {len(results)} results")

# 1.4 Case sensitivity
q_upper = col.where(filter=firestore.FieldFilter("t_any_cuisines", "array_contains", "French"))
q_lower = col.where(filter=firestore.FieldFilter("t_any_cuisines", "array_contains", "french"))
results_upper = list(q_upper.stream())
results_lower = list(q_lower.stream())
print(f'1.4 Case: "French" -> {len(results_upper)}, "french" -> {len(results_lower)}')

# 1.5
q = col.where(filter=firestore.FieldFilter("t_any_actors", "array_contains", "huell howser"))
results = list(q.stream())
print(f'1.5 t_any_actors contains "huell howser": {len(results)} results')

# 1.6
q = col.where(filter=firestore.FieldFilter("t_any_actors", "array_contains", "rick steves"))
results = list(q.stream())
print(f'1.6 t_any_actors contains "rick steves": {len(results)} results')

print()
print("=" * 60)
print("CATEGORY 2: Pipeline filter (equality)")
print("=" * 60)
print()

q = col.where(filter=firestore.FieldFilter("t_log_type", "==", "tripledb"))
results = list(q.stream())
print(f'2.1 t_log_type == "tripledb": {len(results)} results')

q = col.where(filter=firestore.FieldFilter("t_log_type", "==", "calgold"))
results = list(q.stream())
print(f'2.2 t_log_type == "calgold": {len(results)} results')

q = col.where(filter=firestore.FieldFilter("t_log_type", "==", "ricksteves"))
results = list(q.stream())
print(f'2.3 t_log_type == "ricksteves": {len(results)} results')

print()
print("=" * 60)
print("CATEGORY 3: Compound queries (array-contains + equality)")
print("=" * 60)
print()

# 3.1 array-contains + equality on different field
try:
    q = col.where(
        filter=firestore.FieldFilter("t_any_cuisines", "array_contains", "mexican")
    ).where(
        filter=firestore.FieldFilter("t_log_type", "==", "tripledb")
    )
    results = list(q.stream())
    print(f'3.1 t_any_cuisines contains "mexican" + t_log_type == "tripledb": {len(results)} results')
except Exception as e:
    print(f'3.1 FAILED: {e}')

# 3.2 Two array-contains (should fail server-side)
try:
    q = col.where(
        filter=firestore.FieldFilter("t_any_countries", "array_contains", "italy")
    ).where(
        filter=firestore.FieldFilter("t_any_categories", "array_contains", "restaurant")
    )
    results = list(q.stream())
    print(f'3.2 Two array-contains (countries + categories): {len(results)} results')
except Exception as e:
    print(f'3.2 EXPECTED FAIL (two array-contains): {str(e)[:150]}')

# 3.3 array-contains + equality (different combo)
try:
    q = col.where(
        filter=firestore.FieldFilter("t_any_keywords", "array_contains", "medieval")
    ).where(
        filter=firestore.FieldFilter("t_log_type", "==", "ricksteves")
    )
    results = list(q.stream())
    print(f'3.3 t_any_keywords contains "medieval" + t_log_type == "ricksteves": {len(results)} results')
except Exception as e:
    print(f'3.3 FAILED: {e}')

print()
print("=" * 60)
print("CATEGORY 4: Multi-value array queries (array-contains-any)")
print("=" * 60)
print()

# 4.1
try:
    q = col.where(
        filter=firestore.FieldFilter("t_any_cuisines", "array_contains_any", ["mexican", "italian"])
    )
    results = list(q.stream())
    print(f'4.1 t_any_cuisines contains-any ["mexican", "italian"]: {len(results)} results')
    print(f'    Breakdown: {count_by_type(results)}')
except Exception as e:
    print(f'4.1 FAILED: {str(e)[:150]}')

# 4.2
try:
    q = col.where(
        filter=firestore.FieldFilter("t_any_countries", "array_contains_any", ["france", "italy", "spain"])
    )
    results = list(q.stream())
    print(f'4.2 t_any_countries contains-any ["france", "italy", "spain"]: {len(results)} results')
    print(f'    Breakdown: {count_by_type(results)}')
except Exception as e:
    print(f'4.2 FAILED: {str(e)[:150]}')

print()
print("=" * 60)
print("CATEGORY 5: Result counts")
print("=" * 60)
print()

# Total entities
total = 0
for doc in col.stream():
    total += 1
print(f"5.1 Total entities in collection: {total}")

# Count for a specific query
q = col.where(filter=firestore.FieldFilter("t_any_cuisines", "array_contains", "french"))
results = list(q.stream())
print(f'5.2 Entities with "french" cuisine: {len(results)}')
print(f"    NOTE: Flutter app limit(200) caps visible results")
print(f"    NOTE: No result count displayed in Flutter app UI")

print()
print("=" * 60)
print("CATEGORY 6: Edge cases")
print("=" * 60)
print()

# 6.1 Empty query (no filters) - limited
q = col.limit(200)
results = list(q.stream())
print(f"6.1 No filters (limit 200): {len(results)} results")

# 6.2 Invalid field name
q = col.where(filter=firestore.FieldFilter("t_any_nonexistent", "array_contains", "test"))
results = list(q.stream())
print(f'6.2 Invalid field "t_any_nonexistent": {len(results)} results (silent empty)')

# 6.3 Case sensitivity deep-dive
q_exact = col.where(filter=firestore.FieldFilter("t_any_actors", "array_contains", "Huell Howser"))
q_lower = col.where(filter=firestore.FieldFilter("t_any_actors", "array_contains", "huell howser"))
results_exact = list(q_exact.stream())
results_lower = list(q_lower.stream())
print(f'6.3 Case: "Huell Howser" -> {len(results_exact)}, "huell howser" -> {len(results_lower)}')

# 6.4 Value with special characters
q = col.where(filter=firestore.FieldFilter("t_any_shows", "array_contains", "rick steves' europe"))
results = list(q.stream())
print(f"6.4 t_any_shows contains \"rick steves' europe\": {len(results)} results")

print()
print("=" * 60)
print("COMPOSITE INDEX ASSESSMENT")
print("=" * 60)
print()

# Test compound queries that may need indexes
combos = [
    ("t_any_cuisines", "array_contains", "french", "t_log_type", "==", "tripledb"),
    ("t_any_actors", "array_contains", "rick steves", "t_log_type", "==", "ricksteves"),
    ("t_any_countries", "array_contains", "france", "t_log_type", "==", "ricksteves"),
    ("t_any_dishes", "array_contains", "pasta", "t_log_type", "==", "tripledb"),
    ("t_any_keywords", "array_contains", "barbecue", "t_log_type", "==", "tripledb"),
]

for f1, op1, v1, f2, op2, v2 in combos:
    try:
        q = col.where(filter=firestore.FieldFilter(f1, op1, v1)).where(
            filter=firestore.FieldFilter(f2, op2, v2)
        )
        results = list(q.stream())
        print(f'  {f1} {op1} "{v1}" + {f2} {op2} "{v2}": {len(results)} results - OK')
    except Exception as e:
        err = str(e)
        if "index" in err.lower():
            print(f'  {f1} + {f2}: NEEDS INDEX - {err[:200]}')
        else:
            print(f'  {f1} + {f2}: ERROR - {err[:200]}')
