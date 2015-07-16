import argparse
import zipfile
import re
from lxml import etree, isoschematron, objectify
import lxml.html as lh

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
    meta_data = objectify.parse(opf).getroot()
    meta_list = meta_data.findall('.//{http://www.idpf.org/2007/opf}meta')
    dc_list = meta_data.find('.//{http://www.idpf.org/2007/opf}metadata')
    for child in dc_list.iterchildren():
        print(child.xpath('local-name()'), child.text)


def html_tests(files, epub, messages):
    """For each html file, make the Soup and pass it to the tests."""
    nuts_file = [fname for fname in files if "note" in fname]  # find notes.html
    notes = epub.extract(nuts_file[0])
    note_file = lh.parse(notes).getroot().findall(".//a[@id]")
    for html in files:
        file_to_test = html.rsplit('/', maxsplit=1)[1]
        messages.append("\n"+"{:-^60}".format(file_to_test)+"\n")
        html_file = epub.extract(html)
        check_tags(html_file, messages)
        note_list = ["chapter", "intro", "preface"]
        for name in note_list:
            if name in file_to_test:
                check_notes(html_file, note_file, file_to_test, messages)
    return messages


def check_tags(html, messages):
    schema_tree = etree.parse('test.sch')
    schematron = isoschematron.Schematron(schema_tree, store_report=True)
    html_parse = etree.parse(html)
    schematron.validate(html_parse)
    report = schematron.validation_report
    print(html, report.xpath("//text()"))


def check_notes(html, notes, file_to_test, messages):
    chapter = lh.parse(html).getroot().findall(".//a[@href]")
    # note_refs = lh.iterlinks(notes)
    for link in chapter:
        if link.attrib['href'].startswith('note'):
            part = link.attrib['href'].partition('#')[2]
            match = [ref.tag for ref in notes if ref.attrib['id'] == part]
            if not match[0]:
                print('no match for', link[0].attrib['id'] )
            print(match[0])
    for ref in notes:
        chap_refs = [link for link in chapter if 'id' in link.attrib]
        try:
            target = ref.attrib['href'].partition('#')
            if target[0] == file_to_test:
                match = [link.tag for link in chap_refs if link.attrib['id'] == target[2]]
                if match[0]:
                    print('match:', match[0])
                else:
                    print('no match')
        except KeyError:
            print('No href attribute')

def main(file):
    epub = zipfile.ZipFile(file, 'r')
    messages = []
    output_filename = file.rsplit('.', maxsplit=1)[0]+".txt"
    html_files, css_files, opf_file = parse_file_list(epub)
    get_metadata(epub.extract(opf_file[0]), messages)
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
