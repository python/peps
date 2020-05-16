"""Transforms Sphinx HTML output into  python.org input format"""

from pathlib import Path
from bs4 import BeautifulSoup

if __name__ == '__main__':
    root_path = Path(".")
    html_path = root_path.joinpath('_build')
    package_path = root_path.joinpath("package/peps")
    package_path.mkdir(parents=True, exist_ok=True)

    for file_path in html_path.glob("pep-*"):
        if file_path.suffix not in '.html':
            continue
        print(file_path.stem)

        soup = BeautifulSoup(file_path.read_text(encoding="UTF8"), 'lxml')
        contents = soup.find('div', class_="body").div

        # Removes <p> tags from list item elements
        for tag in contents.findAll("li"):
            try:
                tag.p.unwrap()
            except AttributeError:
                # If no <p> tag to unwrap
                pass

        # Removes all permalink elements
        [tag.decompose() for tag in contents.findAll(class_="headerlink")]

        # Replace brackets class with [ and ]
        for tag in contents.findAll("a", class_="brackets"):
            tag.insert(0, "[")
            tag.append("]")
            tag["class"].remove("brackets")

        # Reformat <code> tags to <tt>
        for tag in list(contents.findAll("code")):
            tag.name = "tt"
            [x.unwrap() if x.name else x for x in tag.contents]

        # Reformat code literal blocks
        for tag in contents.findAll("div", class_="highlight-default"):
            tag.div.unwrap()
            tag.pre.unwrap()
            tag.name = "pre"
            tag["class"] = "literal-block"
            tag.string = "\n" + tag.text.strip() + "\n"

        # Transform blockquotes
        for tag in contents.findAll("blockquote"):
            tag.div.unwrap()
            if tag.p:
                tag.p.unwrap()

        # Remove Sphinx Header
        contents.h1.decompose()

        # Promotes all remaining headers
        for level in range(6 - 1):
            h_level = level + 2
            headers = contents.findAll(f"h{h_level}")
            for header in headers:
                header.name = f"h{h_level - 1}"

        dl = contents.find('dl')

        # Adds horizontal rule
        dl.insert_after(soup.new_tag("hr"))

        # Parses the PEP Info box to transform to pydotorg standards
        for tag in dl.findChildren():
            if tag.name == "dt":
                tag.name = "th"
                tag.string += ":"
                tag.attrs['class'] = 'field-name'
                value_tag = tag.find_next_sibling()
                value_tag.name = "td"
                value_tag.string = value_tag.text.strip("\n")
                value_tag['class'] = 'field-body'

                # Wrap the key-value pair in a <tr> element
                tr = soup.new_tag("tr", **{'class': 'field'})
                tag.insert_before(tr)
                tr.insert(0, value_tag)
                tr.insert(0, tag)

        dl.name = 'tbody'

        classes = dl['class']
        classes.remove("simple")
        classes.append("docutils")
        del dl['class']
        tbl = soup.new_tag('table', **{'class': classes})
        dl.wrap(tbl)
        tbl.insert(0, soup.new_tag("col", **{'class': "field-body"}))
        tbl.insert(0, soup.new_tag("col", **{'class': "field-name"}))

        # Fix footnotes/references
        dl_refs = contents.findAll('dl', class_="footnote brackets")

        for ref in dl_refs:
            footnote_rows = []
            for tag in ref.findChildren():
                if tag.name == "dt":
                    tag.name = "td"
                    tag.attrs['class'] = 'label'
                    if tag.span and "brackets" in tag.span.get("class"):
                        tag.span.insert(0, "[")
                        tag.span.append("]")
                        tag.span.unwrap()

                    value_tag = tag.find_next_sibling()
                    value_tag.name = "td"
                    value_tag.string = value_tag.text.strip("\n")

                    # Wrap the key-value pair in a <tr> element
                    tr = soup.new_tag("tr")
                    tr.insert(0, value_tag)
                    tr.insert(0, tag)
                    footnote_rows.append(tr)
            ref.name = 'table'
            ref["class"] = "docutils footnote"
            ref.contents = footnote_rows
            # TODO combine all tables into one (relianbt on fixingf PEP8 table mismatch)

        # Writes transformed HTML
        write_path = Path('./package/peps') / file_path.name
        html = [str(i) for i in contents.contents]
        write_path.write_text(str("".join(html)), encoding="UTF8")

        del soup, contents, headers, dl, tbl, dl_refs, html
