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

from datetime import datetime, timezone
import importlib.metadata
import json
import logging
from pathlib import Path
import ssl
from urllib.error import URLError
from urllib.request import urlopen

LOGGER = logging.getLogger(__name__)

THISDIR = Path(__file__).parent.resolve()


def get_current_datetime_rfc3339() -> str:
    """
    Gets the current datetime in RFC3339 format

    :returns: `str` of RFC3339
    """

    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def get_userdir() -> str:
    """
    Helper function to get userdir

    :returns: user's home directory
    """

    return Path.home() / '.pywmdr'


def get_package_version() -> str:
    """
    Helper function to get package version

    :returns: `str` of version of package
    """

    return importlib.metadata.version('pywmdr')


def parse_wmdr2(content: str) -> dict:
    """
    Parse a string of WMDR2 JSON into a dict

    :param content: `str` of JSON

    :returns: `dict` object of WMDR2
    """

    LOGGER.debug('Attempting to parse as JSON')
    try:
        data = json.loads(content)
    except json.decoder.JSONDecodeError as err:
        LOGGER.error(err)
        raise RuntimeError(f'Encoding error: {err}')

    return data


def urlopen_(url: str):
    """
    Helper function for downloading a URL

    :param url: URL to download

    :returns: `http.client.HTTPResponse`
    """

    try:
        response = urlopen(url)
    except (ssl.SSLError, URLError) as err:
        LOGGER.warning(err)
        LOGGER.warning('Creating unverified context')
        context = ssl._create_unverified_context()

        response = urlopen(url, context=context)

    return response
