##############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import csv
import io
import logging
from pathlib import Path
import shutil
import tempfile

import click

from pywmdr import cli_options
from pywmdr.util import get_userdir, urlopen_

LOGGER = logging.getLogger(__name__)

USERDIR = get_userdir()

TEMPDIR = tempfile.TemporaryDirectory()
TEMPDIR2 = Path(tempfile.TemporaryDirectory().name)

WMDR2_FILES = get_userdir() / 'wmdr2'
WMDR2_FILES_TEMP = TEMPDIR2 / 'wmdr2'
WMDS_DIR = get_userdir() / 'wmds'
WMDS_DIR_TEMP = TEMPDIR2 / 'wmds'


@click.group()
def bundle():
    """Configuration bundle management"""
    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def sync(ctx, verbosity):
    """Sync configuration bundle"""

    LOGGER.debug('Caching schema')
    LOGGER.debug(f'Downloading WMDR2 schema to {WMDR2_FILES_TEMP}')
    WMDR2_FILES_TEMP.mkdir(parents=True, exist_ok=True)
    WMDR2_SCHEMA = 'https://raw.githubusercontent.com/wmo-im/wmdr2/refs/heads/main/schemas/wmdr2-bundled.json'  # noqa

    json_schema = WMDR2_FILES_TEMP / 'wmdr2-bundled.json'
    with json_schema.open('wb') as fh:
        fh.write(urlopen_(f'{WMDR2_SCHEMA}').read())

    LOGGER.debug('Caching codelists')
    LOGGER.debug(f'Downloading WMDS codelists to {WMDS_DIR_TEMP}')
    WMDS_DIR_TEMP.mkdir(parents=True, exist_ok=True)
    WMDS_CODELISTS_LIST = 'https://codes.wmo.int/wmdr?_format=csv&_view=with_metadata&status=valid'  # noqa
    codelists = urlopen_(WMDS_CODELISTS_LIST).read().decode('utf-8')
    codelists_fh = io.StringIO(codelists.strip())
    reader = csv.reader(codelists_fh)
    for row in reader:
        codelist_url = f'https://codes.wmo.int/wmdr/{row[1]}?_format=csv&_view=with_metadata&status=valid'  # noqa
        LOGGER.debug(f'Downloading {codelist_url}')
        codelist_file = WMDS_DIR_TEMP / f'{row[1]}.csv'
        LOGGER.debug(f'Writing codelist {codelist_file}')
        with codelist_file.open('wb') as fh:
            fh.write(urlopen_(codelist_url).read())

    LOGGER.debug(f'Removing {USERDIR}')
    if USERDIR.exists():
        shutil.rmtree(USERDIR)

    LOGGER.debug(f'Moving files from {TEMPDIR2} to {USERDIR}')
    shutil.move(TEMPDIR2, USERDIR)

    LOGGER.debug(f'Cleaning up {TEMPDIR}')
    TEMPDIR.cleanup()


bundle.add_command(sync)
