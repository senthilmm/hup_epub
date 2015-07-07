import argparse
import zipfile
import re
from bs4 import BeautifulSoup, SoupStrainer
from lxml import etree, isoschematron

import logging

logging.basicConfig(level='DEBUG')


def parse_file_list(file):
    fnames = file.namelist()
    html_files = [name for name in fnames if name.endswith('html')]
    css_files = [name for name in fnames if name.endswith('css')]
    opf_file = [name for name in fnames if name.endswith('opf')]
    return html_files, css_files, opf_file


def get_metadata(opf, messages):
    """Find title and author metadata."""
    metadata = SoupStrainer("metadata")
    content = BeautifulSoup(opf, "xml", parse_only=metadata)
    try:
        messages.append('Title: {0}\n'.format(content.title.contents[0].string))
    except AttributeError:
        messages.append("No author found\n")
    try:
        sub = content.find(id="subtitle").string
        messages.append("Subtitle: "+sub+"\n")
    except AttributeError:
        messages.append("No subtitle found\n")
    try:
        messages.append('Author: {0}\n'.format(content.creator.contents[0].string))
    except:
        messages.append("No author found\n")


def html_tests(files, epub, messages):
    """For each html file, make the Soup and pass it to the tests."""
    nuts_file = [fname for fname in files if "note" in fname]  # find notes.html
    nuts = BeautifulSoup(epub.open(nuts_file[0])).select("a[id]")  # make soup from notes
    for html in files:
        file_to_test = html.rsplit('/', maxsplit=1)[1]
        messages.append("\n"+"{:-^60}".format(file_to_test)+"\n")
        html_file = epub.extract(html)
        soup_ingredients = epub.open(html)
        soup = BeautifulSoup(soup_ingredients)
        check_tags(html_file, messages)
        note_list = ["chapter", "intro", "preface"]
        for name in note_list:
            if name in file_to_test:
                check_notes(soup, nuts, file_to_test, messages)
    return messages


def check_tags(html, messages):
    schema_tree = etree.parse('test.sch')
    schematron = isoschematron.Schematron(schema_tree, store_report=True)
    html_parse = etree.parse(html)
    schematron.validate(html_parse)
    report = schematron.validation_report
    print(html, report.xpath("//text()"))



def check_notes(soup, footnotes, file, messages):
    """Examine callout and notes. Check that notes and links work both ways."""
    links = soup.select('a[href^="note"]')
    for link in links:
        l = link['href'].partition('#')[2]
        match = [footnote for footnote in footnotes if footnote['id'] == l]
        if not match[0]:
            messages.append("no match for "+l+"\n")
    return messages
        # except KeyError:


def main(file):
    epub = zipfile.ZipFile(file, 'r')
    messages = []
    output_filename = file.rsplit('.', maxsplit=1)[0]+".txt"
    html_files, css_files, opf_file = parse_file_list(epub)
    get_metadata(epub.open(opf_file[0]), messages)
    result = html_tests(html_files, epub, messages)
#    logging.debug(repr(result))
    with open(output_filename, 'w') as results:
        line = ''.join(result)
        results.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", help="epub file to be tested")
    args = parser.parse_args()
    main(args.epub)
