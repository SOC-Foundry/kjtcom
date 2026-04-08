"""iao.doctor - Shared health checks for IAO environments.

Provides three levels:
- quick: configuration and structural integrity (sub-second)
- preflight: environment readiness for execution
- postflight: verification of iteration results and deployment
"""
import os
import sys
import json
import hashlib
import pathlib
import subprocess
from pathlib import Path
from iao.paths import find_project_root, IaoProjectNotFound

def _check_project_root():
    try:
        root = find_project_root()
        return ("ok", str(root))
    except IaoProjectNotFound as e:
        return ("fail", str(e))

def _check_iao_json():
    try:
        root = find_project_root()
        p = root / ".iao.json"
        if not p.exists():
            return ("fail", ".iao.json missing at root")
        data = json.loads(p.read_text())
        return ("ok", f"version {data.get('version', 'unknown')}")
    except Exception as e:
        return ("fail", f"error: {e}")

def _check_manifest():
    try:
        root = find_project_root()
        # Post-10.68.1 W1 rename: middleware lives at iao/
        middleware_home = root / "iao"
        m_path = middleware_home / "MANIFEST.json"
        if not m_path.exists():
            return ("warn", "MANIFEST.json missing")
        
        # Verify a few key files from manifest
        data = json.loads(m_path.read_text())
        files = data.get("files", {})
        if not files:
            return ("warn", "MANIFEST.json empty")
            
        checked = 0
        failed_files = []
        for rel_path, expected_hash in list(files.items()):
            p = middleware_home / rel_path
            if not p.exists():
                failed_files.append(f"{rel_path} (missing)")
                continue
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            if h != expected_hash:
                failed_files.append(f"{rel_path} (hash mismatch)")
            checked += 1
            
        if failed_files:
            return ("warn", f"MANIFEST integrity failed: {', '.join(failed_files[:2])}")
        return ("ok", f"MANIFEST verified ({len(files)} files)")
    except Exception as e:
        return ("warn", f"integrity check skipped: {e}")

def _check_shims():
    try:
        root = find_project_root()
        scripts_dir = root / "scripts"
        shims = ["query_registry.py", "build_context_bundle.py"]
        results = []
        for s in shims:
            p = scripts_dir / s
            if not p.exists():
                results.append(f"{s} missing")
                continue
            text = p.read_text()
            if "from iao" not in text and "import iao" not in text:
                results.append(f"{s} not shimmed")
        
        if results:
            return ("warn", ", ".join(results))
        return ("ok", "all shims resolve to package")
    except Exception:
        return ("warn", "shim check failed")

def _check_path():
    # Check if iao is on PATH
    try:
        r = subprocess.run(["which", "iao"], capture_output=True, text=True)
        if r.returncode == 0:
            return ("ok", r.stdout.strip())
        return ("warn", "iao CLI not on PATH")
    except Exception:
        return ("warn", "PATH check failed")

def _check_fish_marker():
    # Check if fish marker block is present exactly once
    config_path = Path.home() / ".config" / "fish" / "config.fish"
    if not config_path.exists():
        return ("ok", "fish config absent (non-fish system?)")
    
    try:
        content = config_path.read_text()
        count = content.count("# >>> iao-middleware >>>")
        if count == 1:
            return ("ok", "marker block present")
        elif count == 0:
            return ("warn", "marker block missing")
        else:
            return ("fail", f"multiple marker blocks found ({count})")
    except Exception as e:
        return ("warn", f"fish check error: {e}")

def _quick_checks():
    return {
        "project_root": _check_project_root(),
        "iao_json": _check_iao_json(),
        "manifest": _check_manifest(),
        "shims": _check_shims(),
        "path": _check_path(),
        "fish_marker": _check_fish_marker(),
    }

def _check_ollama():
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        if r.stdout.strip() == "200":
            return ("ok", "ollama up")
        return ("fail", f"ollama down (HTTP {r.stdout.strip()})")
    except Exception as e:
        return ("fail", f"ollama unreachable: {e}")

def _check_qwen():
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if "qwen" in r.stdout.lower():
            return ("ok", "qwen loaded")
        return ("fail", "qwen not pulled")
    except Exception:
        return ("warn", "qwen check failed")

def _check_python_deps():
    deps = ["litellm", "jsonschema", "playwright", "imagehash", "PIL"]
    missing = []
    for d in deps:
        try:
            __import__(d)
        except ImportError:
            missing.append(d)
    
    if missing:
        return ("fail", f"missing: {', '.join(missing)}")
    return ("ok", "all dependencies importable")

def _check_disk():
    try:
        r = subprocess.run(["df", "-h", str(Path.home())], capture_output=True, text=True)
        # /dev/nvme0n1p2  912G  127G  740G  15% /
        line = r.stdout.strip().splitlines()[-1]
        avail = line.split()[3]
        if avail.endswith("G"):
            val = float(avail[:-1])
            if val < 10:
                return ("fail", f"low disk space: {avail}")
            return ("ok", f"{avail} available")
        return ("ok", f"disk check: {avail}")
    except Exception:
        return ("warn", "disk check failed")

def _preflight_checks():
    return {
        "ollama": _check_ollama(),
        "qwen": _check_qwen(),
        "python_deps": _check_python_deps(),
        "disk": _check_disk(),
    }

def _load_plugins(dir_path: Path):
    """Dynamically load all .py plugins from a directory (10.69 W2)."""
    import importlib.util
    plugins = {}
    if not dir_path.exists():
        return plugins

    for p in dir_path.glob("*.py"):
        if p.name == "__init__.py":
            continue
        
        module_name = f"iao_plugin_{p.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(p))
        if spec and spec.loader:
            try:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "check"):
                    plugins[p.stem] = mod
            except Exception as e:
                print(f"[iao.doctor] Failed to load plugin {p.name}: {e}", file=sys.stderr)
    return plugins


def _postflight_checks():
    """Run dynamic post-flight plugins from base and project (10.69 W2)."""
    from iao.paths import find_project_root
    try:
        root = find_project_root()
        iao_json = root / ".iao.json"
        project_code = "kjtco" # default
        if iao_json.exists():
            project_code = json.loads(iao_json.read_text()).get("project_code", "kjtco")
    except Exception:
        root = Path.cwd()
        project_code = "kjtco"

    # Base plugins from the package itself
    package_dir = Path(__file__).parent / "postflight"
    base_plugins = _load_plugins(package_dir)
    
    # Project plugins from [project_code]/postflight
    project_dir = root / project_code / "postflight"
    project_plugins = _load_plugins(project_dir)
    
    # Merge, project overrides base if same name
    all_plugins = {**base_plugins, **project_plugins}
    
    results = {}
    for name, mod in all_plugins.items():
        try:
            res = mod.check()
            # Standardize output to (status, message)
            if isinstance(res, tuple) and len(res) == 2:
                results[name] = res
            else:
                results[name] = ("ok" if res else "fail", str(res))
        except Exception as e:
            results[name] = ("fail", f"error: {e}")
            
    return results

def run_all(level: str = "quick") -> dict[str, tuple[str, str]]:
    """
    Run health checks at the specified level.

    Returns: {check_name: (status, message)}
             status in {"ok", "warn", "fail", "deferred"}
    """
    checks = {}
    checks.update(_quick_checks())
    if level in ("preflight", "postflight"):
        checks.update(_preflight_checks())
    if level == "postflight":
        checks.update(_postflight_checks())
    return checks
