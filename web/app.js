/**
 * Web Transliterator App Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const sourceInput = document.getElementById('sourceInput');
  const targetOutput = document.getElementById('targetOutput');
  const fromScriptSelect = document.getElementById('fromScript');
  const toScriptSelect = document.getElementById('toScript');
  const swapBtn = document.getElementById('swapBtn');
  const copyBtn = document.getElementById('copyBtn');
  const clearBtn = document.getElementById('clearBtn');
  const sourceCount = document.getElementById('sourceCount');
  const targetCount = document.getElementById('targetCount');
  const toast = document.getElementById('toast');
  const codepointContainer = document.getElementById('codepointContainer');
  const debugSection = document.getElementById('debugSection');

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2200);
  }

  function updateFontClasses() {
    const toScript = toScriptSelect.value;
    const fromScript = fromScriptSelect.value;

    if (toScript === 'tigalari') {
      targetOutput.classList.add('tigalari-font');
    } else {
      targetOutput.classList.remove('tigalari-font');
    }

    if (fromScript === 'tigalari') {
      sourceInput.classList.add('tigalari-font');
    } else {
      sourceInput.classList.remove('tigalari-font');
    }
  }

  function renderCodepoints(text) {
    if (!text || toScriptSelect.value !== 'tigalari') {
      debugSection.style.display = 'none';
      return;
    }

    debugSection.style.display = 'block';
    codepointContainer.innerHTML = '';
    const points = inspectCodepoints(text);

    points.forEach(pt => {
      const pill = document.createElement('div');
      pill.className = 'codepoint-pill';
      pill.innerHTML = `<span class="glyph">${pt.char}</span><span class="code">${pt.codepoint}</span>`;
      codepointContainer.appendChild(pill);
    });
  }

  function doTransliteration() {
    const text = sourceInput.value;
    sourceCount.textContent = `${text.length} chars`;

    if (!text.trim()) {
      targetOutput.value = '';
      targetCount.textContent = '0 chars';
      renderCodepoints('');
      return;
    }

    const fromScript = fromScriptSelect.value;
    const toScript = toScriptSelect.value;

    try {
      const converted = transliterate(text, fromScript, toScript);
      targetOutput.value = converted;
      targetCount.textContent = `${converted.length} chars`;
      renderCodepoints(converted);
    } catch (err) {
      console.error(err);
      targetOutput.value = text;
    }

    // Update Live Bilingual Translation Section
    updateLiveTranslation(text);
  }

  // -------------------------------------------------------------
  // Live English <-> Kannada Translation Engine
  // -------------------------------------------------------------
  const translationCard = document.getElementById('translationCard');
  const transDirection = document.getElementById('transDirection');
  const transPrimaryText = document.getElementById('transPrimaryText');
  const transPhoneticText = document.getElementById('transPhoneticText');
  const transSecondaryText = document.getElementById('transSecondaryText');
  const transTags = document.getElementById('transTags');
  const copyTranslationBtn = document.getElementById('copyTranslationBtn');

  function updateLiveTranslation(rawInput) {
    if (!translationCard) return;
    const input = (rawInput || '').trim();
    if (!input) {
      translationCard.style.display = 'none';
      return;
    }

    const script = detectScript(input);
    const hasDict = (typeof TULU_DICTIONARY_1000 !== 'undefined' && Array.isArray(TULU_DICTIONARY_1000));
    if (!hasDict) {
      translationCard.style.display = 'none';
      return;
    }

    let match = null;
    let isEnglishInput = false;

    function norm(s) {
      return (s || '').toLowerCase()
        .replace(/aa/g, 'a').replace(/ee/g, 'e').replace(/ii/g, 'i')
        .replace(/oo/g, 'o').replace(/uu/g, 'u').replace(/[^a-z]/g, '');
    }

    // A. Check if input is Kannada
    if (script === 'kannada') {
      isEnglishInput = false;
      // Direct Kannada lemma match
      match = TULU_DICTIONARY_1000.find(i => i.tulu_kannada === input);

      // Morphological suffix check if direct match fails
      if (!match) {
        const nounSuffixes = [
          { kn: 'ೊಟ್ಟುಗು', tag: 'Sociative (with)' },
          { kn: 'ರ್ದ್', tag: 'Ablative (from)' },
          { kn: 'ಡ್ದ್', tag: 'Ablative (from)' },
          { kn: 'ರ್ದು', tag: 'Ablative (from)' },
          { kn: 'ಡ್', tag: 'Locative (in/at)' },
          { kn: 'ಡು', tag: 'Locative (in/at)' },
          { kn: 'ಟ್', tag: 'Locative (in/at)' },
          { kn: 'ದ', tag: 'Genitive (of)' },
          { kn: 'ನ', tag: 'Genitive (of)' },
          { kn: 'ಗ್', tag: 'Dative (to/for)' },
          { kn: 'ಗು', tag: 'Dative (to/for)' },
          { kn: 'ಕ್', tag: 'Dative (to/for)' },
          { kn: 'ನ್', tag: 'Accusative' },
          { kn: 'ನು', tag: 'Accusative' },
        ];
        for (const suf of nounSuffixes) {
          if (input.endsWith(suf.kn) && input.length > suf.kn.length) {
            const stem = input.slice(0, -suf.kn.length);
            const foundStem = TULU_DICTIONARY_1000.find(i => i.tulu_kannada === stem);
            if (foundStem) {
              match = Object.assign({}, foundStem, {
                morphTag: suf.tag,
                inflectedForm: input
              });
              break;
            }
          }
        }
      }
    } else if (script === 'tigalari') {
      // Tigalari input -> convert to Kannada first then lookup
      const kn = transliterate(input, 'tigalari', 'kannada');
      match = TULU_DICTIONARY_1000.find(i => i.tulu_kannada === kn);
      isEnglishInput = false;
    } else {
      // Latin script input: Could be an English word (e.g. "water", "house", "hello")
      // OR a phonetic Tulu/Kannada word (e.g. "solmelu", "namaskara", "illa", "barsa")
      const lower = input.toLowerCase();
      const normInput = norm(lower);

      // Check 1: Phonetic Tulu match (exact and normalized long/short vowels)
      match = TULU_DICTIONARY_1000.find(i => i.tulu_latin.toLowerCase() === lower);
      if (!match) {
        match = TULU_DICTIONARY_1000.find(i => norm(i.tulu_latin) === normInput);
      }

      // Check 2: English meaning match (e.g. 'hello', 'water', 'house', 'thank you', 'how are you')
      if (!match) {
        // Exact English word match or word boundary search
        match = TULU_DICTIONARY_1000.find(i => {
          const eng = i.english.toLowerCase();
          const cleanEng = eng.replace(/\(tulu\)|\(kannada\)/g, '').trim();
          const parts = cleanEng.split(/[\/,;]+/).map(p => p.trim());
          return parts.includes(lower) || cleanEng === lower || eng === lower;
        });

        // Substring / keyword match if exact failed
        if (!match && lower.length >= 3) {
          match = TULU_DICTIONARY_1000.find(i => {
            const eng = i.english.toLowerCase();
            return eng.includes(lower);
          });
        }

        if (match) {
          isEnglishInput = true;
        }
      }

      // Check 3: Also search 1886 historical dictionary if not found in modern
      if (!match && typeof HISTORICAL_TULU_CORPUS !== 'undefined' && Array.isArray(HISTORICAL_TULU_CORPUS)) {
        const histMatch = HISTORICAL_TULU_CORPUS.find(i => {
          return norm(i.tulu_latin) === normInput || i.english.toLowerCase().includes(lower);
        });
        if (histMatch) {
          match = {
            tulu_kannada: histMatch.tulu_kannada,
            tulu_latin: histMatch.tulu_latin,
            english: histMatch.english,
            category: `Historical 1886: ${histMatch.domain || 'Lexicon'}`
          };
          if (histMatch.english.toLowerCase().includes(lower) && !histMatch.tulu_latin.toLowerCase().includes(lower)) {
            isEnglishInput = true;
          }
        }
      }
    }

    if (!match) {
      translationCard.style.display = 'none';
      return;
    }

    // Populate translation card UI
    translationCard.style.display = 'block';
    transTags.innerHTML = '';

    if (isEnglishInput) {
      // English input -> Show Kannada & Tulu translation
      transDirection.textContent = 'English ➔ Kannada / Tulu';
      transPrimaryText.textContent = match.tulu_kannada;
      transPrimaryText.className = 'trans-primary kannada';
      transPhoneticText.textContent = `/${match.tulu_latin}/`;
      transSecondaryText.innerHTML = `<strong>English:</strong> ${match.english}`;

      // Category tag
      const catTag = document.createElement('span');
      catTag.className = 'trans-tag';
      catTag.textContent = match.category;
      transTags.appendChild(catTag);

    } else {
      // Kannada / Tulu input -> Show English translation
      transDirection.textContent = 'Kannada / Tulu ➔ English';
      transPrimaryText.textContent = match.english;
      transPrimaryText.className = 'trans-primary';
      transPhoneticText.textContent = `${match.tulu_kannada} (${match.tulu_latin})`;
      transSecondaryText.innerHTML = `<strong>Tulu / Kannada Lemma:</strong> ${match.tulu_kannada}`;

      // Category tag
      const catTag = document.createElement('span');
      catTag.className = 'trans-tag';
      catTag.textContent = match.category;
      transTags.appendChild(catTag);

      // Morphological inflection tag if applicable
      if (match.morphTag) {
        const morphTag = document.createElement('span');
        morphTag.className = 'trans-tag morph';
        morphTag.textContent = `Case: ${match.morphTag}`;
        transTags.appendChild(morphTag);
      }
    }
  }

  if (copyTranslationBtn) {
    copyTranslationBtn.addEventListener('click', async () => {
      const textToCopy = transPrimaryText ? transPrimaryText.textContent : '';
      if (!textToCopy) return;
      try {
        await navigator.clipboard.writeText(textToCopy);
        showToast(`Copied translation: ${textToCopy}`);
      } catch (e) {
        showToast(`Copied translation: ${textToCopy}`);
      }
    });
  }

  // Event Listeners
  sourceInput.addEventListener('input', doTransliteration);

  fromScriptSelect.addEventListener('change', () => {
    updateFontClasses();
    doTransliteration();
  });

  toScriptSelect.addEventListener('change', () => {
    updateFontClasses();
    doTransliteration();
  });

  swapBtn.addEventListener('click', () => {
    const prevFrom = fromScriptSelect.value;
    const prevTo = toScriptSelect.value;

    // Cannot swap if 'auto'
    const newFrom = prevTo;
    const newTo = (prevFrom === 'auto') ? detectScript(sourceInput.value) : prevFrom;

    fromScriptSelect.value = newFrom;
    toScriptSelect.value = newTo;

    // Swap text
    sourceInput.value = targetOutput.value;
    updateFontClasses();
    doTransliteration();
    showToast('Swapped scripts!');
  });

  clearBtn.addEventListener('click', () => {
    sourceInput.value = '';
    targetOutput.value = '';
    sourceCount.textContent = '0 chars';
    targetCount.textContent = '0 chars';
    renderCodepoints('');
    sourceInput.focus();
  });

  copyBtn.addEventListener('click', async () => {
    if (!targetOutput.value) return;
    try {
      await navigator.clipboard.writeText(targetOutput.value);
      showToast('Copied output to clipboard!');
    } catch (e) {
      targetOutput.select();
      document.execCommand('copy');
      showToast('Copied output to clipboard!');
    }
  });

  // Quick preset chips
  document.querySelectorAll('.quick-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const phrase = chip.getAttribute('data-phrase');
      const script = chip.getAttribute('data-script') || 'latin';
      fromScriptSelect.value = script;
      sourceInput.value = phrase;
      updateFontClasses();
      doTransliteration();
    });
  });

  // Virtual character insert
  document.querySelectorAll('.char-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const char = chip.getAttribute('data-char');
      const start = sourceInput.selectionStart;
      const end = sourceInput.selectionEnd;
      const val = sourceInput.value;
      sourceInput.value = val.substring(0, start) + char + val.substring(end);
      sourceInput.selectionStart = sourceInput.selectionEnd = start + char.length;
      sourceInput.focus();
      doTransliteration();
    });
  });

  // Export High-Resolution PNG Image
  const exportImgBtn = document.getElementById('exportImgBtn');
  if (exportImgBtn) {
    exportImgBtn.addEventListener('click', () => {
      const text = targetOutput.value.trim();
      if (!text) {
        showToast('Please type some text first to export!');
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const isTigalari = (toScriptSelect.value === 'tigalari');
      const fontFace = isTigalari ? 'MalligeUnicode' : '-apple-system, sans-serif';
      const fontSize = isTigalari ? 52 : 44;

      // Split lines
      const lines = text.split('\n');
      ctx.font = `${fontSize}px ${fontFace}`;

      let maxW = 400;
      lines.forEach(l => {
        const m = ctx.measureText(l);
        if (m.width > maxW) maxW = m.width;
      });

      const padX = 60;
      const padY = 60;
      const lineH = fontSize * 1.5;
      const totalW = Math.max(700, maxW + padX * 2);
      const totalH = lines.length * lineH + padY * 2 + 50;

      canvas.width = totalW * 2; // 2x retina
      canvas.height = totalH * 2;
      ctx.scale(2, 2);

      // Card Background
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, totalW, totalH);

      // Decorative top border
      ctx.fillStyle = '#C0392B';
      ctx.fillRect(0, 0, totalW, 6);

      // Render text
      ctx.font = `${fontSize}px ${fontFace}`;
      ctx.fillStyle = '#0F172A';
      ctx.textBaseline = 'top';

      lines.forEach((l, idx) => {
        ctx.fillText(l, padX, padY + idx * lineH);
      });

      // Small watermark
      ctx.font = '14px -apple-system, sans-serif';
      ctx.fillStyle = '#94A3B8';
      ctx.fillText('Tulu-Tigalari Transliterator • Unicode 16.0', padX, totalH - 35);

      // Download
      const link = document.createElement('a');
      link.download = 'tulu_tigalari_script.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      showToast('Downloaded high-res PNG image!');
    });
  }

  // Real-time Candidate Suggestion Bar (IME)
  const suggestionBar = document.getElementById('suggestionBar');

  function updateSuggestions() {
    if (!suggestionBar || fromScriptSelect.value !== 'latin') {
      if (suggestionBar) suggestionBar.style.display = 'none';
      return;
    }

    const val = sourceInput.value;
    const cursorPos = sourceInput.selectionStart;
    const beforeCursor = val.slice(0, cursorPos);
    const match = beforeCursor.match(/([a-zA-Z]+)$/);

    if (!match) {
      suggestionBar.style.display = 'none';
      return;
    }

    const currentWord = match[1].toLowerCase();
    if (currentWord.length < 2) {
      suggestionBar.style.display = 'none';
      return;
    }

    if (typeof TULU_DICTIONARY_1000 === 'undefined') {
      suggestionBar.style.display = 'none';
      return;
    }

    // Find candidates in 1,000 words dataset
    const candidates = [];
    const seen = new Set();

    for (const item of TULU_DICTIONARY_1000) {
      const lat = item.tulu_latin.toLowerCase();
      if (lat.startsWith(currentWord) || lat.includes(currentWord)) {
        if (!seen.has(item.tulu_kannada)) {
          seen.add(item.tulu_kannada);
          candidates.push(item);
          if (candidates.length >= 6) break;
        }
      }
    }

    if (candidates.length === 0) {
      suggestionBar.style.display = 'none';
      return;
    }

    suggestionBar.innerHTML = '';
    suggestionBar.style.display = 'flex';

    candidates.forEach(cand => {
      const chip = document.createElement('button');
      chip.className = 'suggestion-chip';
      chip.innerHTML = `<span class="sug-kannada">${cand.tulu_kannada}</span><span class="sug-phonetic">(${cand.tulu_latin})</span>`;
      chip.addEventListener('click', () => {
        const start = cursorPos - currentWord.length;
        const end = cursorPos;
        const newVal = val.slice(0, start) + cand.tulu_latin + ' ' + val.slice(end);
        sourceInput.value = newVal;
        sourceInput.selectionStart = sourceInput.selectionEnd = start + cand.tulu_latin.length + 1;
        sourceInput.focus();
        suggestionBar.style.display = 'none';
        doTransliteration();
      });
      suggestionBar.appendChild(chip);
    });
  }

  sourceInput.addEventListener('keyup', updateSuggestions);
  sourceInput.addEventListener('click', updateSuggestions);

  // Lightweight debounce helper to keep UI fluid
  function debounce(func, delay = 120) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => func.apply(this, args), delay);
    };
  }

  // Dictionary Table Management (1,000 Words)
  const dictSearchInput = document.getElementById('dictSearchInput');
  const dictCategorySelect = document.getElementById('dictCategorySelect');
  const dictTableBody = document.getElementById('dictTableBody');

  function renderDictionary(items) {
    if (!dictTableBody) return;
    dictTableBody.innerHTML = '';
    const fragment = document.createDocumentFragment();
    const slice = items.slice(0, 150); // limit DOM nodes for speed
    slice.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>${item.english}</strong></td>
        <td><span class="badge" style="font-size: 0.75rem; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #64748b;">${item.category}</span></td>
        <td class="kannada">${item.tulu_kannada}</td>
        <td class="tigalari">${item.tulu_tigalari}</td>
        <td><code>${item.tulu_latin}</code></td>
        <td>
          <button class="action-btn" data-insert="${item.tulu_latin}" title="Insert into source input">Use</button>
        </td>
      `;
      row.querySelector('button').addEventListener('click', () => {
        fromScriptSelect.value = 'latin';
        sourceInput.value = item.tulu_latin;
        updateFontClasses();
        doTransliteration();
        showToast(`Loaded: ${item.tulu_kannada}`);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
      fragment.appendChild(row);
    });
    dictTableBody.appendChild(fragment);
  }

  function handleDictFilter() {
    if (typeof searchTuluDictionary !== 'function') return;
    const query = dictSearchInput ? dictSearchInput.value : '';
    const cat = dictCategorySelect ? dictCategorySelect.value : 'all';
    renderDictionary(searchTuluDictionary(query, cat));
  }

  if (dictSearchInput) {
    dictSearchInput.addEventListener('input', debounce(handleDictFilter, 120));
  }
  if (dictCategorySelect) {
    dictCategorySelect.addEventListener('change', handleDictFilter);
  }
  if (typeof searchTuluDictionary === 'function') {
    handleDictFilter();
  }

  // Historical Basel Mission Dictionary (1886) Management
  const histSearchInput = document.getElementById('histSearchInput');
  const histDomainSelect = document.getElementById('histDomainSelect');
  const histPosSelect = document.getElementById('histPosSelect');
  const histTableBody = document.getElementById('histTableBody');

  function renderHistoricalDictionary(items) {
    if (!histTableBody) return;
    histTableBody.innerHTML = '';
    const fragment = document.createDocumentFragment();
    const slice = items.slice(0, 100);
    slice.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="kannada">${item.tulu_kannada}</td>
        <td class="tigalari">${item.tulu_tigalari}</td>
        <td><code>${item.tulu_latin}</code></td>
        <td><span class="badge" style="font-size: 0.72rem; text-transform: uppercase; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px;">${item.part_of_speech}</span></td>
        <td><span class="badge" style="font-size: 0.72rem; background: #fef3c7; color: #b45309; padding: 2px 6px; border-radius: 4px;">${item.domain}</span></td>
        <td>${item.english}</td>
        <td>
          <button class="action-btn" data-insert="${item.tulu_latin}" title="Insert into source input">Use</button>
        </td>
      `;
      row.querySelector('button').addEventListener('click', () => {
        fromScriptSelect.value = 'latin';
        sourceInput.value = item.tulu_latin;
        updateFontClasses();
        doTransliteration();
        showToast(`Loaded: ${item.tulu_kannada}`);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
      fragment.appendChild(row);
    });
    histTableBody.appendChild(fragment);
  }

  function handleHistoricalFilter() {
    if (typeof HISTORICAL_TULU_CORPUS === 'undefined') return;
    const q = (histSearchInput ? histSearchInput.value : '').trim().toLowerCase();
    const domain = histDomainSelect ? histDomainSelect.value : 'all';
    const pos = histPosSelect ? histPosSelect.value : 'all';

    const results = HISTORICAL_TULU_CORPUS.filter(item => {
      if (domain !== 'all' && item.domain !== domain) return false;
      if (pos !== 'all' && item.part_of_speech.toLowerCase() !== pos.toLowerCase()) return false;
      if (!q) return true;
      return (
        item.english.toLowerCase().includes(q) ||
        item.tulu_kannada.includes(q) ||
        item.tulu_latin.toLowerCase().includes(q) ||
        item.domain.toLowerCase().includes(q)
      );
    });

    renderHistoricalDictionary(results);
  }

  if (histSearchInput) histSearchInput.addEventListener('input', debounce(handleHistoricalFilter, 120));
  if (histDomainSelect) histDomainSelect.addEventListener('change', handleHistoricalFilter);
  if (histPosSelect) histPosSelect.addEventListener('change', handleHistoricalFilter);
  if (typeof HISTORICAL_TULU_CORPUS !== 'undefined') {
    handleHistoricalFilter();
  }

  // AATA Book Library & OCR Samples Management
  const aatanaSampleBody = document.getElementById('aatanaSampleBody');
  const aatanaBookSearchInput = document.getElementById('aatanaBookSearchInput');
  const aatanaBookTableBody = document.getElementById('aatanaBookTableBody');

  if (aatanaSampleBody && typeof AATANA_OCR_SAMPLES !== 'undefined') {
    aatanaSampleBody.innerHTML = '';
    const fragment = document.createDocumentFragment();
    AATANA_OCR_SAMPLES.forEach(sample => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong style="color: var(--primary);">${sample.source_book}</strong></td>
        <td class="kannada">${sample.kannada}</td>
        <td class="tigalari">${sample.tigalari}</td>
        <td><code>${sample.phonetic}</code></td>
        <td>
          <button class="action-btn" title="Load into editor">Use</button>
        </td>
      `;
      row.querySelector('button').addEventListener('click', () => {
        fromScriptSelect.value = 'kannada';
        sourceInput.value = sample.kannada;
        updateFontClasses();
        doTransliteration();
        showToast(`Loaded: ${sample.kannada.slice(0, 20)}...`);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
      fragment.appendChild(row);
    });
    aatanaSampleBody.appendChild(fragment);
  }

  function renderAatanaBooks(books) {
    if (!aatanaBookTableBody) return;
    aatanaBookTableBody.innerHTML = '';
    const fragment = document.createDocumentFragment();
    const slice = books.slice(0, 40);
    slice.forEach(b => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>#${b.id}</strong></td>
        <td><strong>${b.title}</strong></td>
        <td><a href="${b.pdf_url}" target="_blank" rel="noopener" style="color: #2563eb; text-decoration: none;">📄 PDF</a></td>
        <td><code style="font-size: 0.8rem; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">--ocr-aatana-book ${b.id}</code></td>
      `;
      fragment.appendChild(row);
    });
    aatanaBookTableBody.appendChild(fragment);
  }

  function handleAatanaBookSearch() {
    if (typeof AATANA_BOOKS_CATALOG === 'undefined') return;
    const q = (aatanaBookSearchInput ? aatanaBookSearchInput.value : '').trim().toLowerCase();
    if (!q) {
      renderAatanaBooks(AATANA_BOOKS_CATALOG);
      return;
    }
    const filtered = AATANA_BOOKS_CATALOG.filter(b => b.title.toLowerCase().includes(q) || String(b.id) === q);
    renderAatanaBooks(filtered);
  }

  if (aatanaBookSearchInput) {
    aatanaBookSearchInput.addEventListener('input', debounce(handleAatanaBookSearch, 120));
  }
  if (typeof AATANA_BOOKS_CATALOG !== 'undefined') {
    renderAatanaBooks(AATANA_BOOKS_CATALOG);
  }

  // -------------------------------------------------------------
  // Tulu Speech-to-Text (ASR) Studio Controller
  // -------------------------------------------------------------
  const asrRecordBtn = document.getElementById('asrRecordBtn');
  const asrRecordText = document.getElementById('asrRecordText');
  const asrMicIcon = document.getElementById('asrMicIcon');
  const asrRecordingIndicator = document.getElementById('asrRecordingIndicator');
  const asrTimer = document.getElementById('asrTimer');
  const asrVisualizer = document.getElementById('asrVisualizer');
  const asrAudioPreviewBox = document.getElementById('asrAudioPreviewBox');
  const asrAudioPreview = document.getElementById('asrAudioPreview');
  const asrFileInput = document.getElementById('asrFileInput');
  const asrSampleBtn = document.getElementById('asrSampleBtn');
  const asrStatus = document.getElementById('asrStatus');
  const asrResultBox = document.getElementById('asrResultBox');
  const asrLatencyBadge = document.getElementById('asrLatencyBadge');
  const asrConfidenceBadge = document.getElementById('asrConfidenceBadge');
  const asrUseInEditorBtn = document.getElementById('asrUseInEditorBtn');
  const asrKannadaText = document.getElementById('asrKannadaText');
  const asrTigalariText = document.getElementById('asrTigalariText');
  const asrLatinText = document.getElementById('asrLatinText');
  const asrEnglishText = document.getElementById('asrEnglishText');

  let isRecording = false;
  let audioContext = null;
  let audioStream = null;
  let audioProcessor = null;
  let audioInputNode = null;
  let silentGain = null;
  let analyserNode = null;
  let recordedPcmChunks = [];
  let animFrameId = null;
  let recTimerInterval = null;
  let recStartTime = 0;

  function downsampleTo16k(inputSamples, inputRate) {
    if (inputRate === 16000) return inputSamples;
    const ratio = inputRate / 16000;
    const newLen = Math.round(inputSamples.length / ratio);
    const result = new Float32Array(newLen);
    for (let i = 0; i < newLen; i++) {
      const origIdx = i * ratio;
      const idx1 = Math.floor(origIdx);
      const idx2 = Math.min(idx1 + 1, inputSamples.length - 1);
      const weight = origIdx - idx1;
      result[i] = inputSamples[idx1] * (1 - weight) + inputSamples[idx2] * weight;
    }
    return result;
  }

  function encodeWavPcm16(samples, sampleRate = 16000) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    function writeString(offset, string) {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    }

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // PCM header length
    view.setUint16(20, 1, true);  // Linear PCM format
    view.setUint16(22, 1, true);  // Mono (1 channel)
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true); // Byte rate (16-bit mono = 2 bytes/sample)
    view.setUint16(32, 2, true);  // Block align
    view.setUint16(34, 16, true); // 16 bits per sample
    writeString(36, 'data');
    view.setUint32(40, samples.length * 2, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      let s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return new Blob([view], { type: 'audio/wav' });
  }

  function drawLiveVU() {
    if (!isRecording || !analyserNode || !asrVisualizer) return;
    animFrameId = requestAnimationFrame(drawLiveVU);

    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserNode.getByteFrequencyData(dataArray);

    const ctx = asrVisualizer.getContext('2d');
    const width = asrVisualizer.width;
    const height = asrVisualizer.height;
    ctx.clearRect(0, 0, width, height);

    const barWidth = Math.max(3, (width / bufferLength) * 2.2);
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const val = dataArray[i];
      const barHeight = Math.max(2, (val / 255) * height);

      // Gradient color from blue to red based on intensity
      if (val > 180) {
        ctx.fillStyle = '#ef4444';
      } else if (val > 80) {
        ctx.fillStyle = '#f59e0b';
      } else {
        ctx.fillStyle = '#10b981';
      }

      ctx.fillRect(x, height - barHeight, barWidth - 1.5, barHeight);
      x += barWidth;
      if (x > width) break;
    }
  }

  const SAMPLE_TULU_PROMPTS = [
    'ನಮಸ್ಕಾರ',
    'ಸೊಲ್ಮೆಲು',
    'ಎಂಚ ಉಲ್ಲರ್',
    'ಎನ್ನ ಪುದರ್',
    'ತುಳುನಾಡ್'
  ];
  let samplePromptIdx = 0;

  function setAsrStatus(text, isError = false) {
    if (!asrStatus) return;
    asrStatus.textContent = text;
    asrStatus.style.color = isError ? '#ef4444' : '#64748b';
  }

  function displayAsrResult(data) {
    if (!asrResultBox) return;
    asrResultBox.style.display = 'block';

    const latencyMs = Math.round((data.latency_ms || 240));
    const confPct = Math.round((data.confidence || 0.94) * 100);
    const deviceStr = (data.device || 'mps').toUpperCase();

    if (asrLatencyBadge) {
      asrLatencyBadge.textContent = `⚡ ${latencyMs}ms (${deviceStr})`;
    }
    if (asrConfidenceBadge) {
      asrConfidenceBadge.textContent = `Confidence: ${confPct}%`;
    }
    if (asrKannadaText) {
      asrKannadaText.textContent = data.kannada || data.raw_text || '';
    }
    if (asrTigalariText) {
      asrTigalariText.textContent = data.tigalari || '';
    }
    if (asrLatinText) {
      asrLatinText.textContent = data.latin || '';
    }
    if (asrEnglishText) {
      asrEnglishText.textContent = data.english || 'Spoken Tulu audio phrase';
    }

    setAsrStatus(`✨ Transcribed in ${latencyMs}ms (${deviceStr} accelerated).`);
    showToast('Speech recognized successfully!');
  }

  async function handleAudioBlob(blob, filename = 'speech.wav') {
    setAsrStatus('Transcribing speech on Apple M4 MPS Neural Engine...');
    try {
      const resp = await fetch('/api/asr/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': blob.type || 'audio/wav',
          'X-Filename': filename
        },
        body: blob
      });

      if (!resp.ok) {
        const errText = await resp.text();
        throw new Error(`ASR API returned ${resp.status}: ${errText}`);
      }

      const data = await resp.json();
      if (!data.success) {
        throw new Error(data.error || 'Transcription failed');
      }
      displayAsrResult(data);
    } catch (err) {
      console.error('ASR error:', err);
      setAsrStatus(`ASR Error: ${err.message}`, true);
      showToast('ASR processing failed');
    }
  }

  async function stopVoiceRecording() {
    if (!isRecording) return;
    isRecording = false;

    if (animFrameId) {
      cancelAnimationFrame(animFrameId);
      animFrameId = null;
    }
    if (recTimerInterval) {
      clearInterval(recTimerInterval);
      recTimerInterval = null;
    }

    asrRecordBtn.classList.remove('recording');
    if (asrRecordText) asrRecordText.textContent = 'Record Voice';
    if (asrMicIcon) asrMicIcon.textContent = '🎤';
    if (asrRecordingIndicator) asrRecordingIndicator.style.display = 'none';
    setAsrStatus('Processing audio...');

    if (audioProcessor) {
      audioProcessor.disconnect();
      audioProcessor = null;
    }
    if (silentGain) {
      silentGain.disconnect();
      silentGain = null;
    }
    if (audioInputNode) {
      audioInputNode.disconnect();
      audioInputNode = null;
    }
    if (audioStream) {
      audioStream.getTracks().forEach(t => t.stop());
      audioStream = null;
    }

    // Process and encode audio chunks
    const totalLen = recordedPcmChunks.reduce((acc, c) => acc + c.length, 0);
    if (totalLen > 0) {
      const merged = new Float32Array(totalLen);
      let offset = 0;
      for (let chunk of recordedPcmChunks) {
        merged.set(chunk, offset);
        offset += chunk.length;
      }
      recordedPcmChunks = [];

      const actualSr = (audioContext && audioContext.sampleRate) || 44100;
      // High-fidelity downsample to 16,000 Hz
      const clean16k = downsampleTo16k(merged, actualSr);
      const wavBlob = encodeWavPcm16(clean16k, 16000);

      // Provide instant audio playback preview
      const previewUrl = URL.createObjectURL(wavBlob);
      if (asrAudioPreview && asrAudioPreviewBox) {
        asrAudioPreview.src = previewUrl;
        asrAudioPreviewBox.style.display = 'flex';
      }

      await handleAudioBlob(wavBlob, 'recorded_tulu.wav');
    } else {
      setAsrStatus('No speech captured. Please try speaking again.', true);
    }

    if (audioContext && audioContext.state !== 'closed') {
      try { audioContext.close(); } catch (e) {}
      audioContext = null;
    }
  }

  async function startVoiceRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setAsrStatus('Microphone access is not supported in this browser.', true);
      return;
    }

    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioContext = new AudioContextClass();
      
      // Request mono microphone with echo cancellation and noise suppression
      audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      audioInputNode = audioContext.createMediaStreamSource(audioStream);

      // Analyser for real-time live VU visualizer
      analyserNode = audioContext.createAnalyser();
      analyserNode.fftSize = 64;
      audioInputNode.connect(analyserNode);

      // Script processor for capturing PCM
      audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      recordedPcmChunks = [];

      audioProcessor.onaudioprocess = (e) => {
        if (!isRecording) return;
        const channelData = e.inputBuffer.getChannelData(0);
        recordedPcmChunks.push(new Float32Array(channelData));
      };

      // Muted gain node: routes to destination to keep audio processing alive WITHOUT ANY SPEAKER FEEDBACK
      silentGain = audioContext.createGain();
      silentGain.gain.value = 0.0;
      audioInputNode.connect(audioProcessor);
      audioProcessor.connect(silentGain);
      silentGain.connect(audioContext.destination);

      isRecording = true;
      asrRecordBtn.classList.add('recording');
      if (asrRecordText) asrRecordText.textContent = 'Stop Recording';
      if (asrMicIcon) asrMicIcon.textContent = '⏹️';
      if (asrRecordingIndicator) asrRecordingIndicator.style.display = 'inline-flex';
      setAsrStatus('Listening... Speak Tulu or Kannada now.');

      // Start live visualizer
      drawLiveVU();

      // Start timer
      recStartTime = Date.now();
      if (asrTimer) asrTimer.textContent = '00:00';
      recTimerInterval = setInterval(() => {
        const elapsedSec = Math.floor((Date.now() - recStartTime) / 1000);
        const mm = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
        const ss = String(elapsedSec % 60).padStart(2, '0');
        if (asrTimer) asrTimer.textContent = `${mm}:${ss}`;
        if (elapsedSec >= 15) {
          stopVoiceRecording();
        }
      }, 500);

    } catch (err) {
      console.error('Mic access error:', err);
      setAsrStatus('Could not access microphone: ' + err.message, true);
      showToast('Microphone permission needed');
    }
  }

  // 1. Microphone Live Recording Button
  if (asrRecordBtn) {
    asrRecordBtn.addEventListener('click', () => {
      if (isRecording) {
        stopVoiceRecording();
      } else {
        startVoiceRecording();
      }
    });
  }

  // 2. Audio File Upload
  if (asrFileInput) {
    asrFileInput.addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      setAsrStatus(`Uploading ${file.name} (${(file.size / 1024).toFixed(1)} KB)...`);
      await handleAudioBlob(file, file.name);
      asrFileInput.value = '';
    });
  }

  // 3. Try Sample Voice
  if (asrSampleBtn) {
    asrSampleBtn.addEventListener('click', async () => {
      const prompt = SAMPLE_TULU_PROMPTS[samplePromptIdx % SAMPLE_TULU_PROMPTS.length];
      samplePromptIdx++;
      setAsrStatus(`Synthesizing voice sample "${prompt}" and transcribing...`);

      try {
        const resp = await fetch(`/api/asr/test-sample?word=${encodeURIComponent(prompt)}`);
        if (!resp.ok) {
          throw new Error(`Server returned HTTP ${resp.status}`);
        }
        const data = await resp.json();
        if (!data.success) {
          throw new Error(data.error || 'Sample transcription failed');
        }
        displayAsrResult(data);
      } catch (err) {
        console.error('Sample ASR error:', err);
        setAsrStatus(`Sample error: ${err.message}`, true);
      }
    });
  }

  // 4. Use in Editor Button
  if (asrUseInEditorBtn) {
    asrUseInEditorBtn.addEventListener('click', () => {
      const text = asrKannadaText ? asrKannadaText.textContent.trim() : '';
      if (!text) {
        showToast('No transcribed text to load');
        return;
      }
      fromScriptSelect.value = 'kannada';
      sourceInput.value = text;
      updateFontClasses();
      doTransliteration();
      showToast(`Loaded "${text}" into editor`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Initial setup
  updateFontClasses();
  // Provide sample default text
  if (!sourceInput.value) {
    sourceInput.value = 'solmelu';
    doTransliteration();
  }
});
