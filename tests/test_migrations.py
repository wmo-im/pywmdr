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

from lxml import etree
import pytest

from pywmdr.migrations import Migration, xpath_
from .util import get_test_file_path


@pytest.mark.parametrize("xml, xpath, expected", [
    ('<root><foo>test</foo></root>', './/foo', 'test'),
    ('<root><foo/></root>', './/foo', None),
    ('<root><foo bar="attr">test</foo></root>', './/foo/@bar', 'attr'),
])
def test_xpath_(xml, xpath, expected):
    """Simple tests for testing XPath helper function"""

    node = etree.fromstring(xml)

    assert xpath_(node, xpath) == expected


@pytest.mark.parametrize("filename, wsi, facility_type, nobs", [
    ('0-12-0-10BRACN60417.xml', '0-12-0-10BRACN60417', 'landFixed', 23)
])
def test_wmdr1_to_wmdr2(filename, wsi, facility_type, nobs):
    """Simple tests for WMDR1 XML to WMDR2 migration"""

    with get_test_file_path(filename).open() as fh:
        data = fh.read()

    wmdr2 = Migration(data).migrate()

    assert wmdr2['id'] == wsi
    assert wmdr2['type'] == 'Feature'
    assert wmdr2['properties']['type'] == 'facility'
    assert wmdr2['properties']['facilityType']['id'] == facility_type
    assert len(wmdr2['properties']['observations']) == nobs
