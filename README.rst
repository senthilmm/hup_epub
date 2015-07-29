Test Protocol for HUP Ebooks
============================

Introduction
------------

The test protocol script is being developed to help insure compliance with the HUP Epub3 coding guidelines. The file is parsed and individual elements are checked against the supplied test condition.

Basic Tests
-----------

The core of the test is a schematron test suite. The epub archive is opened and each html file is tested. The test results are passed to the logger and output to a file. Test results should be considered warnings rather than strict errors, due to the limitations of the test logic. But the results should provide guidance where deviations from the specifications exist and need to be checked. Over time, I hope to be able to improve the specificity of the tests and the detail of the messages.

The log file should have as a header a dump of the metadata from the content.opf file. The script will also attempt to check endnotes against text callouts. The test expects to find all the notes in one file; if the notes are broken into two, the test will fail. Also, the test does not yet deal with notes that may be at the end of a chapter.

Currently, the script is configured to run from the command line with Python 3. It was developed with Python 3.4, and I haven't tested with earlier versions.

Install and run
---------------

This can be installed into an environment with the latest Python and pip. The only dependency is lxml.

::

    pip install git+https://github.com/bcholfin/hup_epub.git

Get the epub-schematron.sch file from https://github.com/bcholfin/schematron.git, place it wherever is convenient.

run::

    hup_epub.py file-to-test.epub epub-schematron.sch
