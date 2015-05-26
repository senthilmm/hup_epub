import argparse
import zipfile
import re
from bs4 import BeautifulSoup, SoupStrainer

tag_list = [{'tag': 'body', 'attrs': {'epub:type': 'bodymatter'}},
            {'tag': 'article', 'attrs': {'role': 'main', 'epub:type': 'chapter'}},
            {'tag': 'img', 'attrs': {'id': '', 'alt': ''}},
            {'tag': 'blockquote', 'attrs': {'class': ['epigraph', 'extract']}},
            {'tag': 'tr', 'attrs': {'role': 'row'}}
            {'tag': 'h1', 'attrs': {'class': 'head'}}
            ]


def parse_file_list(file):
    fnames = file.namelist()
    html_files = [name for name in fnames if name.endswith('html')]
    css_files = [name for name in fnames if name.endswith('css')]
    opf_file = [name for name in fnames if name.endswith('opf')]
    return html_files, css_files, opf_file


def get_metadata(opf):
    """Find title and author metadata and print it."""
    metadata = SoupStrainer("metadata")
    content = BeautifulSoup(opf, "xml", parse_only=metadata)
    try:
        print('Title: {0}'.format(content.title.contents[0].string))
    except AttributeError:
        print("No author found")
    try:
        sub = content.find(id="subtitle").string
        print("Subtitle: ", sub)
    except AttributeError:
        print("No subtitle found")
    try:
        print('Author: {0}'.format(content.creator.contents[0].string))
    except:
        print("No author found")


class Test:
    """test suite for html files in epub"""
    def __init__(self, files, epub, output_filename):
        """set up files for tests"""
        self.out_file = open(output_filename, 'w')
        self.html_tests(files, epub)

    def html_tests(self, files, epub):
        """For each html file, make the Soup and pass it to the tests."""
        nuts_file = [fname for fname in files if "note" in fname]  # find notes.html
        nuts = BeautifulSoup(epub.open(nuts_file[0])).select("p > a:nth-of-type(1)")  # make soup from notes
        for html in files:
            file_test = html.rsplit('/', maxsplit=1)[1]
            self.out_file.write("\n"+"{:-^60}".format(file_test)+"\n")
            soup = BeautifulSoup(epub.open(html))
            self.check_tags(soup, tag_list)
            text_list = ["chapter", "intro", "preface"]
            for text in text_list:
                if text in file_test:
                    self.check_notes(soup, nuts, file_test)
        self.out_file.close()

    def check_tags(self, soup, tags):
        for tag in tags:
            tag_soup = soup.find_all(tag.get("tag"))
            for element in tag_soup:
                attr_exist = self.check_attr_exist(element, tag["attrs"])
                if attr_exist:
                    self.check_attr_values(element, tag["attrs"])

    def check_figure(self, soup):
        """Examine <figure> tags. Check if fallbacks are needed."""
        figures = soup.find_all('figure')
        for figure in figures:
            if figure.table:
                if figure.img:
                    self.check_attr_values(figure.img, "class", "fallback")
                else:
                    self.out_file.write("no fallback image\n")

    def check_attr_exist(self, tag, attrs):
        """Check attribute attr exists for tag."""
        for attr in attrs.keys():
            print(attr, tag.name, tag.attrs)
            if attr not in tag.attrs:
                self.out_file.write(attr+" not found for "+tag.name+"\n")
                return False
            else:
                return True

    def check_attr_values(self, tag, attrs):
        """check that attribute has allowed value"""
        for attr, values in attrs.items():
            print(attr, values, tag.name, tag.attrs)
            for value in values:
                if value not in tag.attrs[attr]:
                    self.out_file.write(attr+" value "+value+" missing or incorrect\n")

    def check_alt_text(self, soup):
        """Check <img> tags for alt-text"""
        images = soup.find_all('img')
        for image in images:
            if ('alt' not in image.attrs) or (image['alt'] == "image") or (image['alt'] == ""):
                self.out_file.write("no alt text for "+image.name+"\n")

    def check_notes(self, soup, nuts, file):
        """Examine callout and notes. Check that notes and links work both ways."""
        links = soup.select('a[href^="note"]')
        footnotes = nuts
        for link in links:
            l = link['href'].partition('#')[2]
            for fnote in footnotes:
                if fnote['id']:
                    if fnote['id'] == l:
                        m = fnote
#                        print(m)
                else:
                    print('no id')
            # try:
            #     m = [f for f in footnotes if f['id'] == l]
            #     if not m[0]:
            #         self.out_file.write("no match for "+l+"\n")
            # except KeyError:


def main(file):
    epub = zipfile.ZipFile(file, 'r')
    output_filename = file.rsplit('.', maxsplit=1)[0]+".txt"
    html_files, css_files, opf_file = parse_file_list(epub)
    get_metadata(epub.open(opf_file[0]))
    Test(html_files, epub, output_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", help="epub file to be tested")
    args = parser.parse_args()
    main(args.epub)
