"""
garbage_collector.py — Removes stale shell pages and generated HTML files.

When you delete a .docx from content/, this ensures the corresponding
shell pages and generated/ HTML files are also cleaned up.
"""

import os


class GarbageCollector:
    """
    Compares what exists on disk against what the manifest says should exist.
    Deletes anything extra. Also removes empty directories.
    """

    SKIP_DIRS = {'media'}

    # Directories at repo root that contain shell pages
    SHELL_DIRS = {'characters', 'storylines', 'geography'}

    # Directories to never touch during GC
    PROTECTED = {'generated', 'content', 'assets', 'scripts', '.github', '_site'}

    def __init__(self, manifest: dict):
        self.manifest = manifest
        self._expected_generated: set[str] = set()
        self._expected_shell: set[str] = set()

    def run(self) -> None:
        print('\nRunning garbage collection...')
        self._build_expected_sets()
        stale = self._find_stale()
        if not stale:
            print('  Nothing to clean up.')
            return
        for path in sorted(stale):
            self._delete(path)

    # ── expected set ──────────────────────────────────────────────────────────

    def _build_expected_sets(self) -> None:
        for sl in self.manifest['storylines']:
            self._expect_shell(f"storylines/{sl['id']}/index.html")
            self._expect_generated(f"storylines/{sl['id']}/index.html")
            for ch in sl['chapters']:
                self._expect_shell(f"storylines/{sl['id']}/{ch['id']}.html")
                self._expect_generated(f"storylines/{sl['id']}/{ch['id']}.html")

        self._expect_shell('characters/index.html')
        for char in self.manifest['characters']:
            self._expect_shell(f"characters/{char['id']}.html")
            self._expect_generated(f"characters/{char['id']}.html")

        for geo in self.manifest['geography']:
            self._expect_shell(f"geography/{geo['id']}/index.html")
            self._expect_generated(f"geography/{geo['id']}/index.html")
            for loc in geo['locations']:
                self._expect_shell(f"geography/{geo['id']}/{loc['id']}.html")
                self._expect_generated(f"geography/{geo['id']}/{loc['id']}.html")

    def _expect_shell(self, relative: str) -> None:
        self._expected_shell.add(relative)

    def _expect_generated(self, relative: str) -> None:
        self._expected_generated.add(f'generated/{relative}')

    # ── stale detection ───────────────────────────────────────────────────────

    def _find_stale(self) -> set[str]:
        actual_generated = self._collect('generated')
        actual_shell = self._collect_shell()
        return (actual_generated - self._expected_generated) | \
               (actual_shell - self._expected_shell)

    def _collect_shell(self) -> set[str]:
        """Collect shell HTML files from known shell dirs at repo root."""
        found: set[str] = set()
        for shell_dir in self.SHELL_DIRS:
            if not os.path.isdir(shell_dir):
                continue
            for dirpath, dirs, files in os.walk(shell_dir):
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
                for fname in files:
                    if fname.endswith('.html'):
                        found.add(
                            os.path.join(dirpath, fname).replace(os.sep, '/')
                        )
        return found

    def _collect(self, root: str) -> set[str]:
        found: set[str] = set()
        if not os.path.exists(root):
            return found
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for fname in files:
                if fname.endswith('.html'):
                    found.add(
                        os.path.join(dirpath, fname).replace(os.sep, '/')
                    )
        return found

    # ── deletion ─────────────────────────────────────────────────────────────

    def _delete(self, path: str) -> None:
        try:
            os.remove(path)
            print(f'  Deleted: {path}')
            self._remove_if_empty(os.path.dirname(path))
        except FileNotFoundError:
            pass

    def _remove_if_empty(self, directory: str) -> None:
        try:
            if directory and os.path.isdir(directory) and not os.listdir(directory):
                os.rmdir(directory)
                print(f'  Removed empty dir: {directory}')
        except Exception:
            pass
