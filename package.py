"""Transforms Sphinx HTML output into  python.org input format"""

from bs4 import BeautifulSoup
from pathlib import Path

if __name__ == '__main__':
    root_path = Path(".")
    html_path = root_path.joinpath('_build')
    package_path = root_path.joinpath("package/peps")
    package_path.mkdir(parents=True, exist_ok=True)

    for file_path in html_path.glob("pep-*"):
        if file_path.suffix not in '.html':
            continue

        soup = BeautifulSoup(file_path.read_text(encoding="UTF8"), 'lxml')
        contents = soup.find('div', class_="body").div
        dl = contents.find('dl')
        for tag in dl.findChildren():
            if tag.name == "dt":
                tag.name = "th"
                tag.find_next_sibling().name = "td"
                tag.attrs['class'] = 'field-name'
                tag.find_next_sibling()['class'] = 'field-body'
                tr = soup.new_tag("tr", **{'class': 'field'})
                tag.insert_before(tr)
                tr.insert(0, tag.find_next_sibling())
                tr.insert(0, tag)

        dl.name = 'tbody'
        tbl = soup.new_tag('table', **{'class': dl['class']})
        dl.wrap(tbl)
        dl['class'] = []
        tbl.insert(0, soup.new_tag("col", **{'class': "field-body"}))
        tbl.insert(0, soup.new_tag("col", **{'class': "field-name"}))

        write_path = Path('./package/peps') / file_path.name
        write_path.write_text(str(contents), encoding="UTF8")

        del soup, contents, dl, tbl
