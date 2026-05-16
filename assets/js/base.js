/**
 * base.js — Loaded first on every shell page.
 * Defines _BASE and _url() used by all other JS files.
 *
 * All shell pages use /worldbuilding/ prefixed paths.
 * On GitHub Pages: /worldbuilding/ is the repo root — paths work natively.
 * On localhost: serve.py strips /worldbuilding/ prefix before resolving files.
 */

const _BASE = '/worldbuilding/';

function _url(path) {
  return _BASE + path;
}
