import argparse
import zipfile
import re
from bs4 import BeautifulSoup, SoupStrainer
import logging

logging.basicConfig(level='DEBUG')

tag_list = [{'tag': 'body', 'attrs': {'epub:type': ['bodymatter']}},
            {'tag': 'article', 'attrs': {'role': ['main'], 'epub:type': ['chapter']}},
            {'tag': 'img', 'attrs': {'id': [''], 'alt': ['']}},
            {'tag': 'blockquote', 'attrs': {'class': ['epigraph', 'extract']}},
            {'tag': 'tr', 'attrs': {'role': ['row']}},
            {'tag': 'h1', 'attrs': {'class': ['head']}},
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


def html_tests(files, epub, messages):
    """For each html file, make the Soup and pass it to the tests."""
    nuts_file = [fname for fname in files if "note" in fname]  # find notes.html
    nuts = BeautifulSoup(epub.open(nuts_file[0])).select("a[id]")  # make soup from notes
    for html in files:
        file_test = html.rsplit('/', maxsplit=1)[1]
        messages.append("\n"+"{:-^60}".format(file_test)+"\n")
        soup = BeautifulSoup(epub.open(html))
        check_tags(soup, tag_list, messages)
        text_list = ["chapter", "intro", "preface"]
        for text in text_list:
            if text in file_test:
                check_notes(soup, nuts, file_test, messages)
    return messages


def check_tags(soup, tag_list, messages):
    for tag_to_check in tag_list:
        logging.debug("tag %r" % tag_to_check)
        tag_soup = soup.find_all(tag_to_check.get("tag"))
        for element in tag_soup:
            message = [check_attr_values(element, attr, tag_to_check["attrs"][attr], messages)
                        for attr in tag_to_check["attrs"] if check_attr_exist(element, attr, messages)]
            messages.append(message)
    return messages


def check_figure(soup, messages):
    """Examine <figure> tags. Check if fallbacks are needed."""
    figures = soup.find_all('figure')
    for figure in figures:
        if figure.table:
            if figure.img:
                check_attr_values(figure.img, "class", "fallback", messages)
            else:
                messages.append("no fallback image\n")
    return messages


def check_attr_exist(tag, attr, messages):
    if attr not in tag.attrs:
        messages.append(attr+" not found for "+tag.name+"\n")
        return False
    else:
        return True


def check_attr_values(tag, attr, values, messages):
    """check that attribute has allowed value"""
    logging.debug("tag %r %r" % (tag.name, attr))
    for value in values:
        if value not in tag.attrs[attr]:
            messages.append(attr+" value "+value+" missing or incorrect\n")
    return messages


def check_alt_text(soup, messages):
    """Check <img> tags for alt-text"""
    images = soup.find_all('img')
    for image in images:
        if ('alt' not in image.attrs) or (image['alt'] == "image") or (image['alt'] == ""):
            messages.append("no alt text for "+image.name+"\n")
    return messages


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
    get_metadata(epub.open(opf_file[0]))
    result = html_tests(html_files, epub, messages)
    with open(output_filename, 'w') as results:
        for line in result:
            results.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", help="epub file to be tested")
    args = parser.parse_args()
    main(args.epub)
