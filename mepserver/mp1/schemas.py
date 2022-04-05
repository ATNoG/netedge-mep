# Copyright 2022 Instituto de Telecomunicações - Aveiro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


########################################################################
# This file serves the purpose to validate POST/PUT/PATCH HTTP METHODS #
# from a mec app. These schemas are json schemas that represent valid  #
# inputs that a mec app can execute                                    #
########################################################################
linktype_schema = {
    "type": "object",
    "properties": {
        "href": {"type": "string"},
    },
    "required": ["href"],
    "additionalProperties": False
}

subscription_schema = {
    "type": "object",
    "properties": {"href": {"type": "string"}, "subscriptionType": {"type": "string"}},
    "required": ["href"],
    "additionalProperties": False
}

links_schema = {
    "type": "object",
    "properties": {
        "self": linktype_schema,
        "subscriptions": {"type": "array", "items": subscription_schema},
        "liveness": linktype_schema,
    },
    "required": ["self"],
    "additionalProperties": False
}

mecservicemgmtapisubscriptionlinklist_schema = {
    "type": "object",
    "properties": {"_links": links_schema},
    "required": ["_links"],
    "additionalProperties": False
}

categoryref_schema = {
    "type": "object",
    "properties": {
        "href": {"type": "string"},
        "id": {"type": "string"},
        "name": {"type": "string"},
        "version": {"type": "string"},
    },
    "required": ["href", "id", "name", "version"],
    "additionalProperties": False
}

# This approach is weird but "additionalProperties" wasn't cutting it and neither was required which forced
# one of the mutually exclusive but not required methods to be present
# the dependentschema might also fix this issue should be, if time allows, checked in the future

filteringcriteria_schema = {
    "type": "object",
    "properties": {
        "states": {"type":"array","items":{"type":"string","enum": ["ACTIVE", "INACTIVE","SUSPENDED"]}},
        "isLocal": {"type": "boolean"},
        "serNames": {"type":"array","items":{"type":"string"}},
        "serInstanceIds": {"type":"array","items":{"type":"string"}},
        "serCategories":{"type":"array","items":categoryref_schema}
    },
    "oneOf":[ {"not": {"anyOf":[
                            {"required":["serNames",
                                         "serInstancesId",
                                         "serCategories"]
                            },
                            ]}},
            {"required":["serNames","serInstanceIds","serCategories"]},
            ],
    "additionalProperties": False
}


seravailabilitynotificationsubscription_schema = {
    "type": "object",
    "properties": {
        "callbackReference": {"type": "string"},
        "filteringCriteria": filteringcriteria_schema,
        "subscriptionType": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["callbackReference", "subscriptionType"],
}
oauth2info_schema = {
    "type": "object",
    "properties": {
        "grantTypes": {
            "type": "array",
            "items": {
                "enum": [
                    "OAUTH2_AUTHORIZATION_CODE",
                    "OAUTH2_IMPLICIT_GRANT",
                    "OAUTH2_RESOURCE_OWNER",
                    "OAUTH2_CLIENT_CREDENTIALS",
                ]
            },
            "uniqueItems": True,
            "minItems": 1,
            "maxItems": 4,
        },
        "tokenEndpoint": {"type": "string"},
    },
    "required": ["grantTypes"],
    "additionalProperties": False
}

securityinfo_schema = {
    "type": "object",
    "properties": {"oAuth2Info": oauth2info_schema},
    "required": ["oAuth2Info"],
    "additionalProperties": False
}

endpointinfo_address_schema = {
    "type": "object",
    "properties": {"host": {"type": "string"}, "port": {"type": "integer"}},
    "required": ["host", "port"],
    "additionalProperties": False
}
endpointinfo_addresses_schema = {
    "type": "object",
    "properties": {
        "addresses": {
            "type": "array",
            "items": endpointinfo_address_schema,
            "minItems": 1,
        }
    },
    "required": ["addresses"],
    "additionalProperties": False
}

endpointinfo_uris_schema = {
    "type": "object",
    "properties": {
        "uris": {"type": "array", "items": {"type": "string"}, "minItems": 1}
    },
    "required": ["uris"],
    "additionalProperties": False
}

implSpecificInfo_schema = {
    "type": "object",
    "properties": {"description": {"type": "string"}},
    "additionalProperties": False
}

transportinfo_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "type": {
            "enum": [
                "REST_HTTP",
                "MB_TOPIC_BASED",
                "MB_ROUTING",
                "MB_PUBSUB",
                "RPC",
                "RPC_STREAMING",
                "WEBSOCKET",
            ]
        },
        "version": {"type": "string"},
        "endpoint": {
            "oneOf": [endpointinfo_addresses_schema, endpointinfo_uris_schema]
        },
        "security": securityinfo_schema,
        "description": {"type": "string"},
        "implSpecificInfo": implSpecificInfo_schema,
        "protocol": {"type": "string"},
    },
    "required": ["id", "name", "type", "protocol", "version", "endpoint", "security"],
    "additionalProperties": False
}

serviceinfo_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "transportInfo": transportinfo_schema,
        "serializer": {"enum": ["JSON", "XML", "PROTOBUF3"]},
        "livenessInterval": {"type": "integer"},
        "consumedLocalOnly": {"type": "boolean"},
        "isLocal": {"type": "boolean"},
        "scopeOfLocality": {
            "enum": [
                "MEC_SYSTEM",
                "MEC_HOST",
                "NFVI_POP",
                "ZONE",
                "ZONE_GROUP",
                "NFVI_NODE",
            ]
        },
        "state": {"enum":["ACTIVE","INACTIVE","SUSPENDED"]},
        "serName": {"type": "string"},
        "serCategory": categoryref_schema,
    },
    "required": ["version", "state", "serializer","serName"],
    "additionalProperties": False
}

appreadyconfirmation_schema = {
    "type": "object",
    "properties": {"indication": {"type": "string"}},
    "required": ["indication"],
    "additionalProperties": False
}

appterminationconfirmation_schema = {
    "type": "object",
    "properties": {"operationAction": {"type": "string"}},
    "required": ["operationAction"],
    "additionalProperties": False
}
