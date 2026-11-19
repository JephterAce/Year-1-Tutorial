"""Syntax-check inline JavaScript in Learnwise HTML pages using Node.js."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.current = []
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag == "script" and not dict(attrs).get("src"):
            self.active = True
            self.current = []
    def handle_data(self, data):
        if self.active:
            self.current.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.active:
            self.items.append("".join(self.current))
            self.active = False

def main():
    pages = list((ROOT / "frontend").glob("*.html")) + list((ROOT / "admin").glob("*.html"))
    for page in pages:
        parser = Scripts()
        parser.feed(page.read_text(encoding="utf-8"))
        for index, source in enumerate(parser.items, start=1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as tmp:
                tmp.write(source)
                tmp.flush()
                result = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
            if result.returncode:
                raise SystemExit(f"{page.name} inline script {index} failed syntax check:\n{result.stderr}")
    print(f"JavaScript syntax valid in {len(pages)} Learnwise HTML pages.")

if __name__ == "__main__":
    main()
