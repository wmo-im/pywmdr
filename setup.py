
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import io
import os
import re
from setuptools import Command, find_packages, setup
import sys
import zipfile
import glob
import shutil

from lxml import etree

from pywmdr.util import get_userdir, urlopen_


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, os.path.join('tests',
                                 'run_tests.py')])
        raise SystemExit(errno)


def read(filename, encoding='utf-8'):
    """read file contents"""
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with io.open(full_path, encoding=encoding) as fh:
        contents = fh.read().strip()
    return contents


def get_package_version():
    """get version from top-level package init"""
    version_file = read('pywmdr/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


USERDIR = get_userdir()

KEYWORDS = [
    'WMO',
    'Metadata',
    'WIGOS',
    'Test Suite',
]

DESCRIPTION = 'A Python implementation of the test suite for WMO WIGOS Metadata Representation'  # noqa

# ensure a fresh MANIFEST file is generated
if (os.path.exists('MANIFEST')):
    os.unlink('MANIFEST')

print(f'Downloading WMO WMDR XML Schemas and Codelists.xml to {USERDIR}')

if not os.path.exists(USERDIR):
    os.mkdir(USERDIR)
    FILE_URL = 'https://raw.githubusercontent.com/wmo-im/wmdr/master/xsd/wmdr.xsd'
    xsd_filename = f'{USERDIR}{os.sep}wmdr.xsd'
    with open(xsd_filename,'wb') as f:
        f.write(urlopen_(FILE_URL).read())

    CODELIST_URL = 'https://wis.wmo.int/2012/codelists/WMOCodeLists.xml'  # do we have this for wigos?

    schema_filename = f'{USERDIR}{os.sep}WMOCodeLists.xml'

    with open(schema_filename, 'wb') as f:
        f.write(urlopen_(CODELIST_URL).read())

    if not os.path.exists(f'{USERDIR}{os.sep}schema'):
        os.mkdir(f'{USERDIR}{os.sep}schema')
        os.mkdir(f'{USERDIR}{os.sep}schema{os.sep}resources')
        os.mkdir(f'{USERDIR}{os.sep}schema{os.sep}resources{os.sep}Codelist')
        os.mkdir(f'{USERDIR}{os.sep}schema{os.sep}resources{os.sep}maps')
        script_dirname = os.path.dirname(__file__)
        codelist_filenames = os.path.join(script_dirname, 'resources/Codelist/*.rdf')
        for file in glob.glob(codelist_filenames):
            shutil.copy(file,f'{USERDIR}{os.sep}schema{os.sep}resources{os.sep}Codelist')
        map_filenames = os.path.join(script_dirname, 'resources/maps/*.json')
        for file in glob.glob(map_filenames):
            shutil.copy(file,f'{USERDIR}{os.sep}schema{os.sep}resources{os.sep}maps')

    # because some ISO instances ref both gmd and gmx, create a
    # stub xsd in order to validate
    # SCHEMA = etree.Element('schema',
    #                        elementFormDefault='qualified',
    #                        version='1.0.0',
    #                        nsmap={None: 'http://www.w3.org/2001/XMLSchema'})

    # schema_wrapper_filename = f'{USERDIR}{os.sep}iso-all.xsd'

    # with open(schema_wrapper_filename, 'wb') as f:
    #     for uri in ['gmd', 'gmx']:
    #         namespace = f'http://www.isotc211.org/2005/{uri}'
    #         schema_location = f'schema/{uri}/{uri}.xsd'

    #         etree.SubElement(SCHEMA, 'import',
    #                          namespace=namespace,
    #                          schemaLocation=schema_location)
    #     f.write(etree.tostring(SCHEMA, pretty_print=True))
else:
    print(f'Directory {USERDIR} exists')


setup(
    name='pywmdr',
    version=get_package_version(),
    description=DESCRIPTION.strip(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    platforms='all',
    keywords=' '.join(KEYWORDS),
    author='',
    author_email='',
    maintainer='',
    maintainer_email='',
    url='https://github.com/wmo-im/pywmdr',
    install_requires=read('requirements.txt').splitlines(),
    packages=find_packages(),
    package_data={'pywdmr': ['dictionary.txt']},
    entry_points={
        'console_scripts': [
            'pywmdr=pywmdr:cli'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    cmdclass={'test': PyTest},
    test_suite='tests.run_tests'
)