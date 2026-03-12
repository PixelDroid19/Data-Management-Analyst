#!/usr/bin/env python3
"""Deploy the pre-built docs viewer into a target repository.

This is THE script the AI must call to set up documentation in any analyzed repo.
It handles everything: scaffolding, viewer deployment, manifest generation, and verification.

Usage:
    python deploy_viewer.py --target-repo /path/to/analyzed-repo

What it does:
    1. Creates docs/, docs/flows/, docs/flows/diagrams/ if they don't exist
    2. Creates docs/README.md and docs/flows/README.md if missing
    3. Copies the pre-built viewer (index.html, app.js, styles.css) into docs/site/
    4. Scans all .md files in docs/ and generates docs/site/manifest.json
    5. Verifies all 4 required files exist and are valid

The AI does NOT need to generate any HTML, JS, or CSS — everything is pre-built.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path


def skill_root() -> Path:
    """Return the sdd-docs-viewer skill root directory."""
    return Path(__file__).resolve().parents[1]


def resolve_target(target_arg: str | None) -> Path:
    """Resolve the target repo. Uses --target-repo or falls back to cwd."""
    if target_arg:
        p = Path(target_arg).resolve()
        if not p.exists():
            print(f"ERROR: Target repo does not exist: {p}")
            sys.exit(1)
        return p
    return Path.cwd().resolve()


# ── Step 1: Scaffold docs structure ────────────────────────────
def scaffold_docs(target: Path) -> Path:
    """Create the docs/ folder structure if it doesn't exist."""
    docs = target / 'docs'
    flows = docs / 'flows'
    diagrams = flows / 'diagrams'
    site = docs / 'site'

    for d in [docs, flows, diagrams, site]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d.relative_to(target)}/")

    # Create README files if missing
    docs_readme = docs / 'README.md'
    if not docs_readme.exists():
        docs_readme.write_text(
            '# Documentación técnica\n\n'
            'Documentación generada por el pipeline SDD.\n\n'
            '## Flujos documentados\n\n'
            'Ver [`flows/`](flows/) para la documentación de cada flujo investigado.\n\n'
            '## Viewer interactivo\n\n'
            'Abrir [`site/index.html`](site/index.html) en un navegador para ver la documentación.\n',
            encoding='utf-8',
        )
        print(f"  ✓ Created {docs_readme.relative_to(target)}")

    flows_readme = flows / 'README.md'
    if not flows_readme.exists():
        flows_readme.write_text(
            '# Flujos documentados\n\n'
            'Esta carpeta contiene la documentación técnica de cada flujo investigado.\n\n'
            'Cada archivo `.md` documenta un flujo completo: DM, cadena de servicios, payload, canales, y navegación.\n',
            encoding='utf-8',
        )
        print(f"  ✓ Created {flows_readme.relative_to(target)}")

    return docs


# ── Step 2: Copy pre-built viewer assets ───────────────────────
def deploy_assets(skill: Path, site_dir: Path) -> None:
    """Copy the pre-built viewer files from skill assets/ to docs/site/."""
    assets = skill / 'assets'

    for filename in ['index.html', 'app.js', 'styles.css']:
        src = assets / filename
        dst = site_dir / filename
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ Deployed {filename}")
        else:
            print(f"  ✗ WARNING: {src} not found in skill assets")


# ── Step 3: Build manifest ─────────────────────────────────────
def build_manifest(skill: Path, docs_root: Path, site_dir: Path) -> None:
    """Run build_manifest.py to generate manifest.json from docs/ content."""
    build_script = skill / 'scripts' / 'build_manifest.py'
    subprocess.run(
        [
            sys.executable, str(build_script),
            '--docs-root', str(docs_root),
            '--viewer-dir', str(site_dir),
            '--manifest-path', str(site_dir / 'manifest.json'),
        ],
        check=True,
    )
    print("  ✓ manifest.json generated")


# ── Step 4: Verify deployment ──────────────────────────────────
REQUIRED_FILES = ['index.html', 'app.js', 'styles.css', 'manifest.json']


def verify(site_dir: Path) -> bool:
    """Verify all required files exist and are valid. Returns True if OK."""
    ok = True

    for f in REQUIRED_FILES:
        path = site_dir / f
        if not path.exists():
            print(f"  ✗ MISSING: {f}")
            ok = False
        elif path.stat().st_size == 0:
            print(f"  ✗ EMPTY: {f}")
            ok = False
        else:
            print(f"  ✓ {f} ({path.stat().st_size:,} bytes)")

    # Validate manifest JSON
    manifest = site_dir / 'manifest.json'
    if manifest.exists() and manifest.stat().st_size > 0:
        try:
            data = json.loads(manifest.read_text(encoding='utf-8'))
            doc_count = len(data.get('docs', []))
            print(f"  ✓ manifest.json contains {doc_count} document(s)")
        except json.JSONDecodeError as e:
            print(f"  ✗ manifest.json is invalid JSON: {e}")
            ok = False

    return ok


# ── Main ───────────────────────────────────────────────────────
def main() -> None:
    parser = ArgumentParser(
        description='Deploy the pre-built docs viewer into a target repository.',
        epilog='This is the ONLY script needed. It scaffolds docs/, deploys the viewer, and builds the manifest.',
    )
    parser.add_argument(
        '--target-repo',
        help='Path to the repo being analyzed. Defaults to current working directory.',
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify an existing deployment without rebuilding.',
    )
    args = parser.parse_args()

    target = resolve_target(args.target_repo)
    skill = skill_root()
    site_dir = target / 'docs' / 'site'

    print(f"\n{'='*60}")
    print(f"SDD Docs Viewer — Deploy")
    print(f"{'='*60}")
    print(f"Target repo : {target}")
    print(f"Skill source: {skill}")
    print(f"Deploy to   : {site_dir}")
    print(f"{'='*60}\n")

    if args.verify_only:
        print("Step: Verify existing deployment\n")
        if verify(site_dir):
            print("\n✅ Verification PASSED")
        else:
            print("\n❌ Verification FAILED")
            sys.exit(1)
        return

    # Full deployment
    print("Step 1/4: Scaffold docs/ structure\n")
    docs_root = scaffold_docs(target)

    print("\nStep 2/4: Deploy pre-built viewer assets\n")
    deploy_assets(skill, site_dir)

    print("\nStep 3/4: Build manifest from docs/ content\n")
    build_manifest(skill, docs_root, site_dir)

    print("\nStep 4/4: Verify deployment\n")
    if verify(site_dir):
        print(f"\n✅ Viewer deployed successfully!")
        print(f"   Open {site_dir / 'index.html'} in a browser.")
        print(f"   Add .md files to {docs_root / 'flows'}/ and re-run to refresh.")
    else:
        print(f"\n❌ Deployment FAILED — check errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
