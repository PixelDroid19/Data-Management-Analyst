from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_target_repo(target_arg: str | None) -> Path:
    """Resolve the target repo where docs will be deployed.

    Priority:
    1. --target-repo argument (explicit path from user or AI)
    2. Current working directory (cwd)
    """
    if target_arg:
        target = Path(target_arg).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Target repo does not exist: {target}")
        return target
    return Path.cwd().resolve()


def sync_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"  Synced {destination}")


def build_export_manifest(scripts_dir: Path, docs_root: Path, export_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(scripts_dir / 'build_manifest.py'),
            '--docs-root', str(docs_root),
            '--viewer-dir', str(export_dir),
            '--manifest-path', str(export_dir / 'manifest.json'),
        ],
        check=True,
    )


def export_viewer(skill: Path, export_dir: Path) -> None:
    """Copy the pre-built viewer assets into the target export directory."""
    assets_dir = skill / 'assets'
    export_dir.mkdir(parents=True, exist_ok=True)

    for filename in ['index.html', 'app.js', 'styles.css', 'README.md']:
        source = assets_dir / filename
        if source.exists():
            sync_file(source, export_dir / filename)
        else:
            print(f"  Warning: source asset not found: {source}")


REQUIRED_EXPORT_FILES = ['index.html', 'app.js', 'styles.css', 'manifest.json']


def verify_export(export_dir: Path) -> list[str]:
    """Verify the exported site has all required files. Returns list of issues."""
    issues: list[str] = []

    for filename in REQUIRED_EXPORT_FILES:
        filepath = export_dir / filename
        if not filepath.exists():
            issues.append(f"Missing: {filepath}")
        elif filepath.stat().st_size == 0:
            issues.append(f"Empty file: {filepath}")

    manifest_path = export_dir / 'manifest.json'
    if manifest_path.exists() and manifest_path.stat().st_size > 0:
        try:
            data = json.loads(manifest_path.read_text(encoding='utf-8'))
            if 'docs' not in data:
                issues.append("manifest.json is missing the 'docs' field")
            elif not isinstance(data['docs'], list):
                issues.append("manifest.json 'docs' field is not an array")
        except json.JSONDecodeError as e:
            issues.append(f"manifest.json is invalid JSON: {e}")

    return issues


def ensure_docs_structure(target_repo: Path) -> Path:
    """Create docs/ folder structure if it doesn't exist. Returns docs_root."""
    docs_root = target_repo / 'docs'
    flows_dir = docs_root / 'flows'
    diagrams_dir = flows_dir / 'diagrams'

    for d in [docs_root, flows_dir, diagrams_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Create README.md files if they don't exist
    docs_readme = docs_root / 'README.md'
    if not docs_readme.exists():
        docs_readme.write_text(
            '# Documentación\n\nDocumentación técnica generada por el pipeline SDD.\n\n'
            '## Flujos documentados\n\nVer `flows/` para la documentación de cada flujo.\n\n'
            '## Viewer\n\nAbrir `site/index.html` en un navegador para ver la documentación con el viewer interactivo.\n',
            encoding='utf-8',
        )
        print(f"  Created {docs_readme}")

    flows_readme = flows_dir / 'README.md'
    if not flows_readme.exists():
        flows_readme.write_text(
            '# Flujos documentados\n\nEsta carpeta contiene la documentación técnica de cada flujo investigado.\n',
            encoding='utf-8',
        )
        print(f"  Created {flows_readme}")

    return docs_root


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Deploy the pre-built docs viewer into a target repo and generate the manifest.'
    )
    parser.add_argument(
        '--target-repo',
        help='Path to the repo being analyzed. Defaults to current working directory. '
             'The viewer will be deployed to <target-repo>/docs/site/.',
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify an existing export without rebuilding.',
    )
    args = parser.parse_args()

    skill = skill_root()
    scripts_dir = skill / 'scripts'
    target_repo = resolve_target_repo(args.target_repo)

    print(f"Target repo: {target_repo}")
    print(f"Skill source: {skill}")

    if args.verify_only:
        export_dir = target_repo / 'docs' / 'site'
        issues = verify_export(export_dir)
        if issues:
            print(f"\nVerification FAILED for {export_dir}:")
            for issue in issues:
                print(f"  ✗ {issue}")
            sys.exit(1)
        else:
            print(f"\nVerification PASSED: all {len(REQUIRED_EXPORT_FILES)} required files present in {export_dir}")
        return

    # Step 1: Ensure docs/ structure exists in target repo
    print("\n1. Ensuring docs/ structure...")
    docs_root = ensure_docs_structure(target_repo)

    # Step 2: Copy pre-built viewer assets to docs/site/
    export_dir = target_repo / 'docs' / 'site'
    print(f"\n2. Deploying viewer to {export_dir}...")
    export_viewer(skill, export_dir)

    # Step 3: Build manifest from docs/ content
    print("\n3. Building manifest...")
    build_export_manifest(scripts_dir, docs_root, export_dir)

    # Step 4: Verify
    print("\n4. Verifying export...")
    issues = verify_export(export_dir)
    if issues:
        print(f"\nExport verification FAILED:")
        for issue in issues:
            print(f"  ✗ {issue}")
        sys.exit(1)
    else:
        print(f"\n✅ Viewer deployed successfully to {export_dir}")
        print(f"   Open {export_dir / 'index.html'} in a browser to view documentation.")
        print(f"   Verification PASSED: all {len(REQUIRED_EXPORT_FILES)} required files present.")


if __name__ == '__main__':
    main()