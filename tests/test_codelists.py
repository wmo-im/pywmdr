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

import pytest

from pywmdr.codelists import WMDSCodelists


@pytest.mark.parametrize("pname, pvalue, expected, raise_", [
    ('unit', {'id': 'metres'}, False, False),
    ('unit', None, True, False),
    ('iunit', {'id': 'metres'}, False, True),
    ('programAffiliation', {'id': 'GBON'}, True, False),
    ('programAffiliation', {'id': '404'}, False, False)
])
def test_codelists_is_valid(pname, pvalue, expected, raise_):
    """Simple tests for testing codelist value validity"""

    codelists = WMDSCodelists()

    if raise_:
        with pytest.raises(ValueError):
            assert codelists.is_valid(pname, pvalue)
    elif expected:
        assert codelists.is_valid(pname, pvalue)
    else:
        assert not codelists.is_valid(pname, pvalue)
