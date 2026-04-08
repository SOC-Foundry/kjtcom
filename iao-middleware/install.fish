#!/usr/bin/env fish
# iao-middleware install script - Linux + fish (Phase A, v10.66)
#
# Self-locates via (status filename). Walks up to find parent .iao.json.
# Copies components to ~/iao-middleware/. Writes idempotent fish config entries.

set -l SCRIPT_DIR (dirname (realpath (status filename)))
set -l cur $SCRIPT_DIR/..
while not test -f $cur/.iao.json
    if test "$cur" = "/"
        echo "ERROR: cannot find .iao.json walking up from $SCRIPT_DIR"
        exit 1
    end
    set cur (realpath $cur/..)
end
set -l PROJECT_ROOT $cur

echo "iao-middleware install"
echo "  source project: $PROJECT_ROOT"
echo "  source middleware: $SCRIPT_DIR"
echo "  destination: ~/iao-middleware/"
echo ""

# Compatibility check (if checker present)
if test -f $SCRIPT_DIR/lib/check_compatibility.py
    echo "Running compatibility check..."
    python3 $SCRIPT_DIR/lib/check_compatibility.py
    or begin
        echo "ERROR: compatibility check failed"
        exit 1
    end
else
    echo "(compatibility check deferred - W5 not yet shipped)"
end

# Copy components
mkdir -p ~/iao-middleware
cp -r $SCRIPT_DIR/bin ~/iao-middleware/
cp -r $SCRIPT_DIR/lib ~/iao-middleware/
cp -r $SCRIPT_DIR/prompts ~/iao-middleware/
cp -r $SCRIPT_DIR/templates ~/iao-middleware/
test -f $SCRIPT_DIR/MANIFEST.json; and cp $SCRIPT_DIR/MANIFEST.json ~/iao-middleware/
test -f $SCRIPT_DIR/COMPATIBILITY.md; and cp $SCRIPT_DIR/COMPATIBILITY.md ~/iao-middleware/
chmod +x ~/iao-middleware/bin/iao

# Idempotent fish config write
mkdir -p ~/.config/fish ~/.config/iao
touch ~/.config/fish/config.fish
set -l MARKER_BEGIN "# >>> iao-middleware >>>"
set -l MARKER_END "# <<< iao-middleware <<<"
if not grep -q "$MARKER_BEGIN" ~/.config/fish/config.fish
    printf "\n%s\n%s\n%s\n%s\n" \
        "$MARKER_BEGIN" \
        "set -gx PATH \$HOME/iao-middleware/bin \$PATH" \
        "test -f \$HOME/.config/iao/active.fish; and source \$HOME/.config/iao/active.fish" \
        "$MARKER_END" >> ~/.config/fish/config.fish
    echo "fish config: added iao-middleware block"
else
    echo "fish config: iao-middleware block already present (idempotent)"
end

echo ""
echo "Install complete. Open a new shell or:"
echo "  set -gx PATH ~/iao-middleware/bin \$PATH"
echo "  iao --version"
echo ""
echo "Next: iao project add kjtcom --gcp-project kjtcom-c78cd --prefix KJTCOM --path $PROJECT_ROOT"
