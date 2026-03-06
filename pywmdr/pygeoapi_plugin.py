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

#
# pywmdr as a service
# -------------------
#
# This file is intended to be used as a pygeoapi process plugin which will
# provide pywmdr functionality via OGC API - Processes.
#
# To integrate this plugin in pygeoapi:
#
# 1. ensure pywmdr is installed into the pygeoapi deployment environment
#
# 2. add the processes to the pygeoapi configuration as follows:
#
# pywmdr-record-validate:
#     type: process
#     processor:
#         name: pywmdr.pygeoapi_plugin.WMDR2ETSProcessor
#
# 3. (re)start pygeoapi
#
# The resulting processes will be available at the following endpoints:
#
# /processes/pywmdr-record-validate
#
# Note that pygeoapi's OpenAPI/Swagger interface (at /openapi) will also
# provide a developer-friendly interface to test and run requests
#

import json
import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError

from pywmdr.wmdr2.ets import WMDR2TestSuite
from pywmdr.util import get_package_version, THISDIR, urlopen_

LOGGER = logging.getLogger(__name__)

with (THISDIR / 'resources' / 'ets-report.json').open() as fh:
    ETS_REPORT_SCHEMA = json.load(fh)

with (THISDIR / 'resources' / '20250504_0-20008-0-NRB.json').open() as fh:
    EXAMPLE_WMDR2 = json.load(fh)


PROCESS_WMDR2_ETS = {
    'version': get_package_version(),
    'id': 'pywmdr-record-validate',
    'title': {
        'en': 'WMDR2 record validator'
    },
    'description': {
        'en': 'Validate a WMDR2 record against the ETS'
    },
    'keywords': ['wigos', 'wmdr2', 'ets', 'test suite', 'metadata'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://github.com/wmo-im/wmdr2',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'record': {
            'title': 'WMDR2 record',
            'description': 'WMDR2 record (can be inline or remote link)',
            'schema': {
                'type': ['object', 'string']
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['wmdr2']
        }
    },
    'outputs': {
        'result': {
            'title': 'Report of ETS results',
            'description': 'Report of ETS results',
            'schema': {
                'contentMediaType': 'application/json',
                **ETS_REPORT_SCHEMA
            }
        }
    },
    'example': {
        'inputs': {
            'record': EXAMPLE_WMDR2
        }
    }
}


class WMDR2ETSProcessor(BaseProcessor):
    """WMDR2 ETS"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pywmdr.pygeoapi_plugin.WMDR2ETSProcessor
        """

        super().__init__(processor_def, PROCESS_WMDR2_ETS)

    def execute(self, data, outputs=None):

        response = None
        mimetype = 'application/json'
        record = data.get('record')

        if record is None:
            msg = 'Missing record'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        if isinstance(record, str) and record.startswith('http'):
            LOGGER.debug('Record is a link')
            record = json.loads(urlopen_(record).read())
        else:
            LOGGER.debug('Record is inline')

        LOGGER.debug('Running ETS against record')
        response = WMDR2TestSuite(record).run_tests()

        return mimetype, response

    def __repr__(self):
        return '<WMDR2ETSProcessor>'
