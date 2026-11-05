/**
 * Tulu & Kannada Web Transliterator Engine
 * Unicode 16.0 Standard (Tulu-Tigalari block: U+11380 - U+113FF)
 * Supports English/Latin Phonetic, Kannada, and Tulu-Tigalari
 */

const KANNADA_CONSONANTS = new Set([
  'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ',
  'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ',
  'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ',
  'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ',
  'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ',
  'ಯ', 'ರ', 'ಱ', 'ಲ', 'ವ',
  'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ', 'ೞ'
]);

const KANNADA_TO_TIGALARI = {
  // Independent Vowels
  'ಅ': '\u{11380}',
  'ಆ': '\u{11381}',
  'ಇ': '\u{11382}',
  'ಈ': '\u{11383}',
  'ಉ': '\u{11384}',
  'ಊ': '\u{11385}',
  'ಋ': '\u{11386}',
  'ೠ': '\u{11387}',
  'ಌ': '\u{11388}',
  'ೡ': '\u{11389}',
  'ಎ': '\u{1138A}',
  'ಏ': '\u{1138B}',
  'ಐ': '\u{1138E}',
  'ಒ': '\u{1138F}',
  'ಓ': '\u{11390}',
  'ಔ': '\u{11391}',

  // Consonants
  'ಕ': '\u{11392}',
  'ಖ': '\u{11393}',
  'ಗ': '\u{11394}',
  'ಘ': '\u{11395}',
  'ಙ': '\u{11396}',
  'ಚ': '\u{11397}',
  'ಛ': '\u{11398}',
  'ಜ': '\u{11399}',
  'ಝ': '\u{1139A}',
  'ಞ': '\u{1139B}',
  'ಟ': '\u{1139C}',
  'ಠ': '\u{1139D}',
  'ಡ': '\u{1139E}',
  'ಢ': '\u{1139F}',
  'ಣ': '\u{113A0}',
  'ತ': '\u{113A1}',
  'ಥ': '\u{113A2}',
  'ದ': '\u{113A3}',
  'ಧ': '\u{113A4}',
  'ನ': '\u{113A5}',
  'ಪ': '\u{113A6}',
  'ಫ': '\u{113A7}',
  'ಬ': '\u{113A8}',
  'ಭ': '\u{113A9}',
  'ಮ': '\u{113AA}',
  'ಯ': '\u{113AB}',
  'ರ': '\u{113AC}',
  'ಱ': '\u{113B4}',
  'ಲ': '\u{113AD}',
  'ಳ': '\u{113B3}',
  'ವ': '\u{113AE}',
  'ಶ': '\u{113AF}',
  'ಷ': '\u{113B0}',
  'ಸ': '\u{113B1}',
  'ಹ': '\u{113B2}',
  'ೞ': '\u{113B5}',

  // Vowel Signs / Matras
  'ಾ': '\u{113B8}',
  'ಿ': '\u{113B9}',
  'ೀ': '\u{113BA}',
  'ು': '\u{113BB}',
  'ೂ': '\u{113BC}',
  'ೃ': '\u{113BD}',
  'ೄ': '\u{113BE}',
  'ೢ': '\u{113BF}',
  'ೣ': '\u{113C0}',
  'ೆ': '\u{113C1}',
  'ೇ': '\u{113C2}',
  'ೈ': '\u{113C5}',
  'ೊ': '\u{113C6}',
  'ೋ': '\u{113C7}',
  'ೌ': '\u{113C8}',

  // Yogavahakagalu & Punctuation
  'ಂ': '\u{113CC}',
  'ಃ': '\u{113CD}',
  'ಁ': '\u{113CA}',
  'ಽ': '\u{113B7}',
  '।': '\u{113D4}',
  '॥': '\u{113D5}',
};

// Build reverse Tigalari to Kannada mapping
const TIGALARI_TO_KANNADA = {};
for (const [k, v] of Object.entries(KANNADA_TO_TIGALARI)) {
  TIGALARI_TO_KANNADA[v] = k;
}
TIGALARI_TO_KANNADA['\u{113CE}'] = '್'; // VIRAMA
TIGALARI_TO_KANNADA['\u{113D0}'] = '್'; // CONJOINER
TIGALARI_TO_KANNADA['\u{113CF}'] = '್'; // LOOPED VIRAMA

// Vowel mappings for Latin -> Kannada
const VOWEL_MAPPINGS = [
  ['aae', 'ಾೆ್', 'ಆೆ್'],
  ['ae', 'ೆ್', 'ಎ್'],
  ['aa', 'ಾ', 'ಆ'],
  ['AA', 'ಾ', 'ಆ'],
  ['ii', 'ೀ', 'ಈ'],
  ['II', 'ೀ', 'ಈ'],
  ['ee', 'ೀ', 'ಈ'],
  ['EE', 'ೀ', 'ಈ'],
  ['uu', 'ೂ', 'ಊ'],
  ['UU', 'ೂ', 'ಊ'],
  ['oo', 'ೂ', 'ಊ'],
  ['OO', 'ೂ', 'ಊ'],
  ['ai', 'ೈ', 'ಐ'],
  ['AI', 'ೈ', 'ಐ'],
  ['au', 'ೌ', 'ಔ'],
  ['AU', 'ೌ', 'ಔ'],
  ['ou', 'ೌ', 'ಔ'],
  ['OU', 'ೌ', 'ಔ'],
  ['Ru', 'ೃ', 'ಋ'],
  ['RU', 'ೄ', 'ೠ'],
  ['A', 'ಾ', 'ಆ'],
  ['I', 'ೀ', 'ಈ'],
  ['U', 'ೂ', 'ಊ'],
  ['E', 'ೇ', 'ಏ'],
  ['O', 'ೋ', 'ಓ'],
  ['a', '', 'ಅ'],
  ['i', 'ಿ', 'ಇ'],
  ['u', 'ು', 'ಉ'],
  ['e', 'ೆ', 'ಎ'],
  ['o', 'ೊ', 'ಒ'],
];

// Consonant mappings for Latin -> Kannada
const CONSONANT_MAPPINGS = [
  ['kSh', 'ಕ್ಷ', true],
  ['ksh', 'ಕ್ಷ', true],
  ['Ksh', 'ಕ್ಷ', true],
  ['Jn', 'ಜ್ಞ', true],
  ['jn', 'ಜ್ಞ', true],
  ['dny', 'ಜ್ಞ', true],
  ['shh', 'ಷ್', true],
  ['chh', 'ಛ', true],
  ['Chh', 'ಛ', true],
  ['kh', 'ಖ', true],
  ['Kh', 'ಖ', true],
  ['gh', 'ಘ', true],
  ['Gh', 'ಘ', true],
  ['ng', 'ಙ', true],
  ['NG', 'ಙ', true],
  ['~g', 'ಙ', true],
  ['ch', 'ಚ', true],
  ['Ch', 'ಛ', true],
  ['jh', 'ಝ', true],
  ['Jh', 'ಝ', true],
  ['nj', 'ಞ', true],
  ['NJ', 'ಞ', true],
  ['~j', 'ಞ', true],
  ['Th', 'ಠ', true],
  ['TH', 'ಠ', true],
  ['th', 'ಥ', true],
  ['Dh', 'ಢ', true],
  ['DH', 'ಢ', true],
  ['dh', 'ಧ', true],
  ['ph', 'ಫ', true],
  ['Ph', 'ಫ', true],
  ['bh', 'ಭ', true],
  ['Bh', 'ಭ', true],
  ['sh', 'ಶ', true],
  ['Sh', 'ಷ', true],
  ['SH', 'ಷ', true],
  ['zh', 'ೞ', true],
  ['ZH', 'ೞ', true],
  ['rr', 'ಱ', true],
  ['RR', 'ಱ', true],
  ['k', 'ಕ', true],
  ['K', 'ಕ', true],
  ['g', 'ಗ', true],
  ['G', 'ಗ', true],
  ['c', 'ಚ', true],
  ['C', 'ಚ', true],
  ['j', 'ಜ', true],
  ['J', 'ಜ', true],
  ['T', 'ಟ', true],
  ['t', 'ತ', true],
  ['D', 'ಡ', true],
  ['d', 'ದ', true],
  ['N', 'ಣ', true],
  ['n', 'ನ', true],
  ['p', 'ಪ', true],
  ['P', 'ಪ', true],
  ['f', 'ಫ', true],
  ['F', 'ಫ', true],
  ['b', 'ಬ', true],
  ['B', 'ಬ', true],
  ['m', 'ಮ', true],
  ['M', 'ಂ', false],
  ['y', 'ಯ', true],
  ['Y', 'ಯ', true],
  ['r', 'ರ', true],
  ['R', 'ಱ', true],
  ['l', 'ಲ', true],
  ['L', 'ಳ', true],
  ['v', 'ವ', true],
  ['V', 'ವ', true],
  ['w', 'ವ', true],
  ['W', 'ವ', true],
  ['s', 'ಸ', true],
  ['S', 'ಶ', true],
  ['h', 'ಹ', true],
  ['H', 'ಃ', false],
];

function matchPrefix(text, idx, mapping) {
  for (const entry of mapping) {
    const pat = entry[0];
    if (text.startsWith(pat, idx)) {
      return [pat, entry.slice(1)];
    }
  }
  return [null, null];
}

function latinToKannada(text) {
  const res = [];
  let i = 0;
  const n = text.length;
  const VIRAMA = '್';

  while (i < n) {
    const [patC, valC] = matchPrefix(text, i, CONSONANT_MAPPINGS);
    if (patC) {
      const [sym, needsVowel] = valC;
      i += patC.length;
      if (!needsVowel) {
        res.push(sym);
        continue;
      }

      const [patV, valV] = matchPrefix(text, i, VOWEL_MAPPINGS);
      if (patV) {
        const [matra] = valV;
        res.push(sym + matra);
        i += patV.length;
      } else {
        res.push(sym + VIRAMA);
      }
      continue;
    }

    const [patV, valV] = matchPrefix(text, i, VOWEL_MAPPINGS);
    if (patV) {
      const [, indep] = valV;
      res.push(indep);
      i += patV.length;
      continue;
    }

    if (text[i] === '~' || text[i] === "'") {
      res.push(VIRAMA);
      i++;
      continue;
    }

    res.push(text[i]);
    i++;
  }

  return res.join('');
}

const KANNADA_TO_LATIN_VOWELS = {
  'ಅ': 'a', 'ಆ': 'aa', 'ಇ': 'i', 'ಈ': 'ee', 'ಉ': 'u', 'ಊ': 'oo',
  'ಋ': 'Ru', 'ೠ': 'RU', 'ಌ': 'li', 'ೡ': 'lI',
  'ಎ': 'e', 'ಏ': 'E', 'ಎ್': 'ae', 'ಐ': 'ai', 'ಒ': 'o', 'ಓ': 'O', 'ಔ': 'au'
};

const KANNADA_TO_LATIN_MATRAS = {
  'ಾ': 'aa', 'ಿ': 'i', 'ೀ': 'ee', 'ು': 'u', 'ೂ': 'oo',
  'ೃ': 'Ru', 'ೄ': 'RU', 'ೆ': 'e', 'ೇ': 'E', 'ೈ': 'ai',
  'ೊ': 'o', 'ೋ': 'O', 'ೌ': 'au'
};

const KANNADA_TO_LATIN_CONSONANTS = {
  'ಕ': 'k', 'ಖ': 'kh', 'ಗ': 'g', 'ಘ': 'gh', 'ಙ': 'ng',
  'ಚ': 'ch', 'ಛ': 'chh', 'ಜ': 'j', 'ಝ': 'jh', 'ಞ': 'nj',
  'ಟ': 'T', 'ಠ': 'Th', 'ಡ': 'D', 'ಢ': 'Dh', 'ಣ': 'N',
  'ತ': 't', 'ಥ': 'th', 'ದ': 'd', 'ಧ': 'dh', 'ನ': 'n',
  'ಪ': 'p', 'ಫ': 'ph', 'ಬ': 'b', 'ಭ': 'bh', 'ಮ': 'm',
  'ಯ': 'y', 'ರ': 'r', 'ಱ': 'rr', 'ಲ': 'l', 'ವ': 'v',
  'ಶ': 'sh', 'ಷ': 'Sh', 'ಸ': 's', 'ಹ': 'h', 'ಳ': 'L', 'ೞ': 'zh'
};

const KANNADA_SIGNS = {
  'ಂ': 'M', 'ಃ': 'H', '್': ''
};

function kannadaToLatin(text) {
  const res = [];
  const n = text.length;
  let i = 0;

  while (i < n) {
    if (i + 1 < n && text[i] === 'ೆ' && text[i + 1] === '್') {
      res.push('ae');
      i += 2;
      continue;
    }

    const ch = text[i];
    if (KANNADA_TO_LATIN_VOWELS[ch]) {
      res.push(KANNADA_TO_LATIN_VOWELS[ch]);
      i++;
      continue;
    }

    if (KANNADA_TO_LATIN_CONSONANTS[ch]) {
      const base = KANNADA_TO_LATIN_CONSONANTS[ch];
      if (i + 1 < n) {
        const nextCh = text[i + 1];
        if (nextCh === 'ೆ' && i + 2 < n && text[i + 2] === '್') {
          res.push(base + 'ae');
          i += 3;
          continue;
        }
        if (nextCh === '್') {
          res.push(base);
          i += 2;
          continue;
        }
        if (KANNADA_TO_LATIN_MATRAS[nextCh]) {
          res.push(base + KANNADA_TO_LATIN_MATRAS[nextCh]);
          i += 2;
          continue;
        }
      }
      res.push(base + 'a');
      i++;
      continue;
    }

    if (KANNADA_TO_LATIN_MATRAS[ch]) {
      res.push(KANNADA_TO_LATIN_MATRAS[ch]);
      i++;
      continue;
    }

    if (KANNADA_SIGNS[ch]) {
      res.push(KANNADA_SIGNS[ch]);
      i++;
      continue;
    }

    res.push(ch);
    i++;
  }

  return res.join('');
}

function kannadaToTigalari(text, formConjuncts = true) {
  // Normalize & canonicalize split matras
  text = text.normalize('NFC')
    .replace(/\u0CC6\u0CD5/g, 'ೇ')
    .replace(/\u0CC6\u0CD6/g, 'ೈ')
    .replace(/\u0CCA\u0CD5/g, 'ೋ')
    .replace(/\u0CC6\u0CC2/g, 'ೊ')
    .replace(/\u0CC6\u0CCC/g, 'ೌ');

  const chars = Array.from(text);
  const result = [];
  const n = chars.length;

  for (let i = 0; i < n; i++) {
    const ch = chars[i];
    if (ch === '್') {
      const nextIsConsonant = (i + 1 < n && KANNADA_CONSONANTS.has(chars[i + 1]));
      if (formConjuncts && nextIsConsonant) {
        result.push('\u{113D0}'); // CONJOINER
      } else {
        result.push('\u{113CE}'); // VIRAMA
      }
    } else {
      result.push(KANNADA_TO_TIGALARI[ch] || ch);
    }
  }

  return result.join('');
}

function tigalariToKannada(text) {
  const chars = Array.from(text);
  return chars.map(ch => TIGALARI_TO_KANNADA[ch] || ch).join('');
}

function detectScript(text) {
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if (cp >= 0x11380 && cp <= 0x113FF) return 'tigalari';
    if (cp >= 0x0C80 && cp <= 0x0CFF) return 'kannada';
  }
  return 'latin';
}

function inspectCodepoints(text) {
  return Array.from(text).map(ch => ({
    char: ch,
    codepoint: 'U+' + ch.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')
  }));
}

function transliterate(text, fromScript = 'auto', toScript = 'tigalari') {
  if (!text) return '';
  const src = (fromScript === 'auto') ? detectScript(text) : fromScript.toLowerCase();
  const tgt = toScript.toLowerCase();

  if (src === tgt) return text;

  if (src === 'latin') {
    if (tgt === 'kannada') return latinToKannada(text);
    if (tgt === 'tigalari') return kannadaToTigalari(latinToKannada(text));
  } else if (src === 'kannada') {
    if (tgt === 'latin') return kannadaToLatin(text);
    if (tgt === 'tigalari') return kannadaToTigalari(text);
  } else if (src === 'tigalari') {
    const kan = tigalariToKannada(text);
    if (tgt === 'kannada') return kan;
    if (tgt === 'latin') return kannadaToLatin(kan);
  }

  return text;
}

// Export for browser window and Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    latinToKannada,
    kannadaToLatin,
    kannadaToTigalari,
    tigalariToKannada,
    detectScript,
    inspectCodepoints,
    transliterate
  };
}
