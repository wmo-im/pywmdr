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

import pytest

from pywmdr.wmdr2.ets import WMDR2TestSuite

from .util import get_test_file_path


@pytest.mark.parametrize("filename, passed, failed, skipped, warnings_", [
    ('wmdr2-passing.json', 2, 0, 0, 0),
    ('wmdr2-failing-invalid.json', 1, 1, 0, 0),
    ('wmdr2-failing-codelisted-value.json', 1, 1, 0, 0)
])
def test_ets(filename, passed, failed, skipped, warnings_):
    """Simple tests for ETS validation"""

    with get_test_file_path(filename).open() as fh:
        data = json.load(fh)

    ts = WMDR2TestSuite(data)
    results = ts.run_tests()

    assert results['report_type'] == 'ets'
    assert results['metadata_id'] == data['id']

    codes = [r['code'] for r in results['tests']]

    assert codes.count('PASSED') == passed
    assert codes.count('FAILED') == failed
    assert codes.count('SKIPPED') == skipped
    assert codes.count('WARNINGS') == warnings_
