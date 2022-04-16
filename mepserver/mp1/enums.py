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

from enum import Enum


class ServiceState(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class SerializerType(Enum):
    JSON = "JSON"
    XML = "XML"
    PROTOBUF3 = "PROTOBUF3"


class LocalityType(Enum):
    MEC_SYSTEM = "MEC_SYSTEM"
    MEC_HOST = "MEC_HOST"
    NFVI_POP = "NFVI_POP"
    ZONE = "ZONE"
    ZONE_GROUP = "ZONE_GROUP"
    NFVI_NODE = "NFVI_NODE"


class TransportType(Enum):
    REST_HTTP = "REST_HTTP"
    MB_TOPIC_BASED = "MB_TOPIC_BASED"
    MB_ROUTING = "MB_ROUTING"
    MB_PUBSUB = "MB_PUBSUB"
    RPC = "RPC"
    RPC_STREAMING = "RPC_STREAMING"
    WEBSOCKET = "WEBSOCKET"


class GrantTypes(Enum):
    OAUTH2_AUTHORIZATION_CODE = "OAUTH2_AUTHORIZATION_CODE"
    OAUTH2_IMPLICIT_GRANT = "OAUTH2_IMPLICIT_GRANT"
    OAUTH2_RESOURCE_OWNER = "OAUTH2_RESOURCE_OWNER"
    OAUTH2_CLIENT_CREDENTIALS = "OAUTH2_CLIENT_CREDENTIALS"


class IndicationType(Enum):
    READY = "READY"


class OperationActionType(Enum):
    STOPPING = "STOPPING"
    TERMINATING = "TERMINATING"
