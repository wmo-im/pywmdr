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
import logging

from pywmdr.util import get_userdir

LOGGER = logging.getLogger(__name__)

CODELISTS_MAP = {
    'facilityType': {
        'codelists': ['FacilityType.csv']
    },
    'wmoRegion': {
        'codelists': ['WMORegion.csv']
    },
    'territory': {
        'codelists': ['TerritoryName.csv']
    },
    'observedGeometry': {
        'codelists': ['Geometry.csv']
    },
    'observedProperty': {
        'codelists': [
            'ObservedVariableAtmosphere.csv',
            'ObservedVariableEarth.csv',
            'ObservedVariableOcean.csv',
            'ObservedVariableOuterSpace.csv',
            'ObservedVariableTerrestrial.csv'
        ]
    },
    'programAffiliation': {
        'codelists': ['ProgramAffiliation.csv']
    },
    'reportingStatus': {
        'codelists': ['ReportingStatus.csv']
    },
    'observingMethod': {
        'codelists': [
            'ObservingMethodAtmosphere.csv',
            'ObservingMethodTerrestrial.csv',
            'ObservingMethodOcean.csv'
        ]
    },
    'operatingStatus': {
        'codelists': ['InstrumentOperatingStatus.csv']
    },
    'sourceOfObservation': {
        'codelists': ['SourceOfObservation.csv']
    },
    'referenceSurface': {
        'codelists': ['ReferenceSurfaceType.csv']
    },
    'unit': {
        'codelists': ['unit.csv']
    },
}


class WMDSCodelists:
    def __init__(self):
        """initializer"""

        self.codelists = {}
        for key, value in CODELISTS_MAP.items():
            self.codelists[key] = []
            for codelist in value['codelists']:
                filename = get_userdir() / 'wmds' / codelist
                with filename.open() as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        self.codelists[key].append(row['@notation'])

    def __repr__(self):
        return '<WMDSCodelists>'
