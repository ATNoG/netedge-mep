########################################################################
# This file serves the purpose to validate POST/PUT/PATCH HTTP METHODS #
# from a mec app. These schemas are json schemas that represent valid  #
# inputs that a mec app can execute                                    #
########################################################################
linktype_schema = {

    "type" : "object",
    "properties" : {
        "href" : {"type" : "string"},
    },
    "required":["href"]
}

subscription_schema = {
    "type" : "object",
    "properties": {
        "href": {"type":"string"},
        "subscriptionType":{"type":"string"}
    },
    "required":["href","subscriptionType"]
}

links_schema = {
    "type" : "object",
    "properties":{
        "self": linktype_schema,
        "subscriptions": {"type":"array","items":subscription_schema},
        "liveness":linktype_schema
    },
    "required":["self"]
}

mecservicemgmtapisubscriptionlinklist_schema = {
    "type" : "object",
    "properties":{
        "_links":links_schema
    },
    "required": ["_links"]
}

categoryref_schema = {
    "type":"object",
    "properties":{
        "href":{"type":"string"},
        "id":{"type":"string"},
        "name":{"type":"string"},
        "version":{"type":"string"}
    },
    "required":["href","id","name","version"]
}

filteringcriteria_schema = {
    "type":"object",
    "properties":{
        "state":{"enum":["ACTIVE","INACTIVE"]},
        "isLocal":{"type":"boolean"},
        "serInstanceId":{"type":"string"},
        "serName":{"type":"string"},
        "serCategory":categoryref_schema
    },
}

seravailabilitynotificationsubscription_schema = {
    "type":"object",
    "properties":{
        "callbackReference":{"type":"string"},
        "_links":links_schema,
        "filteringCriteria":filteringcriteria_schema,
        "subscriptionType":{"type":"string"}
    },
    "required":["callbackReference","subscriptionType"]
}
oauth2info_schema = {
    "type":"object",
    "properties":{
        "grantTypes":{"type":"array",
                      "items":{"enum":["OAUTH2_AUTHORIZATION_CODE","OAUTH2_IMPLICIT_GRANT",
                                                       "OAUTH2_RESOURCE_OWNER","OAUTH2_CLIENT_CREDENTIALS"]
                               },
                      "uniqueItems": True,
                      "minItems":1,
                      "maxItems":4
                      },
        "tokenEndpoint": {"type":"string"}
    },
    "required":["grantTypes"]
}

securityinfo_schema = {
    "type":"object",
    "properties":{
        "oAuth2Info":oauth2info_schema
    },
    "required":["oAuth2Info"]
}

endpointinfo_address_schema = {
    "type":"object",
    "properties":{
        "host":{"type":"string"},
        "port":{"type":"integer"}
    },
    "required":["host","port"]
}
endpointinfo_addresses_schema = {
    "type":"object",
    "properties":{
        "addresses":{"type":"array",
                     "items":endpointinfo_address_schema,
                     "minItems":1}
    },
    "required":["addresses"]
}

endpointinfo_uris_schema = {
    "type":"object",
    "properties":{
        "uris":{"type":"array",
                "items":
                    {"type":"string"
                     },
                "minItems":1
                }
    },
    "required":["uris"]
}

implSpecificInfo_schema = {
    "type":"object",
    "properties":
        {"description":{"type":"string"}
        }
}

transportinfo_schema = {
    "type":"object",
    "properties":{
        "id":{"type":"string"},
        "name":{"type":"string"},
        "type:":{"enum":["REST_HTTP","MB_TOPIC_BASED","MB_ROUTING","MB_PUBSUB","RPC","RPC_STREAMING","WEBSOCKET"]},
        "version":{"type":"string"},
        "endpoint":{"oneOf":[endpointinfo_addresses_schema,endpointinfo_uris_schema]},
        "security":securityinfo_schema,
        "description":{"type":"string"},
        "implSpecificInfo":implSpecificInfo_schema,
        "protocol":{"type":"string"}
    },
    "required":["id","name","type","protocol","version","endpoint","security"]
}

serviceinfo_schema = {
    "type":"object",
    "properties":{
        "version":{"type":"string"},
        "transportInfo":transportinfo_schema,
        "serializer":{"enum":["JSON","XML","PROTOBUF3"]},
        "_links":links_schema,
        "livenessInterval":{"type":"integer"},
        "consumedLocalOnly":{"type":"boolean"},
        "isLocal":{"type":"boolean"},
        "scopeOfLocality":{"enum":["MEC_SYSTEM","MEC_HOST","NFVI_POP","ZONE","ZONE_GROUP","NFVI_NODE"]},
        "serInstanceId":{"type":"string"},
        "serName":{"type":"string"},
        "serCategory":categoryref_schema
    },
    "oneOf":[{"required":["serInstanceId"]},{"required":["serName"]},{"required":["serCategory"]}],
    "required":["version","state","serializer","_links"]
}