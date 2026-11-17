// YouTube Studio upload routine. Set window.__U = {url, name, title, desc, pl} on the upload page, then run this.
(async () => {
  const U = window.__U; const W = ms => new Promise(r => setTimeout(r, ms));
  const inp = document.querySelector('ytcp-uploads-file-picker input[type=file]') || document.querySelector('input[type=file]');
  const b = await (await fetch(U.url)).blob();
  const dt = new DataTransfer(); dt.items.add(new File([b], U.name, { type: 'video/mp4' }));
  inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  await W(9000);
  const boxes = [...document.querySelectorAll('ytcp-uploads-dialog #textbox[contenteditable=true]')];
  const put = (el, t) => { el.focus(); document.execCommand('selectAll'); document.execCommand('insertText', false, t); el.blur(); };
  put(boxes[0], U.title); put(boxes[1], U.desc);
  const d = document.querySelector('ytcp-uploads-dialog');
  d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').click();
  d.querySelector('#toggle-button')?.click(); await W(1500);
  d.querySelector('tp-yt-paper-radio-button[name=VIDEO_HAS_ALTERED_CONTENT_YES]').click();
  const t = d.querySelector('ytcp-video-metadata-playlists ytcp-dropdown-trigger'); t.scrollIntoView({ block: 'center' }); t.click(); await W(1500);
  const li = [...document.querySelectorAll('ytcp-playlist-dialog li')].find(x => x.offsetParent && x.innerText.trim().startsWith(U.pl));
  const cb = li && li.querySelector('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role=checkbox]'); (cb || li) && (cb || li).click(); await W(500);
  const ok = [...document.querySelectorAll('ytcp-playlist-dialog ytcp-button, ytcp-playlist-dialog button')].find(x => x.offsetParent && /^\s*OK\s*$/i.test(x.innerText)); ok && ok.click(); await W(800);
  const l = d.querySelector('#language-input ytcp-dropdown-trigger, ytcp-form-language-input ytcp-dropdown-trigger'); l.scrollIntoView({ block: 'center' }); l.click(); await W(1200);
  const it = [...document.querySelectorAll('tp-yt-paper-item')].find(x => x.offsetParent && /^\s*Arabe\s*$/.test(x.innerText)); it && it.click(); await W(800);
  for (let i = 0; i < 3; i++) { d.querySelector('#next-button').click(); await W(1800); }
  d.querySelector('#second-container-expand-button').click();
  window.__R = b.size + ' li=' + !!li + ' link=' + ((d.innerText.match(/https:\/\/youtube\.com\/shorts\/\S+/) || [''])[0]);
})();
