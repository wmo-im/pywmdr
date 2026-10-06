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

import datetime
import json
import logging
import re

from lxml import etree

import click

from pywmdr import cli_options
from pywmdr.util import urlopen_

LOGGER = logging.getLogger(__name__)

NAMESPACES = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gml': 'http://www.opengis.net/gml/3.2',
    'om': 'http://www.opengis.net/om/2.0',
    'wmdr': 'http://def.wmo.int/wmdr/2017',
    'xlink': 'http://www.w3.org/1999/xlink'
}


def xpath_(node: etree.Element, xpath: str) -> str | None:
    """
    Helper function to derive a value from an XPath

    :param node: `etree.Element`
    :param xpath: `str` of XPath expression

    :returns: `str` of matching XPath value or `None`
    """

    try:
        val = node.xpath(xpath, namespaces=NAMESPACES)[0]
        if hasattr(val, 'text'):  # node
            return val.text
        else:  # attribute
            return val
    except IndexError:
        return None


class Migration:
    def __init__(self, record: str):
        """
        Initializer

        :param record: `str` of WMDR1 XML record

        :returns: `pywmdr.migrations.Migration`
        """

        self.record = record
        self.warnings = []

    def migrate(self) -> dict:
        """
        Migrate a WMDR1 XML to WMDR2

        :returns: `dict` of WMDR2
        """

        created = datetime.datetime.now(datetime.UTC).strftime(
            '%Y-%m-%dT%H:%M:%SZ').replace('+00:00', 'Z')

        wmdr2 = {
            'id': None,
            'type': 'Feature',
            'conformsTo': ['http://wigos.wmo.int/spec/wmdr/2/conf/core'],
            'time': None,
            'geometry': None,
            'properties': {
                'type': 'facility',
                'created': created,
                'contacts': []
            },
            'links': []
        }

        if isinstance(self.record, str):
            record_ = self.record.encode('utf-8')
        elif isinstance(self.record, bytes):
            record_ = self.record

        tree = etree.fromstring(record_)

        facility = tree.xpath('//wmdr:facility', namespaces=NAMESPACES)[0]

        val = xpath_(facility, './/wmdr:ObservingFacility/gml:identifier')
        wmdr2['id'] = val

        val = xpath_(facility, './/wmdr:geospatialLocation//gml:Point/gml:pos')

        if val is not None:
            coordinates = [float(x) for x in val.split()]
            wmdr2['geometry'] = {
                'type': 'Point',
                'coordinates': [coordinates[1], coordinates[0]]
            }
            if len(coordinates) == 3:
                wmdr2['geometry']['coordinates'].append(coordinates[2])

        val = xpath_(facility, './/wmdr:ObservingFacility/gml:name')
        wmdr2['properties']['title'] = val

        val = xpath_(facility, './/wmdr:ObservingFacility/wmdr:description//wmdr:description')  # noqa
        if val is not None:
            wmdr2['properties']['description'] = val

        val = xpath_(facility, './/wmdr:facilityType/@xlink:href')
        wmdr2['properties']['facilityType'] = {
            'id': val.split('/')[-1],
            'url': val
        }

        val = xpath_(facility, './/wmdr:wmoRegion/@xlink:href')
        if val is not None:
            wmdr2['properties']['wmoRegion'] = {
                'id': val.split('/')[-1],
                'url': val
            }
        else:
            wmdr2['properties']['wmoRegion'] = {
                'id': 'unknown',
                'url': 'http://codes.wmo.int/wmdr/WMORegion/unknown'
            }

        val = xpath_(facility, './/wmdr:dateEstablished')
        wmdr2['time'] = {
            'interval': [val]
        }

        val = xpath_(facility, './/wmdr:dateClosed')
        if val is not None:
            wmdr2['time']['interval'].append(val)
        else:
            wmdr2['time']['interval'].append('..')

        for ci_rp in tree.xpath('//gmd:CI_ResponsibleParty', namespaces=NAMESPACES):  # noqa
            contact2 = self.ci_responsibleparty_to_contact(ci_rp)
            if contact2 is not None:
                wmdr2['properties']['contacts'].append(contact2)

        if not wmdr2['properties']['contacts']:
            wmdr2['properties'].pop('contacts')
            if contact2 is not None:
                wmdr2['properties']['contacts'].append(contact2)

        for link in facility.xpath('.//wmdr:onlineResource//gmd:URL', namespaces=NAMESPACES):  # noqa
            wmdr2['links'].append({
                'rel': 'related',
                'href': link.text
            })

        territories = tree.xpath('//wmdr:territory', namespaces=NAMESPACES)
        if territories:
            wmdr2['properties']['territories'] = []
            for territory in territories:
                territory_ = {}
                territory_name = xpath_(
                    territory, './/wmdr:territoryName/@xlink:href')

                if territory_name is not None:
                    territory_['territory'] = {
                        'id': territory_name.split('/')[-1],
                        'url': territory_name
                    }
                    begin = xpath_(
                        territory, './/wmdr:validPeriod//gml:beginPosition')

                    territory_['dates'] = [begin]

                    end = xpath_(territory, './/wmdr:validPeriod//gml:endPosition')  # noqa

                    if end is None:
                        territory_['dates'].append('..')
                    else:
                        territory_['dates'].append(end)
                    wmdr2['properties']['territories'].append(territory_)

        observations = tree.xpath('//wmdr:observation/wmdr:ObservingCapability', namespaces=NAMESPACES)  # noqa

        if observations:
            wmdr2['properties']['observations'] = []

            for observation in observations:
                observation_ = {
                    'programAffiliations': [],
                    'configurations': []
                }
                observed_geometry = xpath_(
                    observation, './/om:type/@xlink:href')

                if observed_geometry is not None:
                    observation_['observedGeometry'] = {
                        'id': observed_geometry.split('/')[-1],
                        'url': observed_geometry
                    }

                observed_property = xpath_(
                    observation, './/om:observedProperty/@xlink:href')

                observation_['observedProperty'] = {
                    'id': observed_property.split('/')[-1],
                    'url': observed_property
                }

                program_affiliations = observation.xpath(
                    './wmdr:programAffiliation/@xlink:href',
                    namespaces=NAMESPACES)
                if program_affiliations:
                    for program_affiliation in program_affiliations:
                        observation_['programAffiliations'].append({
                            'programAffiliation': {
                                'id': program_affiliation.split('/')[-1],
                                'url': program_affiliation
                             }})

                deployments = observation.xpath(
                    './/wmdr:Deployment', namespaces=NAMESPACES)

                for deployment in deployments:
                    configuration_ = {
                        'id': None,
                        'time': {
                            'interval': []
                        }
                    }
                    configuration_['id'] = xpath_(deployment, './/@gml:id')

                    begin = xpath_(
                        deployment, './/wmdr:validPeriod//gml:beginPosition')

                    configuration_['time']['interval'].append(begin)

                    end = xpath_(
                        deployment, './/wmdr:validPeriod//gml:endPosition')

                    if end is None:
                        configuration_['time']['interval'].append('..')
                    else:
                        configuration_['time']['interval'].append(end)

                    observing_method = xpath_(
                        deployment, './/wmdr:observingMethod/@xlink:href')
                    if observing_method is not None:
                        configuration_['observingMethod'] = {
                            'id': observing_method.split('/')[-1],
                            'url': observing_method
                        }

                    observation_['configurations'].append(configuration_)

                if not observation_['configurations']:
                    msg = f"No configurations found for observation ({observation_['observedProperty']['url']})"  # noqa
                    self.warnings.append(msg)
                    observation_.pop('configurations')

                wmdr2['properties']['observations'].append(observation_)

        wmdr2['links'].append({
            'rel': 'original',
            'type': 'application/xml',
            'title': f"{wmdr2['properties']['title']} as WMDR1",
            'href': f"https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier={wmdr2['id']}"  # noqa
        })

        return wmdr2


    def ci_responsibleparty_to_contact(self, node: etree.Element) -> tuple[dict, list[str]]:  # noqa
        """
        Helper function to transform ISO gmd:CI_ResponsibleParty to a
        WMDR2 contact

        :param node: `etree.Element` of gmd:CI_ResponsibleParty

        :returns: `dict` of WMDR2 contact object, or `None`
        """

        val = None
        contact = {}

        val = xpath_(node, './/gmd:role/gmd:CI_RoleCode/@codeListValue')
        if val is None:
            LOGGER.debug('No role found; skipping')
            return
        else:
            contact['roles'] = [val]

        val = xpath_(node, './/gmd:individualName/gco:CharacterString')
        if val is not None:
            contact['name'] = val

        val = xpath_(node, './/gmd:organisationName/gco:CharacterString')
        if val is not None:
            contact['organization'] = val

        phones = node.xpath('.//gmd:voice/gco:CharacterString',
                            namespaces=NAMESPACES)
        if phones:
            contact['phones'] = []
            for phone in phones:
                contact['phones'].append({'value': phone.text})

        emails = node.xpath('.//gmd:electronicMailAddress/gco:CharacterString',
                            namespaces=NAMESPACES)
        if emails:
            contact['emails'] = []
            for email in emails:
                # validate we have email address
                # (something at something dot something, no white space)
                email_valid = re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email.text) is not None  # noqa
                email_address = email.text.strip()
                if not email_valid:
                    msg = f'Invalid email: {email_address}'
                    self.warnings.append(msg)
                contact['emails'].append({'value': email_address})

        val = xpath_(node, './/gmd:contactInstructions/gco:CharacterString')
        if val is not None:
            contact['contactInstructions'] = val

        try:
            val = node.xpath('.//gmd:address', namespaces=NAMESPACES)[0]
        except IndexError:
            val = None

        if val is not None:
            address = {}

            val2 = xpath_(val, './/gmd:deliveryPoint/gco:CharacterString')
            if val2 is not None:
                address['deliveryPoint'] = [val2]

            val2 = xpath_(val, './/gmd:city/gco:CharacterString')
            if val2 is not None:
                address['city'] = val2

            val2 = xpath_(val, './/gmd:postalCode/gco:CharacterString')
            if val2 is not None:
                address['postalCode'] = val2

            val2 = xpath_(val, './/gmd:country/gco:CharacterString')
            if val2 is not None:
                address['country'] = val2

            val2 = xpath_(val, './/gmd:onlineResource//gmd:URL')
            if val2 is not None:
                address['links'] = [{
                    'href': val2
                }]

            if address:
                contact['addresses'] = [address]

        return contact


@click.command()
@click.pass_context
@click.argument('file_or_url')
@cli_options.OPTION_OUTPUT
@cli_options.OPTION_VERBOSITY
def migrate(ctx, file_or_url, output, verbosity):
    """migrate a WMDR1 record to WMDR2 core"""

    click.echo(f'Opening {file_or_url}')

    if file_or_url.startswith('http'):
        content = urlopen_(file_or_url).read()
    else:
        with open(file_or_url) as fh:
            content = fh.read()

    click.echo(f'Migrating {file_or_url} from WMDR1 to WMDR2')

    try:
        m = Migration(content)
        content = m.migrate()
        if output is not None:
            json.dump(content, output, indent=4)
        else:
            click.echo(json.dumps(content, indent=4))

        if m.warnings:
            click.echo('\nWARNINGS:')
            for w in m.warnings:
                click.echo(f'- {w}')
    except Exception as err:
        import traceback
        print(traceback.format_exc())
        raise click.ClickException(err)
        ctx.exit(1)
