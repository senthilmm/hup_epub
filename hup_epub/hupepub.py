import argparse
import zipfile
import re
from lxml import etree, isoschematron, objectify
import lxml.html as lh

import logging


def parse_file_list(file):
    fnames = file.namelist()
    html_files = [name for name in fnames if name.endswith('html')]
    css_files = [name for name in fnames if name.endswith('css')]
    opf_file = [name for name in fnames if name.endswith('opf')]
    return html_files, css_files, opf_file


def get_metadata(opf):
    """Find metadata"""
    meta_data = objectify.parse(opf).getroot()
    meta_list = meta_data.findall('.//{http://www.idpf.org/2007/opf}meta')
    dc_list = meta_data.find('.//{http://www.idpf.org/2007/opf}metadata')
    for child in dc_list.iterchildren():
        tag = child.xpath('local-name()')
        val = child.text
        logging.info("%s, %s", tag, val)


def html_tests(files, epub):
    """For each html, run schematron and check notes."""
    nuts_file = [fname for fname in files if "note" in fname]  # find notes.html
    notes = epub.open(nuts_file[0])
    note_list = lh.parse(notes).getroot().findall(".//a[@id]")
    for html in files:
        file_to_test = html.rsplit('/', maxsplit=1)[1]
        html_file = epub.open(html)
        check_tags(html_file)
        note_checks = ["chapter", "intro", "preface"]
        for name in note_checks:
            if name in file_to_test:
                html_file = epub.open(html)
                check_notes(html_file, note_list, file_to_test)


def check_tags(html):
    """run the schematron tests on each html document"""
    schema_tree = etree.parse('schematron/epub-schematron.sch')
    schematron = isoschematron.Schematron(schema_tree, store_report=True)
    html_parse = etree.parse(html)
    logging.info("%s -------------", html.name)
    schematron.validate(html_parse)
    reports = schematron.validation_report
    for report in reports.iter():
        if report.text is None or report.text == "None":
            pass
        else:
            logging.info("test: %s", report.text)


def check_notes(html, notes, file_to_test):
    """for each chapter, check note callouts for matching endnotes, then reverse"""
    chapter = lh.parse(html).getroot().findall(".//a[@href]")
    for link in chapter:
        if link.attrib['href'].startswith('note'):
            part = link.attrib['href'].partition('#')[2]
            match = [ref.tag for ref in notes if ref.attrib['id'] == part]
            if not match[0]:
                logging.info('no match for %s', link[0].attrib['id'] )
    for ref in notes:
        chap_refs = [link for link in chapter if 'id' in link.attrib]
        target = ref.attrib.get('href')
        if target:
            if target.partition('#')[0] == file_to_test:
                match = [link.tag for link in chap_refs if link.attrib['id'] == target.partition('#')[2]]
                if match[0] is None:
                    logging.info('no match')
        else:
            logging.info('No href attribute')

def main(file):
    epub = zipfile.ZipFile(file, 'r')
    output_filename = file.rsplit('.', maxsplit=1)[0]+".txt"
    html_files, css_files, opf_file = parse_file_list(epub)
    logname = file + ".log"
    logging.basicConfig(filename=logname, filemode='w', level=logging.INFO, format='%(message)s')
    get_metadata(epub.open(opf_file[0]))
    html_tests(html_files, epub)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("epub", help="epub file to be tested")
    args = parser.parse_args()
    main(args.epub)
