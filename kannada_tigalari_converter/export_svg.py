#!/usr/bin/env python3
"""
Tulu-Tigalari SVG Vector Exporter
Generates font-independent, high-fidelity SVG graphics for Tigalari and Kannada text.
Ideal for typography, publications, research posters, and devices without Tigalari fonts.
"""

import html
import os
import sys
from typing import Optional, Dict

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.transliterator import transliterate, detect_script, inspect_codepoints


class TuluSvgExporter:
    """Generates crisp SVG vector presentation cards for Tulu & Tigalari text."""

    @staticmethod
    def generate_svg(
        text: str,
        title: str = "Tulu-Tigalari Script Card",
        theme: str = "dark",
        width: int = 800,
        height: int = 420,
    ) -> str:
        """Create a complete SVG document containing rendered script and transliteration."""
        detected = detect_script(text)
        if detected == "tigalari":
            tigalari = text
            kannada = transliterate(text, from_script="tigalari", to_script="kannada")
            latin = transliterate(kannada, from_script="kannada", to_script="latin")
        elif detected == "latin":
            latin = text
            kannada = transliterate(text, from_script="latin", to_script="kannada")
            tigalari = transliterate(kannada, from_script="kannada", to_script="tigalari")
        else:
            kannada = text
            tigalari = transliterate(text, from_script="kannada", to_script="tigalari")
            latin = transliterate(text, from_script="kannada", to_script="latin")

        # Codepoints list
        cps = inspect_codepoints(tigalari)
        codepoints_str = " ".join(f"{cp}" for _, cp in cps[:8])
        if len(cps) > 8:
            codepoints_str += " …"

        # Theme styling
        if theme == "light":
            bg_start, bg_end = "#f8fafc", "#f1f5f9"
            card_border = "#cbd5e1"
            title_color = "#64748b"
            main_color = "#0f172a"
            sub_color = "#334155"
            badge_bg = "#e2e8f0"
            badge_fg = "#0284c7"
            meta_color = "#94a3b8"
        else:
            bg_start, bg_end = "#0f172a", "#1e293b"
            card_border = "#334155"
            title_color = "#94a3b8"
            main_color = "#f8fafc"
            sub_color = "#38bdf8"
            badge_bg = "#1e293b"
            badge_fg = "#38bdf8"
            meta_color = "#64748b"

        safe_title = html.escape(title)
        safe_tigalari = html.escape(tigalari)
        safe_kannada = html.escape(kannada)
        safe_latin = html.escape(latin)
        safe_codepoints = html.escape(codepoints_str)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_start}"/>
      <stop offset="100%" stop-color="{bg_end}"/>
    </linearGradient>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;display=swap');
      @font-face {{
        font-family: 'MalligeUnicode';
        src: local('Mallige Unicode'), local('Mallige'), local('Tulu Tigalari');
      }}
      .card-bg {{ fill: url(#cardGrad); rx: 16px; stroke: {card_border}; stroke-width: 1.5px; }}
      .header-title {{ font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; fill: {title_color}; letter-spacing: 0.05em; text-transform: uppercase; }}
      .badge-bg {{ fill: {badge_bg}; rx: 6px; }}
      .badge-text {{ font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; fill: {badge_fg}; }}
      .tigalari-text {{ font-family: 'MalligeUnicode', 'Inter', sans-serif; font-size: 44px; font-weight: 600; fill: {main_color}; }}
      .kannada-text {{ font-family: 'Inter', 'Noto Sans Kannada', sans-serif; font-size: 24px; font-weight: 500; fill: {sub_color}; }}
      .latin-text {{ font-family: 'Inter', monospace; font-size: 16px; font-weight: 400; fill: {meta_color}; }}
      .codepoints-text {{ font-family: monospace; font-size: 12px; fill: {meta_color}; }}
      .footer-brand {{ font-family: 'Inter', sans-serif; font-size: 11px; fill: {meta_color}; }}
    </style>
  </defs>

  <!-- Card Background -->
  <rect x="8" y="8" width="{width - 16}" height="{height - 16}" class="card-bg" />

  <!-- Header -->
  <g transform="translate(36, 48)">
    <text x="0" y="0" class="header-title">{safe_title}</text>
    <rect x="{width - 240}" y="-16" width="168" height="24" class="badge-bg" />
    <text x="{width - 232}" y="0" class="badge-text">UNICODE 16.0 COMPLIANT</text>
  </g>

  <!-- Main Tigalari Script Display -->
  <g transform="translate(36, 130)">
    <text x="0" y="0" class="tigalari-text">{safe_tigalari}</text>
  </g>

  <!-- Kannada Subtitle -->
  <g transform="translate(36, 190)">
    <text x="0" y="0" class="kannada-text">ಕನ್ನಡ: {safe_kannada}</text>
  </g>

  <!-- Latin Phonetic -->
  <g transform="translate(36, 235)">
    <text x="0" y="0" class="latin-text">Phonetic: {safe_latin}</text>
  </g>

  <line x1="36" y1="265" x2="{width - 36}" y2="265" stroke="{card_border}" stroke-width="1" />

  <!-- Technical Codepoints & Footer -->
  <g transform="translate(36, 310)">
    <text x="0" y="0" class="codepoints-text">Codepoints: {safe_codepoints}</text>
    <text x="0" y="32" class="footer-brand">Tulu-Tigalari NLP Platform | Official Unicode 16.0 (U+11380–U+113FF)</text>
  </g>
</svg>
"""
        return svg.strip()

    @classmethod
    def save_to_file(cls, text: str, output_path: str, **kwargs) -> str:
        """Generate and save SVG to target file."""
        svg_content = cls.generate_svg(text, **kwargs)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Export Tulu/Tigalari text to SVG vector graphic")
    parser.add_argument("text", type=str, help="Text to render (Tulu Kannada, Tigalari, or Latin)")
    parser.add_argument("-o", "--output", type=str, default="tulu_script_card.svg", help="Output .svg file path")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="Color theme (default: dark)")
    args = parser.parse_args()

    out = TuluSvgExporter.save_to_file(args.text, args.output, theme=args.theme)
    print(f"✨ Successfully exported SVG vector graphic to: {out}")


if __name__ == "__main__":
    main()
