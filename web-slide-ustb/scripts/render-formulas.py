#!/usr/bin/env python3
"""Render data-tex objects to one outlined SVG each; needs XeLaTeX + dvisvgm.

Usage: python beike-ppt-template/scripts/render-formulas.py [deck.html]
The delivered HTML needs no TeX, web fonts, CDN, or runtime math renderer.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


class MathSources(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sources: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if 'data-math-asset' not in data:
            return
        name, tex = data['data-math-asset'], data.get('data-tex', '')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', name or '') or not tex:
            raise ValueError('Each math source needs a safe asset name and nonempty data-tex')
        if name in self.sources and self.sources[name] != tex:
            raise ValueError(f'Conflicting formula sources: {name}')
        self.sources[name] = tex


def main():
    deck = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'template.html'
    source = deck.read_text(encoding='utf-8')
    parser = MathSources()
    parser.feed(source)
    if not parser.sources:
        raise SystemExit('No data-math-asset sources found')
    for command in ('xelatex', 'dvisvgm'):
        if not shutil.which(command):
            raise SystemExit(f'{command} is required to rebuild formulas; existing SVGs remain usable')
    assets = deck.parent / 'assets' / 'math'
    assets.mkdir(parents=True, exist_ok=True)
    # Build into a private temporary directory; all public files are committed after success.
    with tempfile.TemporaryDirectory(prefix='beike-math-') as temp:
        work = Path(temp)
        results = []
        for name, tex in parser.sources.items():
            color = '005B94' if name.startswith('symbol-') else '12374E'
            document = (
                r'\documentclass[border=1pt]{standalone}' '\n'
                r'\usepackage{amsmath,unicode-math,xcolor}' '\n'
                r'\setmathfont{Cambria Math}' '\n'
                r'\begin{document}\fontsize{12}{14}\selectfont' '\n'
                r'\color[HTML]{' + color + r'}$\displaystyle ' + tex + '$\n'
                r'\end{document}' '\n'
            )
            (work / 'formula.tex').write_text(document, encoding='utf-8')
            for command in (
                ['xelatex', '-no-pdf', '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'formula.tex'],
                ['dvisvgm', '--no-fonts', '--exact-bbox', '--output=formula.svg', 'formula.xdv'],
            ):
                run = subprocess.run(command, cwd=work, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
                if run.returncode:
                    raise RuntimeError(f'{name}: {command[0]} failed\n{(run.stdout + run.stderr)[-5000:]}')
            svg = (work / 'formula.svg').read_text(encoding='utf-8')
            root = ET.fromstring(svg)
            # dvisvgm expresses dimensions in big points; TeX's 12pt em is 12*72/72.27 bp.
            em = 12 * 72 / 72.27
            width, height = (float(re.fullmatch(r'([0-9.]+)pt', root.attrib[key]).group(1)) / em for key in ('width', 'height'))
            pattern = r'(<img\b[^>]*\bdata-math-image="' + re.escape(name) + r'"[^>]*\bstyle=")[^"]*(")'
            source, count = re.subn(pattern, lambda m: m[1] + f'width:{width:.5f}em;height:{height:.5f}em' + m[2], source)
            if count != 1:
                raise ValueError(f'{name}: expected exactly one img[data-math-image] with a style attribute')
            results.append((name, svg))
        for name, svg in results:
            (assets / f'{name}.svg').write_text(svg, encoding='utf-8')
        deck.write_text(source, encoding='utf-8')
    print(f'Rendered {len(results)} Cambria Math SVGs; now run scripts/embed-assets.py for this HTML.')


if __name__ == '__main__':
    main()
