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

import json
import logging
import uuid

from jsonschema import FormatChecker
from jsonschema.validators import Draft202012Validator

from pywmdr.bundle import WMDR2_FILES
from pywmdr.errors import TestSuiteError
from pywmdr.util import get_current_datetime_rfc3339, get_package_version

LOGGER = logging.getLogger(__name__)


def gen_test_id(test_id: str) -> str:
    """
    Convenience function to print test identifier as URI

    :param test_id: test suite identifier

    :returns: test identifier as URI
    """

    return f'http://wis.wmo.int/spec/wmdr/2/conf/core/{test_id}'


class WMDR2TestSuite:
    def __init__(self, record):
        """
        initializer

        :param data: dict of WMDR2 JSON

        :returns: `pywmdr.wmdr2.ets.WMDR2TestSuite`
        """

        self.version = get_package_version()
        self.errors = []
        self.record = record

    def run_tests(self):

        results = []
        tests = []

        ets_report = {
            'id': str(uuid.uuid4()),
            'report_type': 'ets',
            'summary': {
                'PASSED': 0,
                'FAILED': 0,
                'SKIPPED': 0,
                'WARNINGS': 0
            },
            'generated_by': f'pywmdr {self.version} (https://github.com/wmo-im/pywmdr)'  # noqa
        }

        for f in dir(WMDR2TestSuite):
            if all([callable(getattr(WMDR2TestSuite, f)),
                    f.startswith('test_requirement'),
                    not f.endswith('validation')]):
                tests.append(f)

        LOGGER.debug('Running schema validation')
        result = self.test_requirement_validation()
        results.append(result)
        if result['code'] == 'FAILED':
            self.errors.append(result)

        for t in tests:
            result = getattr(self, t)()
            results.append(result)
            if result['code'] == 'FAILED':
                self.errors.append(result)

        for code in ['PASSED', 'FAILED', 'SKIPPED', 'WARNINGS']:
            r = len([t for t in results if t['code'] == code])
            ets_report['summary'][code] = r

        ets_report['tests'] = results
        ets_report['datetime'] = get_current_datetime_rfc3339()
        ets_report['metadata_id'] = self.record['id']

        return ets_report

    def test_requirement_validation(self):
        """
        Validate that an WMDR2 record is valid to the authoritative schema.
        """

        validation_errors = []

        format_checkers = ['date-time', 'email', 'regex',
                           'uri', 'uri-reference']

        status = {
            'id': gen_test_id('validation'),
            'code': 'PASSED'
        }

        schema = WMDR2_FILES / 'wmdr2-bundled.json'

        if not schema.exists():
            msg = "WMDR2 schema missing. Run 'pywmdr bundle sync' to cache"
            LOGGER.error(msg)
            raise RuntimeError(msg)

        with schema.open() as fh:
            LOGGER.debug(f'Validating {self.record} against {schema}')
            validator = Draft202012Validator(
                json.load(fh),
                format_checker=FormatChecker(formats=format_checkers)
            )

            for error in validator.iter_errors(self.record):
                LOGGER.debug(f'{error.json_path}: {error.message}')
                validation_errors.append(f'{error.json_path}: {error.message}')

            if validation_errors:
                status['code'] = 'FAILED'
                status['message'] = f'{len(validation_errors)} error(s)'
                status['errors'] = validation_errors

        return status

    def raise_for_status(self):
        """
        Raise error if one or more failures were found during validation.

        :returns: `pywmdr.errors.TestSuiteError` or `None`
        """

        if len(self.errors) > 0:
            raise TestSuiteError('Invalid WMDR2 record', self.errors)
