from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / 'skills').exists() and ((parent / 'agents').exists() or (parent / '.github').exists()):
            return parent
    raise RuntimeError(
        'Unable to resolve repository root for docs viewer scripts. '
        'Make sure this script is located inside a skill directory within a repo '
        'that has a "skills/" folder and either "agents/" or ".github/".'
    )


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def extract_title(path: Path) -> str:
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return path.stem.replace('-', ' ').replace('_', ' ').title()


def extract_description(path: Path) -> str:
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        return stripped[:180]
    return ''


def count_words(path: Path) -> int:
    try:
        text = path.read_text(encoding='utf-8')
        return len(text.split())
    except Exception:
        return 0


def last_modified_iso(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
        dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return ''


def category_for(docs_root: Path, path: Path) -> str:
    relative = path.relative_to(docs_root)
    if relative == Path('README.md'):
        return 'Overview'
    if relative.parts and relative.parts[0] == 'flows':
        return 'Flows'
    return 'Docs'


def collect_docs(docs_root: Path, viewer_dir: Path) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []

    if not docs_root.exists():
        return docs

    for path in sorted(docs_root.rglob('*.md')):
        if viewer_dir == path.parent or viewer_dir in path.parents:
            continue
        relative_to_docs = path.relative_to(docs_root)
        if relative_to_docs.parts and relative_to_docs.parts[0] == 'site':
            continue
        if 'diagrams' in path.parts:
            continue

        word_count = count_words(path)
        modified = last_modified_iso(path)

        entry: dict[str, str | int] = {
            'slug': '-'.join(relative_to_docs.with_suffix('').parts),
            'title': extract_title(path),
            'path': Path(os.path.relpath(path, start=viewer_dir)).as_posix(),
            'sourcePath': Path('docs', relative_to_docs).as_posix(),
            'category': category_for(docs_root, path),
            'description': extract_description(path),
        }

        if word_count > 0:
            entry['wordCount'] = word_count
        if modified:
            entry['lastModified'] = modified

        docs.append(entry)

    docs.sort(key=lambda item: (item['category'], item['title'].lower()))
    return docs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build a manifest for the docs viewer.')
    parser.add_argument('--docs-root', help='Docs root to index. Defaults to <repo>/docs.')
    parser.add_argument('--viewer-dir', help='Viewer directory used to compute relative fetch paths.')
    parser.add_argument('--manifest-path', help='Manifest output path. Defaults to <viewer-dir>/manifest.json.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    root = repo_root()
    viewer_dir = Path(args.viewer_dir).resolve() if args.viewer_dir else (skill_root() / 'assets')
    docs_root = Path(args.docs_root).resolve() if args.docs_root else (root / 'docs')
    manifest_path = Path(args.manifest_path).resolve() if args.manifest_path else (viewer_dir / 'manifest.json')

    manifest = {
        'generatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'docs': collect_docs(docs_root, viewer_dir),
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    doc_count = len(manifest['docs'])
    print(f'Wrote {manifest_path} with {doc_count} document{"s" if doc_count != 1 else ""}.')


if __name__ == '__main__':
    main()
