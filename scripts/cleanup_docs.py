"""Clean up docs/ directory per v9.48 file management rules."""
import os
import glob

def cleanup():
    # 1. Delete orphaned changelog-v*.md files in docs/
    for f in glob.glob("docs/changelog-v*.md"):
        print(f"DELETE: {f} (content in kjtcom-changelog.md)")
        os.remove(f)

    # 2. Find duplicates between docs/ and archive/
    docs_files = set(os.path.basename(f) for f in glob.glob("docs/kjtcom-*.md"))
    archive_files = set(os.path.basename(f) for f in glob.glob("docs/archive/kjtcom-*.md"))
    duplicates = docs_files & archive_files
    for dup in duplicates:
        # Keep archive copy, remove docs/ copy (unless it's current iteration)
        current_iter = os.environ.get("IAO_ITERATION", "").replace("v", "")
        if current_iter and current_iter not in dup:
            print(f"DUPLICATE: docs/{dup} (also in archive/)")
            os.remove(os.path.join("docs", dup))

    # 3. Clean drafts
    for f in glob.glob("docs/drafts/*.md"):
        print(f"CLEAN DRAFT: {f}")
        os.remove(f)

    # 4. Verify single changelog
    if not os.path.exists("docs/kjtcom-changelog.md"):
        print("Missing main changelog! Creating it...")
        with open("docs/kjtcom-changelog.md", "w") as f:
            f.write("# kjtcom - Unified Changelog\n\n")
    else:
        print("Main changelog exists: docs/kjtcom-changelog.md")

if __name__ == "__main__":
    cleanup()
