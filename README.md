# pywmdr

[![Build Status](https://github.com/wmo-im/pywmdr/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/wmo-im/pywmdr/actions)

# WIGOS Metadata Record Test Suite

pywmdr provides validation and quality assessment capabilities for the [WIGOS Metadata Record](https://wmo-im.github.io/wmdr) (WMDR2) standard.

- validation against [WMDR2](https://wmo-im.github.io/wmdr2/standard/wmdr2-DRAFT.html), specifically [Annex A: Conformance Class Abstract Test Suite](https://wmo-im.github.io/wmdr2/standard/wmdr2-DRAFT.html#_conformance_class_abstract_test_suite_normative)), implementing an executable test suite against the ATS

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywmdr).

```bash
pip3 install pywmdr
```

### From source

Install latest development version.

```bash
python3 -m venv pywmdr
cd pywmdr
. bin/activate
git clone https://github.com/wmo-im/pywmdr.git
cd pywmdr
pip3 install -r requirements.txt
pip3 install .
```

## Running

From command line:
```bash
# fetch version
pywmdr --version

# sync supporting configuration bundle (schemas, topics, etc.)
pywmdr bundle sync

# abstract test suite

# validate WMDR2 metadata against abstract test suite (file on disk)
pywmdr ets validate /path/to/file.json

# validate WMDR2 metadata against abstract test suite (URL)
pywmdr ets validate https://example.org/path/to/file.json

# validate WMDR2 metadata against abstract test suite (URL), but turn JSON Schema validation off
pywmdr ets validate https://example.org/path/to/file.json --no-fail-on-schema-validation

# adjust debugging messages (CRITICAL, ERROR, WARNING, INFO, DEBUG) to stdout
pywmdr ets validate https://example.org/path/to/file.json --verbosity DEBUG

# write results to logfile
pywmdr ets validate https://example.org/path/to/file.json --verbosity DEBUG --logfile /tmp/foo.txt
```

## Using the API
```pycon
>>> # test a file on disk
>>> import json
>>> from pywmdr.wmdr2.ets import WIGOSMetadataRepresentationTestSuite2
>>> from pywmdr.errors import TestSuiteError
>>> with open('/path/to/file.json') as fh:
...     data = json.load(fh)
>>> # test ETS
>>> ts = WMOCoreMetadataProfileTestSuite2(datal)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pywmdr.errors.TestSuiteError on exception with list of errors captured in .errors property
>>> # test a URL
>>> from urllib2 import urlopen
>>> from StringIO import StringIO
>>> content = StringIO(urlopen('https://....').read())
>>> data = json.loads(content)
>>> ts = WMOCoreMetadataProfileTestSuite2(data)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pywmdr.errors.TestSuiteError on exception with list of errors captured in .errors property
```

## Development

```bash
python3 -m venv pywmdr
cd pywmdr
source bin/activate
git clone https://github.com/World-Meteorological-Organization/pywmdr.git
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 setup.py install
```

### Running tests

```bash
python3 tests/run_tests.py
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi pywmdr/__init__.py  # update __version__
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*

# publish release on GitHub (https://github.com/wmo-im/pywmdr/releases/new)

# bump version back to dev
vi pywmdr/__init__.py  # update __version__
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/wmo-im/pywmdr/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
