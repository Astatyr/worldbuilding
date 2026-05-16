"""
build.py — Local build script.
This file is gitignored and never pushed to the repo.

Converts all .docx files with pandoc, then runs generate.py to produce
the manifest, shell pages, and garbage collection.

Run from repo root before committing:
    python build.py

Then commit and push the generated files — no GitHub Action needed.
"""

import os
import sys
import subprocess


# ── helpers ───────────────────────────────────────────────────────────────────

def find_pandoc() -> str:
    """Find pandoc on Windows or Unix."""
    candidates = [
        'pandoc',
        r'C:\Program Files\Pandoc\pandoc.exe',
        r'C:\Program Files (x86)\Pandoc\pandoc.exe',
        os.path.expanduser(r'~\AppData\Local\Pandoc\pandoc.exe'),
    ]
    for cmd in candidates:
        try:
            r = subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
            if r.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return ''


def run(cmd: list, description: str) -> bool:
    """Run a command, print description, return True if successful."""
    print(f"{description}...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  FAILED: {description}")
        return False
    return True


# ── Step 1: Convert .docx files ───────────────────────────────────────────────

def convert_docx(pandoc: str) -> None:
    print("Converting .docx files...")
    converted = 0
    skipped = 0

    for root, dirs, files in os.walk('content'):
        dirs[:] = [d for d in dirs if d != '_font_backup']
        for fname in sorted(files):
            if not fname.endswith('.docx') or fname.startswith('~$'):
                continue

            docx_path = os.path.join(root, fname)
            html_path = docx_path.replace('content' + os.sep, 'generated' + os.sep)
            html_path = html_path[:-5] + '.html'

            os.makedirs(os.path.dirname(html_path), exist_ok=True)

            result = subprocess.run(
                [pandoc, docx_path,
                 '--from', 'docx',
                 '--to', 'html',
                 '--no-highlight',
                 '--wrap=none',
                 '--extract-media=generated/media',
                 '-o', html_path],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  OK: {docx_path}")
                converted += 1
            else:
                print(f"  SKIPPED (error): {docx_path}")
                if result.stderr:
                    print(f"    {result.stderr.strip()}")
                skipped += 1

    print(f"  {converted} converted, {skipped} skipped.\n")


# ── Step 2: Compress images ───────────────────────────────────────────────────

def compress_images() -> None:
    """Image compression skipped on Windows — optipng/jpegoptim are Linux only.
    Images are compressed automatically on the GitHub Actions runner if you
    ever re-enable the workflow."""
    pass


# ── Step 3: Run generate.py ───────────────────────────────────────────────────

def run_generator() -> None:
    print("Running site generator...")
    result = subprocess.run([sys.executable, 'scripts/generate.py'])
    if result.returncode != 0:
        print("\ngenerate.py failed.")
        sys.exit(1)
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.path.exists('content'):
        print('ERROR: Run from your repo root, not a subfolder.')
        sys.exit(1)

    pandoc = find_pandoc()
    if not pandoc:
        print('ERROR: pandoc not found.')
        print('Install from https://pandoc.org/installing.html')
        sys.exit(1)

    print(f'Using pandoc: {pandoc}\n')

    convert_docx(pandoc)
    compress_images()
    run_generator()

    print('Build complete. Review the output, then commit and push.')
