import csv
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_robots = ""
        self.canonical = ""
        self.text_parts = []
        self.in_title = False
        self.skip = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag in {"script", "style", "noscript", "svg"}:
            self.skip = True
        elif tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.meta_robots = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = attrs.get("href", "")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag in {"script", "style", "noscript", "svg"}:
            self.skip = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title += text + " "
        elif not self.skip:
            self.text_parts.append(text)


def normalize_url(value):
    value = value.strip()
    if not value or value.startswith("#"):
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def fetch(url, user_agent, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        raw = resp.read(2_000_000)
        content_type = resp.headers.get("content-type", "")
        charset_match = re.search(r"charset=([^;]+)", content_type, re.I)
        charset = charset_match.group(1).strip() if charset_match else "utf-8"
        html = raw.decode(charset, errors="replace")
        return resp.status, resp.geturl(), content_type, html


def analyze(url, timeout):
    desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36 SEOVisibilityChecker/1.0"
    try:
        status, final_url, content_type, html = fetch(url, desktop_ua, timeout)
        parser = PageParser()
        parser.feed(html)
        body_text = " ".join(parser.text_parts)
        compact_text = re.sub(r"\s+", " ", body_text).strip()
        lower = compact_text.lower()
        warning_terms = ["login", "sign in", "restricted", "forbidden", "unauthorized", "access denied", "會員登入", "請登入", "登入", "受限制"]
        warnings = [term for term in warning_terms if term in lower]
        robots = parser.meta_robots.lower()
        flags = []
        if status >= 400:
            flags.append("http_error")
        if "noindex" in robots:
            flags.append("noindex")
        if len(compact_text) < 500:
            flags.append("thin_text")
        if warnings:
            flags.append("login_or_restriction_words")
        if "text/html" not in content_type.lower():
            flags.append("non_html")
        return {
            "input_url": url,
            "final_url": final_url,
            "status": status,
            "title": parser.title.strip(),
            "meta_robots": parser.meta_robots.strip(),
            "canonical": parser.canonical.strip(),
            "text_length": len(compact_text),
            "restriction_terms_found": ";".join(warnings),
            "flags": ";".join(flags) if flags else "ok",
            "error": "",
        }
    except urllib.error.HTTPError as e:
        return {"input_url": url, "final_url": getattr(e, "url", url), "status": e.code, "title": "", "meta_robots": "", "canonical": "", "text_length": 0, "restriction_terms_found": "", "flags": "http_error", "error": str(e)}
    except Exception as e:
        return {"input_url": url, "final_url": "", "status": "", "title": "", "meta_robots": "", "canonical": "", "text_length": 0, "restriction_terms_found": "", "flags": "fetch_failed", "error": str(e)}


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 batch_seo_visibility_checker.py sites.txt report.csv")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    timeout = 20
    with open(input_path, "r", encoding="utf-8") as f:
        urls = [normalize_url(line) for line in f]
    urls = [url for url in urls if url]
    fields = ["input_url", "final_url", "status", "title", "meta_robots", "canonical", "text_length", "restriction_terms_found", "flags", "error"]
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url}")
            writer.writerow(analyze(url, timeout))
            time.sleep(0.5)


if __name__ == "__main__":
    main()
