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

import click

from pywmdr.wmdr2.ets import WMDR2TestSuite
from pywmdr import cli_options
from pywmdr.util import parse_wmdr2, urlopen_


@click.group()
def ets():
    """executable test suite"""
    pass


@click.command()
@click.pass_context
@click.argument('file_or_url')
@cli_options.OPTION_VERBOSITY
def validate(ctx, file_or_url, verbosity):
    """validate WMDR2 record against the specification"""

    click.echo(f'Opening {file_or_url}')

    if file_or_url.startswith('http'):
        content = urlopen_(file_or_url).read()
    else:
        with open(file_or_url) as fh:
            content = fh.read()

    click.echo(f'Validating {file_or_url}')

    try:
        data = parse_wmdr2(content)
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    click.echo('Detected WMDR2 record')
    ts = WMDR2TestSuite(data)
    try:
        results = ts.run_tests()
    except Exception as err:
        raise click.ClickException(err)
        ctx.exit(1)

    click.echo(json.dumps(results, indent=4))
    ctx.exit(results['summary']['FAILED'])


ets.add_command(validate)
