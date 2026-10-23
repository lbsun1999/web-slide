"""Export this HTML slide template to a verified 960 x 540 pt PDF.

Usage: python scripts/export-pdf.py [slides.html] [--output slides.pdf]
Requires Python 3.10+ and local Chrome or Edge; no Python packages or print driver.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote


class Slides(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.images: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'article' and 'page' in attributes.get('class', '').split():
            self.count += 1
        if tag == 'img':
            self.images.append(attributes.get('src', ''))


def find_browser() -> Path:
    candidates = [shutil.which(name) for name in ('chrome', 'msedge', 'chromium', 'google-chrome')]
    for variable in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
        base = os.environ.get(variable)
        if base:
            candidates.extend(str(Path(base) / suffix) for suffix in (
                'Google/Chrome/Application/chrome.exe', 'Microsoft/Edge/Application/msedge.exe'))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise RuntimeError('未找到 Chrome 或 Edge，请先安装其中一个浏览器。')


def validate_pdf(data: bytes, expected_pages: int) -> None:
    if not data.startswith(b'%PDF-'):
        raise RuntimeError('浏览器未生成有效 PDF。')
    count = len(re.findall(rb'/Type\s*/Page\b', data))
    boxes = re.findall(rb'/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]', data)
    if count != expected_pages or len(boxes) != expected_pages:
        raise RuntimeError(f'PDF 页数异常：应为 {expected_pages} 页，实际 {count} 页。未覆盖已有 PDF。')
    for box in boxes:
        left, bottom, right, top = map(float, box)
        if abs(right - left - 960) > .05 or abs(top - bottom - 540) > .05:
            raise RuntimeError('PDF 纸张不是 960×540pt 的 16:9 宽屏，已拒绝保存。请保留模板的打印样式。')


def export(source: Path, output: Path) -> int:
    source, output = source.resolve(), output.resolve()
    if source.suffix.lower() not in ('.html', '.htm') or not source.is_file():
        raise RuntimeError('输入必须是已保存的 HTML 幻灯片文件。')
    if output.suffix.lower() != '.pdf':
        raise RuntimeError('输出文件必须使用 .pdf 扩展名。')
    slides = Slides()
    slides.feed(source.read_text(encoding='utf-8-sig'))
    if not slides.count:
        raise RuntimeError('HTML 中没有找到 article.page 幻灯片。')
    for image in slides.images:
        if image.startswith('data:'):
            continue
        if image.startswith(('http:', 'https:', '//')):
            raise RuntimeError('请先用“保存HTML”内嵌图片，或把外部图片改为本地资产。')
        if not image or not (source.parent / unquote(image.split('#')[0].split('?')[0])).is_file():
            raise RuntimeError(f'图片不存在：{image}')
    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix='lntu-pdf-', ignore_cleanup_errors=True) as folder:
        work = Path(folder)
        temporary_pdf = work / 'slides.pdf'
        command = [str(browser), '--headless', '--disable-gpu', '--no-sandbox', '--no-first-run', '--no-default-browser-check',
                   '--disable-extensions', '--disable-background-networking', '--disable-sync',
                   f'--user-data-dir={work / "profile"}', '--no-pdf-header-footer',
                   '--virtual-time-budget=5000', f'--print-to-pdf={temporary_pdf}', source.as_uri()]
        try:
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                    timeout=45, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except subprocess.TimeoutExpired as error:
            raise RuntimeError('浏览器导出超时，请检查 HTML 与本地图片后重试。') from error
        if result.returncode or not temporary_pdf.is_file():
            raise RuntimeError('浏览器未完成 PDF 导出，请确认本地浏览器能够启动后重试。')
        data = temporary_pdf.read_bytes()
        validate_pdf(data, slides.count)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    return slides.count


def main() -> int:
    parser = argparse.ArgumentParser(description='直接导出无纸张白边的 16:9 PDF，不调用系统打印机。')
    parser.add_argument('html', nargs='?', type=Path, default=Path(__file__).resolve().parents[1] / 'template.html')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.html.with_suffix('.pdf')
    try:
        count = export(args.html, output)
    except (RuntimeError, OSError, UnicodeError) as error:
        print(f'导出失败：{error}', file=sys.stderr)
        return 1
    print(f'已导出：{output.resolve()}\n{count} 页；每页 960×540pt（16:9）；无额外纸张白边、日期或路径。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
