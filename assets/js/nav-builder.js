/**
 * nav-builder.js
 * Builds sidebar navigation HTML for all page types.
 */

class NavBuilder {
  static setSection(text) {
    const el = document.getElementById('nav-section-title');
    if (el) el.textContent = text;
  }

  static setItems(items) {
    const el = document.getElementById('nav-items');
    if (!el) return;
    el.innerHTML = items.map(({ href, label, active = false }) =>
      `<a class="nav-btn nav-sub-btn${active ? ' active' : ''}" href="${href}">${label}</a>`
    ).join('');
  }

  static forStoryline(storyline, activeId = 'index') {
    this.setSection(storyline.title);
    const items = [
      { href: 'index.html', label: 'Overview', active: activeId === 'index' },
      ...storyline.chapters.map((ch, i) => ({
        href: `${ch.id}.html`,
        label: `Ch.${i + 1} \u2014 ${ch.title}`,
        active: ch.id === activeId,
      })),
    ];
    this.setItems(items);
  }

  static forCharacters(characters, activeId) {
    this.setSection('Characters');
    this.setItems(characters.map(c => ({
      href: `${c.id}.html`,
      label: c.title,
      active: c.id === activeId,
    })));
  }

  static forGeography(geography, activeId) {
    this.setSection('Geography');
    this.setItems(geography.map(g => ({
      href: _url(`geography/${g.id}/`),
      label: g.title,
      active: g.id === activeId,
    })));
  }

  static forCity(geo, activeCityId) {
    this.setSection(geo.title);
    const items = [
      { href: _url(`geography/${geo.id}/`), label: 'Overview' },
      ...geo.locations.map(loc => ({
        href: `${loc.id}.html`,
        label: loc.title,
        active: loc.id === activeCityId,
      })),
    ];
    this.setItems(items);
  }
}
