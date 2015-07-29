"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name='hup_epub',
    version='0.3.0',

    description='Test suite for epub3 guidelines compliance',
    url='https://github.com/bcholfin/hupepub.git',
    author='Bryan Cholfin at Harvard University Press',
    author_email='bryan_cholfin@harvard.edu',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Test Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Harvard University Press HUP Epub3',
    packages=['hup_epub'],
    install_requires=['lxml'],
    package_data={
        '': ['test.sch'],
    },

)
