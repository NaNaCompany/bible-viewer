(() => {
  'use strict';
  const config = JSON.parse(document.querySelector('#page-config').textContent);
  const labels = config.labels;
  const toast = document.querySelector('#status');
  let timer;
  function notify(message) {
    clearTimeout(timer); toast.textContent = message;
    timer = setTimeout(() => { toast.textContent = ''; }, 4500);
  }
  function stored(key) { try { return localStorage.getItem(key); } catch { return null; } }
  function store(key, value) { try { localStorage.setItem(key, value); } catch {} }
  const savedTheme = stored('bible-viewer-theme');
  if (savedTheme === 'dark') document.documentElement.dataset.theme = 'dark';
  let fontSize = Number(stored('bible-viewer-font')) || 18.4;
  fontSize = Math.min(28, Math.max(16, fontSize));
  document.documentElement.style.setProperty('--verse-size', `${fontSize}px`);
  function urlFor(version, book = config.book, chapter = config.chapter) {
    return config.base + version + '/' + (book ? book + '/' + chapter + '/' : '');
  }
  document.querySelectorAll('[data-version-picker]').forEach(picker => {
    picker.addEventListener('change', () => {
      location.assign(urlFor(picker.value) + (/^#v[\da-z-]+$/.test(location.hash) ? location.hash : ''));
    });
  });
  const bookPicker = document.querySelector('#book-picker');
  if (bookPicker) bookPicker.addEventListener('change', () => location.assign(urlFor(config.version, bookPicker.value, 1)));
  const chapterPicker = document.querySelector('#chapter-picker');
  if (chapterPicker) chapterPicker.addEventListener('change', () => location.assign(urlFor(config.version, config.book, Number(chapterPicker.value))));
  const filter = document.querySelector('#book-filter');
  if (filter) filter.addEventListener('input', () => {
    const query = filter.value.trim().toLocaleLowerCase(); let visible = 0;
    document.querySelectorAll('.book').forEach(book => {
      book.hidden = !book.dataset.search.includes(query);
      if (!book.hidden) { visible++; if (query) book.open = true; }
    });
    document.querySelector('#no-results').hidden = visible > 0;
    document.querySelectorAll('.testament').forEach(section => { section.hidden = !Array.from(section.querySelectorAll('.book')).some(book => !book.hidden); });
  });
  const versePicker = document.querySelector('#verse-picker');
  function selectedVerse() {
    const requested = /^#v([\da-z-]+)$/.exec(location.hash);
    return requested?.[1] || versePicker?.value || '1';
  }
  function reflectHash() {
    const verse = selectedVerse();
    const exists = document.getElementById('v' + verse);
    if (versePicker && exists) versePicker.value = verse;
    else if (versePicker && location.hash.startsWith('#v')) notify(labels.missingVerse);
  }
  if (versePicker) versePicker.addEventListener('change', () => { location.hash = 'v' + versePicker.value; });
  window.addEventListener('hashchange', reflectHash); reflectHash();
  document.querySelectorAll('[data-preserve-hash]').forEach(link => link.addEventListener('click', () => {
    if (/^#v[\da-z-]+$/.test(location.hash)) link.hash = location.hash;
  }));
  function versePayload(verse) {
    const article = document.getElementById('v' + verse);
    if (!article) throw new Error('Missing verse');
    const text = article.querySelector('.verse-text').textContent;
    const reference = `${config.bookName} ${config.chapter}:${verse} · ${config.versionName}`;
    const url = config.canonical + '#v' + verse;
    return { title: reference, text: `${reference}\n${text}`, url, combined: `${reference}\n${text}\n${url}` };
  }
  async function copy(payload) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(payload.combined);
      return true;
    } catch {
      const area = document.createElement('textarea'); area.value = payload.combined;
      area.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(area);
      area.select(); let copied = false;
      try { copied = document.execCommand('copy'); } catch {}
      area.remove();
      if (copied) return true;
      const dialog = document.querySelector('#copy-dialog');
      dialog.querySelector('textarea').value = payload.combined; dialog.showModal();
      dialog.querySelector('textarea').focus(); dialog.querySelector('textarea').select();
      return false;
    }
  }
  async function share(payload) {
    // Native share receives both the literal verse text and its canonical URL.
    if (navigator.share) {
      try { await navigator.share({ title: payload.title, text: payload.text, url: payload.url }); notify(labels.shared); return; }
      catch (error) { if (error.name === 'AbortError') return; }
    }
    if (await copy(payload)) notify(labels.shareCopied);
  }
  document.addEventListener('click', async event => {
    const button = event.target.closest('button[data-action]'); if (!button) return;
    const action = button.dataset.action;
    if (action === 'theme') {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next; store('bible-viewer-theme', next);
      button.setAttribute('aria-pressed', String(next === 'dark')); return;
    }
    if (action === 'font-up' || action === 'font-down') {
      fontSize = Math.min(28, Math.max(16, fontSize + (action === 'font-up' ? 1.6 : -1.6)));
      document.documentElement.style.setProperty('--verse-size', `${fontSize}px`); store('bible-viewer-font', String(fontSize)); return;
    }
    if (action === 'close-dialog') { document.querySelector('#copy-dialog').close(); return; }
    if (action === 'copy' || action === 'share' || action === 'share-selected') {
      button.disabled = true;
      try {
        const requested = action === 'share-selected' ? selectedVerse() : button.closest('.verse').dataset.verse;
        const verse = document.getElementById('v' + requested) ? requested : versePicker.value;
        const payload = versePayload(verse);
        if (action === 'copy') { if (await copy(payload)) notify(labels.copied); }
        else await share(payload);
      } catch { notify(labels.actionFailed); }
      finally { button.disabled = false; }
    }
  });
  const themeButton = document.querySelector('[data-action=theme]');
  if (themeButton) themeButton.setAttribute('aria-pressed', String(document.documentElement.dataset.theme === 'dark'));
})();
