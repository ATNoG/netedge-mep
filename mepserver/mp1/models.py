from __future__ import annotations
from typing import List

import cherrypy

from .utils import *
from .enums import *
import json

####################################
# Classes used by both support and #
# management api                   #
####################################
class LinkType:
    """
    This type represents a type of link and may be referenced from data structures.

    Raises TypeError

    Section 6.3.2 - MEC 011
    """
    def __init__(self,href):
        self.href = validate_uri(href)

    def to_json(self):
        return dict(href=self.href)

class ProblemDetails:
    def __init__(self, type: str, title: str, status: int, detail: str, instance: str):
        """
        :param type: A URI reference according to IETF RFC 3986 that identifies the problem type
        :param title: A short, human-readable summary of the problem type
        :param status: The HTTP status code for this occurrence of the problem
        :param detail: A human-readable explanation specific to this occurrence of the problem
        :param instance: A URI reference that identifies the specific occurrence of the problem
        """
        self.type = type
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance

####################################
# Classes used by management api   #
####################################
class Subscription:
    """
    The MEC application instance's subscriptions.

    Section 6.2.2
    """
    def __init__(self, href: str, subscriptionType: str):
        """
        :param href: URI referring to the subscription.
        :type href: str (String is validated to be a correct URI)
        :param subscriptionType: Type of the subscription.
        :type subscriptionType: str

        Raises TypeError
        """
        self.href = validate_uri(href)
        self.subscriptionType = subscriptionType

    def to_json(self):
        return dict(href=self.href,
                    subscriptionType=self.subscriptionType)
class Links:
    """
    Internal structure to be compliant with MEC 011

    Section 6.2.2
    """

    def __init__(self, _self: LinkType, subscriptions: List[Subscription]):
        self.self = _self
        self.subscriptions = subscriptions

    @staticmethod
    def from_json(data: dict) -> Links:
        _self = LinkType(data["_self"]["href"])

        subscriptions = [Subscription(**subscription) for subscription in data["subscriptions"]]

        return Links(_self=_self,
                     subscriptions=subscriptions)

    def to_json(self):
        return dict(self=self.self,subscriptions=self.subscriptions)

class MecServiceMgmtApiSubscriptionLinkList:
    """
    This type represents a list of links related to currently existing subscriptions for a MEC application instance. This information is returned when sending a request to receive current subscriptions.

    Section 6.2.2 - MEC 011
    """
    def __init__(self,_links: Links):
        self._links = _links

class CategoryRef:

    def __init__(self, href: str, id: str, name: str, version: str):
        """
        This type represents the category reference.

        :param href: Reference of the catalogue.
        :type href: String
        :param id: Unique identifier of the category.
        :type id: String
        :param name: Name of the category.
        :type name: String
        :param version: Category version.
        :type version: String

        Raises TypeError

        Section 8.1.5.2
        """
        self.href = validate_uri(href)
        self.id = id
        self.name = name
        self.version = version

class FilteringCriteria:
    def __init__(self, states: List[ServiceState], isLocal: bool, serInstanceId: List[str] = None, serNames: List[str] = None, serCategories: List[CategoryRef] = None):
        """
        :param states: States of the services about which to report events. If the event is a state change, this filter represents the state after the change
        :type states: List[ServiceState]
        :param isLocal: Restrict event reporting to whether the service is local to the MEC platform where the subscription is managed.
        :type isLocal: Boolean
        :param serInstanceId: Identifiers of service instances about which to report events
        :type serInstanceId: String
        :param serNames: Names of services about which to report events
        :type serNames: String
        :param serCategories: Categories of services about which to report events.
        :type serCategories: List of CategoryRef

        Note serCategories, serInstanceId and serNames are mutually-exclusive
        Raises KeyError when Invalid Enum is provided
        Raises InvalidIdentifier if no identifier is specified

        Section 8.1.3.2
        """
        self.states = states
        self.isLocal = isLocal
        self.serInstanceId = serInstanceId
        self.serNames = serNames
        self.serCategories = serCategories

    @staticmethod
    def from_json(data: dict) -> FilteringCriteria:
        #TODO VALIDATE
        states = [ServiceState[state] for state in data["states"]]
        isLocal = data["isLocal"]
        # If various identifiers are present pick the first one returned
        identifier = pick_identifier(data)
        # Since only one is acceptable start all as none and then set only the one we got from the previous function
        identifier_data = {"serCategories":None,"serNames":None,"serInstanceId":None}
        if identifier == "serCategories":
            identifier_data["serCategories"] = [CategoryRef(**category) for category in data["serCategories"]]
        elif identifier == "serNames":
            identifier_data["serNames"] = data["serNames"]
        elif identifier == "serInstanceId":
            identifier_data["serInstanceId"] = data["serInstanceId"]

        # The object is created from the two known variables and from the dictionary setting only one identifier data
        return FilteringCriteria(states=states,
                                 isLocal=isLocal,
                                 **identifier_data)

    def to_json(self):
        # Only returns the identifier that isn't None
        for tmp_identifier in ["serCategories","serNames","serInstanceId"]:
            tmp_identifier_value = self.__getattribute__(tmp_identifier)
            if tmp_identifier_value is not None:
                # Recreates the dict for the json to be generated
                return dict(states=self.states,
                            isLocal=self.isLocal,
                            **{tmp_identifier:tmp_identifier_value})

class SerAvailabilityNotificationSubscription:
    def __init__(self, callbackReference: str, _links: Links,
                 filteringCriteria: FilteringCriteria,
                 subscriptionType: str = "SetAvailabilityNotificationSubscription"):
        """

        :param callbackReference: Shall be set to "SerAvailabilityNotificationSubscription".
        :type callbackReference: String
        :param _links: Object containing hyperlinks related to the resource. This shall only be included in the HTTP responses.
        :type _links: str (String is validated to be a correct URI)
        :param filteringCriteria: Filtering criteria to match services for which events are requested to be reported. If absent, matches all services. All child attributes are combined with the logical "AND" operation.
        :type filteringCriteria: FilteringCriteria
        :param subscriptionType: Shall be set to "SerAvailabilityNotificationSubscription".
        :type subscriptionType: str

        Raises TypeError

        Section 8.1.3.2
        """
        self.callbackReference = validate_uri(callbackReference)
        self._links = _links
        self.filteringCriteria = filteringCriteria
        self.subscriptionType = subscriptionType

    @staticmethod
    def from_json(data: dict) -> SerAvailabilityNotificationSubscription:
        # TODO VALIDATE
        callbackReference = data["callbackReference"]
        # Rename self to _self due to python keyword restriction
        data["_links"]["_self"] = data["_links"].pop("self")
        _links = Links.from_json(data["_links"])
        filteringCriteria = FilteringCriteria.from_json(data["filteringCriteria"])
        subscriptionType = data["subscriptionType"]
        return SerAvailabilityNotificationSubscription(callbackReference=callbackReference,
                                                       _links=_links,
                                                       filteringCriteria=filteringCriteria,
                                                       subscriptionType=subscriptionType)
    def to_json(self):
        return dict(callbackReference=self.callbackReference,
                    _links=self._links,
                    filteringCriteria=self.filteringCriteria,
                    subscriptionType=self.subscriptionType)

class OAuth2Info:
    def __init__(self, grantTypes: GrantTypes, tokenEndpoint: List[str]):
        """
        This type represents security information related to a transport.

        :param grantTypes: List of supported OAuth 2.0 grant types
        :type grantTypes: GrantTypes
        :param tokenEndpoint: The Token Endpoint
        :type tokenEndpoint: List[String]

        :Note: grantTypes can be between 1 and 4

        Section 8.1.5.4
        """
        self.grantTypes = grantTypes
        self.tokenEndpoint = tokenEndpoint

class SecurityInfo:
    def __init__(self, oAuth2Info: OAuth2Info):
        """
        :param oAuth2Info: Parameters related to use of OAuth 2.0.

        Section 8.1.5.4
        """
        self.oAuth2Info = oAuth2Info

class EndPointInfo:
    """
    Section 8.1.5.3
    """
    class Uris:
        def __init__(self, uri: str):
            """
            :param uri: Entry point information of the service as string, formatted according to URI syntax
            :type uri: String

            Raises TypeError
            """
            self.uris = validate_uri(uri)

    class Address:
        def __init__(self, host: str, port: int):
            """
            :param host: Host portion of the address.
            :type host: str
            :param port: Port portion of the address.
            :type port: int
            """
            self.host = host
            self.port = port

    class Addresses:
        def __init__(self, addresses: List):
            """
            :param addresses: List of EndPointInfo.Addresses
            :type addresses: List[EndpointInfo.Addresses]
            """
            self.addresses = addresses

    class Alternative:
        # This EndPointInfo isn't specified in MEC 011
        pass

class TransportInfo:
    def __init__(self, id: str, name: str, type: TransportType, version: str, endpoint: EndPointInfo, security: SecurityInfo, impltSpecificInfo: str, description: str, protocol: str = "HTTP"):
        """
        :param id: The identifier of this transport.
        :type id: String
        :param name: The name of this transport.
        :type name: String
        :param type: Type of the transport.
        :type type: TransportType
        :param version: The version of the protocol used.
        :type version: String
        :param endpoint: Information about the endpoint to access the transport.
        :type endpoint: EndPointInfo
        :param security: Information about the security used by the transport.
        :type security: SecurityInfo
        :param impltSpecificInfo: Additional implementation specific details of the transport.
        :type impltSpecificInfo: NotSpecified
        :param protocol: The name of the protocol used. Shall be set to "HTTP" for a REST API.
        :type protocol: String
        :param description: Human-readable description of this transport.
        :type description: String

        Section 8.1.2.3
        """
        self.id = id
        self.name = name
        self.type = type
        self.protocol = protocol
        self.version = version
        self.endpoint = endpoint
        self.security = security
        self.description = description
        self.impltSpecificInfo = impltSpecificInfo

class ServiceInfo:
    def __init__(self, serInstanceId: str, serName: str, serCategory: str, version: str,
                 state: ServiceState, transportInfo: TransportInfo, serializer: SerializerType,
                 scopeOfLocality: LocalityType, isLocal: bool, consumedLocalOnly: bool,
                 _links: Links, livenessInterval: int):
        """
        :param serInstanceId: Identifiers of service instances about which to report events
        :type serInstanceId: String
        :param serName: Names of services about which to report events.
        :type serName: String
        :param serCategory: Categories of services about which to report events.
        :type serCategory: String
        :param version: The version of the service.
        :type version: String
        :param state: Contains the service state.
        :type state: String
        :param transportInfo: Identifier of the platform-provided transport to be used by the service.
        :type transportInfo: String
        :param serializer: Indicate the supported serialization format of the service.
        :type serializer: String
        :param scopeOfLocality: The scope of locality as expressed by "consumedLocalOnly" and "isLocal".
        :type scopeOfLocality: LocalityType
        :param consumedLocalOnly: Indicate whether the service can only be consumed by the MEC applications located in the same locality
        :type consumedLocalOnly: Boolean
        :param isLocal: Indicate whether the service is located in the same locality as the consuming MEC application or not
        :type isLocal: Boolean
        :param _links: Links to resources related to this resource
        :type _links: Links
        :param livenessInterval: Interval (in seconds) between two consecutive "heartbeat" messages
        :type livenessInterval: Integer
        Note serCategories, serInstanceId and serNames are mutually-exclusive
        """
        self.serInstanceId = serInstanceId
        self.serName = serName
        self.serCategory = serCategory
        self.version = version
        self.state = state
        self.transportInfo = transportInfo
        self.serializer = serializer
        self.scopeOfLocality = scopeOfLocality
        self.consumedLocalOnly = consumedLocalOnly
        self.isLocal = isLocal
        self._links = _links
        self.livenessInterval = livenessInterval

####################################
# Classes used by support api      #
####################################