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

from __future__ import annotations
from typing import List, Union
from jsonschema import validate
import cherrypy

from .utils import *
from .enums import *
from .mep_exceptions import *
from .schemas import *

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

    def __init__(self, href: str):
        self.href = href

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

    def to_json(self):
        return dict(
            type=self.type,
            title=self.title,
            status=self.status,
            detail=self.detail,
            instance=self.instance,
        )


####################################
# Classes used by management api   #
####################################
class Subscription:
    """
    The MEC application instance's subscriptions.

    Section 6.2.2
    """

    def __init__(
        self,
        href: str,
        subscriptionType: Union[str, None] = "SerAvailabilityNotificationSubscription",
    ):
        """
        :param href: URI referring to the subscription. (isn't a real URI but the path to something in our MEP)
        :type href: str
        :param subscriptionType: Type of the subscription.
        :type subscriptionType: str

        Raises TypeError
        """
        self.href = href
        self.subscriptionType = subscriptionType

    def to_json(self):
        return ignore_none_value(
            dict(href=self.href, subscriptionType=self.subscriptionType)
        )


class Links:
    """
    Internal structure to be compliant with MEC 011

    Section 6.2.2
    """

    def __init__(
        self,
        _self: LinkType = None,
        subscriptions: List[Subscription] = None,
        liveness: LinkType = None,
    ):
        self.self = _self
        self.subscriptions = subscriptions
        self.liveness = liveness

    @staticmethod
    def from_json(data: dict) -> Links:
        validate(instance=data, schema=links_schema)
        _self = LinkType(data["self"]["href"])
        subscriptions = None
        if "subscriptions" in data and len(data["subscriptions"]) > 0:
            cherrypy.log(json.dumps(data["subscriptions"]))
            subscriptions = [
                Subscription(**subscription) for subscription in data["subscriptions"]
            ]
        liveness = None
        if "liveness" in data:
            liveness = LinkType(data["liveness"]["href"])

        return Links(_self=_self, subscriptions=subscriptions, liveness=liveness)

    def to_json(self):
        return ignore_none_value(
            dict(
                self=self.self, subscriptions=self.subscriptions, liveness=self.liveness
            )
        )


class MecServiceMgmtApiSubscriptionLinkList:
    """
    This type represents a list of links related to currently existing subscriptions for a MEC application instance.
    This information is returned when sending a request to receive current subscriptions.

    Section 6.2.2 - MEC 011
    """

    def __init__(self, _links: Links):
        self._links = _links

    @staticmethod
    def from_json(data: dict) -> MecServiceMgmtApiSubscriptionLinkList:
        # First validate the json via jsonschema
        validate(instance=data, schema=mecservicemgmtapisubscriptionlinklist_schema)
        _links = Links.from_json(data["_links"])
        return MecServiceMgmtApiSubscriptionLinkList(_links=_links)

    def to_json(self):
        return dict(_links=self._links)


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

    def to_json(self):
        # All required none should have value none thus there is no need to use ignore_none_val
        return dict(href=self.href, id=self.id, name=self.name, version=self.version)


class FilteringCriteria:
    def __init__(
        self,
        states: List[ServiceState],
        isLocal: bool,
        serInstanceIds: List[str] = None,
        serNames: List[str] = None,
        serCategories: List[CategoryRef] = None,
    ):
        """
        :param states: States of the services about which to report events. If the event is a state change, this filter represents the state after the change
        :type states: List[ServiceState]
        :param isLocal: Restrict event reporting to whether the service is local to the MEC platform where the subscription is managed.
        :type isLocal: Boolean
        :param serInstanceIds: Identifiers of service instances about which to report events
        :type serInstanceIds: String
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
        self.serInstanceIds = serInstanceIds
        self.serNames = serNames
        self.serCategories = serCategories

    @staticmethod
    def from_json(data: dict) -> FilteringCriteria:
        validate(instance=data, schema=filteringcriteria_schema)
        tmp_states = data.pop("states", None)
        if tmp_states == None:
            states = None
        else:
            states = [ServiceState[state] for state in tmp_states]
        isLocal = data.pop("isLocal", None)

        # Since only one is acceptable start all as none and then set only the one presented in the data
        # the validation from json schema deals with the mutually exclusive part
        identifier_data = {
            "serCategories": None,
            "serNames": None,
            "serInstanceIds": None,
        }
        if "serCategories" in data:
            identifier_data["serCategories"] = [
                CategoryRef(**category) for category in data["serCategories"]
            ]
        elif "serNames" in data:
            identifier_data["serNames"] = data["serNames"]
        elif "serInstanceIds" in data:
            identifier_data["serInstanceIds"] = data["serInstanceId"]

        # The object is created from the two known variables and from the dictionary setting only one identifier data
        return FilteringCriteria(states=states, isLocal=isLocal, **identifier_data)

    def to_json(self):
        return ignore_none_value(
            dict(
                states=self.states,
                isLocal=self.isLocal,
                serInstanceIds=self.serInstanceIds,
                serNames=self.serNames,
                serCategories=self.serCategories,
            )
        )

    def to_query(self):
        """
        Different from to_json because it uses singular names instead of plural ones
        This is due to the fact that the filtering criteria is made with plural names while
        services in the database stores things in singular
        """
        return ignore_none_value(
            dict(
                state=self.states,
                isLocal=self.isLocal,
                serInstanceId=self.serInstanceIds,
                serName=self.serNames,
                serCategorie=self.serCategories,
            )
        )


class ServiceAvailabilityNotification:
    def __init__(
        self,
        serviceReferences: List[ServiceReferences],
        _links: Subscription,
        notificationType: str = "SerAvailabilityNotificationSubscription",
    ):
        """

        :param serviceReferences: List of links to services whose availability has changed.
        :type serviceReferences: List of ServiceReferences
        :param _links: Object containing hyperlinks related to the resource.
                        Can be None (Temporarly) in the case of a new service where the data is added during callback
        :type _links: Subscription
        :param notificationType: hall be set to "SerAvailabilityNotification"
        :type notificationType: String

        Section 8.1.4.2
        """
        self.notificationType = notificationType
        self.serviceReferences = serviceReferences
        self._links = _links

    class ServiceReferences:
        def __init__(
            self,
            link: LinkType,
            serInstanceId: str,
            state: ServiceState,
            serName: str,
            changeType: ChangeType,
        ):
            self.link = link
            self.serInstanceId = serInstanceId
            self.serName = serName
            self.state = state
            self.changeType = changeType

        @staticmethod
        def from_json(data: dict):
            """
            :param data: Data used to generate a ServiceReference
            :type data: JSON / Python Dict
            :return: ServiceReference
            """
            # Link is weird - ETSI overall structure for the _link type is really confusing
            link = LinkType(data.get("_links").get("liveness").get("href"))
            serInstanceId = data.get("serInstanceId")
            state = data.get("state")
            serName = data.get("serName")
            changeType = ChangeType(data.get("changeType"))
            return ServiceAvailabilityNotification.ServiceReferences(
                link=link,
                serInstanceId=serInstanceId,
                state=state,
                serName=serName,
                changeType=changeType,
            )

        def to_json(self):
            return dict(
                link=self.link,
                serInstanceId=self.serInstanceId,
                serName=self.serName,
                state=self.state,
                changeType=self.changeType,
            )

    @staticmethod
    def from_json_service_list(
        data: list[dict], changeType: str, subscription: str = None
    ):
        """
        :param data: List containing all services (in json form) that match the filtering criteria
        :type data: JSON / Python dictionary
        :param subscription: URL referencing the subscription resource
        :type subscription: String
        :param changeType: Type of the change being sent to the subscriber
        :type changeType: ChangeType
        :return: ServiceAvailabilityNotification
        """
        if subscription:
            _links = Subscription(href=subscription, subscriptionType=None)
        else:
            _links = None
        serviceReferences = []

        for service in data:
            service["changeType"] = changeType
            tmpReference = ServiceAvailabilityNotification.ServiceReferences.from_json(
                data=service
            )
            serviceReferences.append(tmpReference)
        return ServiceAvailabilityNotification(
            _links=_links, serviceReferences=serviceReferences
        )

    def to_json(self):
        return ignore_none_value(
            dict(
                notificationType=self.notificationType,
                _links=self._links,
                serviceReferences=self.serviceReferences,
            )
        )


class SerAvailabilityNotificationSubscription:
    def __init__(
        self,
        callbackReference: str,
        _links: Links = None,
        filteringCriteria: FilteringCriteria = None,
    ):
        """

        :param callbackReference: URI selected by the MEC application instance to receive notifications on the subscribed MEC service availability information. This shall be included in both the request and the response.".
        :type callbackReference: String
        :param _links: Object containing hyperlinks related to the resource. This shall only be included in the HTTP responses.
        :type _links: str (String is validated to be a correct URI)
        :param filteringCriteria: Filtering criteria to match services for which events are requested to be reported. If absent, matches all services. All child attributes are combined with the logical "AND" operation.
        :type filteringCriteria: FilteringCriteria

        Raises TypeError

        Section 8.1.3.2
        """
        self.callbackReference = validate_uri(callbackReference)
        self._links = _links
        self.filteringCriteria = filteringCriteria
        self.subscriptionType = "SerAvailabilityNotificationSubscription"
        """
        AppInstanceId and subscriptionId are only used internally to deal with callbacks
        """
        self.appInstanceId = None
        self.subscriptionId = None

    @staticmethod
    def from_json(data: dict) -> SerAvailabilityNotificationSubscription:
        # validate the json via jsonschema
        validate(instance=data, schema=seravailabilitynotificationsubscription_schema)
        # FilteringCriteria is not a required request body parameter
        # Using {} instead of None is due to the fact that if nothing is passed it is supposed to match everything
        # this makes it easier to query this edge case in the database
        filteringCriteria = {}
        if "filteringCriteria" in data:
            filteringCriteria = FilteringCriteria.from_json(
                data.pop("filteringCriteria")
            )
        return SerAvailabilityNotificationSubscription(
            filteringCriteria=filteringCriteria, **data
        )

    def to_json(self):
        return ignore_none_value(
            dict(
                callbackReference=self.callbackReference,
                _links=self._links,
                filteringCriteria=self.filteringCriteria,
                subscriptionType=self.subscriptionType,
            )
        )


class OAuth2Info:
    def __init__(self, grantTypes: List[GrantTypes], tokenEndpoint: str):
        """
        This type represents security information related to a transport.

        :param grantTypes: List of supported OAuth 2.0 grant types
        :type grantTypes: List[GrantTypes] Min size 1 Max Size 4
        :param tokenEndpoint: The Token Endpoint
        :type tokenEndpoint: String

        :Note: grantTypes can be between 1 and 4
        :Note: tokenEndpoint seems required in swagger but isn't in MEC011 Specification

        Section 8.1.5.4
        Raises InvalidGrantType
        """
        self.grantTypes = grantTypes
        self.tokenEndpoint = tokenEndpoint

    @staticmethod
    def from_json(data: dict) -> OAuth2Info:
        # list(set()) to ignore possible duplicates from the user
        data["grantTypes"] = list(set(data["grantTypes"]))
        if 1 > len(data["grantTypes"]) > 4:
            raise InvalidGrantType

        grantTypes = [GrantTypes(grantType) for grantType in data.pop("grantTypes")]
        return OAuth2Info(grantTypes=grantTypes, **data)

    def to_json(self):
        return dict(grantTypes=self.grantTypes, tokenEndpoint=self.tokenEndpoint)


class SecurityInfo:
    def __init__(self, oAuth2Info: OAuth2Info):
        """
        :param oAuth2Info: Parameters related to use of OAuth 2.0.

        Section 8.1.5.4
        """
        self.oAuth2Info = oAuth2Info

    @staticmethod
    def from_json(data: dict) -> SecurityInfo:
        oAuth2Info = OAuth2Info.from_json(data["oAuth2Info"])
        return SecurityInfo(oAuth2Info=oAuth2Info)

    def to_json(self):
        return dict(oAuth2Info=self.oAuth2Info)


class EndPointInfo:
    """
    Section 8.1.5.3
    """

    class Uris:
        def __init__(self, uris: List[str]):
            """
            :param uri: Entry point information of the service as string, formatted according to URI syntax
            :type uri: String

            Raises TypeError
            """
            self.uris = [validate_uri(uri) for uri in uris]

        def to_json(self):
            return dict(uris=self.uris)

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

        def to_json(self):
            return dict(host=self.host, port=self.port)

    class Addresses:
        def __init__(self, addresses: List[object]):
            """
            :param addresses: List of EndPointInfo.Addresses
            :type addresses: List[EndpointInfo.Addresses]
            """
            self.addresses = addresses

        @staticmethod
        def from_json(data: dict) -> EndPointInfo.Addresses:
            addresses = [EndPointInfo.Address(host, port) for host, port in data]
            return EndPointInfo.Addresses(addresses)

        def to_json(self):
            return dict(addresses=self.addresses)

    class Alternative:
        # This EndPointInfo isn't specified in MEC 011
        pass

    @staticmethod
    def from_json(data: dict):
        # Check which EndPointInfo was sent
        # Address
        if "addresses" in data.keys():
            return EndPointInfo.Addresses.from_json(data["addresses"])
        if "uris" in data.keys():
            return EndPointInfo.Uris(uris=data["uris"])


class TransportInfo:
    def __init__(
        self,
        id: str,
        name: str,
        type: TransportType,
        version: str,
        endpoint: [EndPointInfo.Addresses, EndPointInfo.Uris, EndPointInfo.Alternative],
        security: SecurityInfo,
        description: str = "",
        implSpecificInfo: str = "",
        protocol: str = "HTTP",
    ):
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
        :param implSpecificInfo: Additional implementation specific details of the transport.
        :type implSpecificInfo: NotSpecified
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
        self.implSpecificInfo = implSpecificInfo

    @staticmethod
    def from_json(data: dict) -> TransportInfo:
        _type = TransportType(data.pop("type"))
        endpoint = EndPointInfo.from_json(data.pop("endpoint"))
        security = SecurityInfo.from_json(data.pop("security"))
        return TransportInfo(type=_type, endpoint=endpoint, security=security, **data)

    def to_json(self):
        return ignore_none_value(
            dict(
                id=self.id,
                name=self.name,
                type=self.type,
                protocol=self.protocol,
                version=self.version,
                endpoint=self.endpoint,
                security=self.security,
                description=self.description,
                implSpecificInfo=self.implSpecificInfo,
            )
        )


class ServiceInfo:
    def __init__(
        self,
        version: str,
        state: ServiceState,
        transportInfo: TransportInfo,
        serializer: SerializerType,
        livenessInterval: int,
        _links: Links = None,
        consumedLocalOnly: bool = True,
        isLocal: bool = True,
        scopeOfLocality: LocalityType = LocalityType.MEC_HOST,
        serInstanceId: str = None,
        serName: str = None,
        serCategory: str = None,
    ):
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

        Section 8.1.2.2
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

    @staticmethod
    def from_json(data: dict) -> ServiceInfo:
        # Validate the json via jsonschema
        validate(instance=data, schema=serviceinfo_schema)
        identifier_data = {}
        categoryref = data.pop("serCategory", None)
        if categoryref is not None:
            identifier_data["serCategory"] = CategoryRef(**categoryref)
        identifier_data["serName"] = data.pop("serName", None)

        # Each required element or element that can't be automatically generated from the unpacking is popped
        # to avoid having the function received the element twice and throwing an exception
        state = ServiceState(data.pop("state"))
        transportInfo = TransportInfo.from_json(data.pop("transportInfo"))
        serializer = SerializerType(data.pop("serializer"))
        scopeOfLocality = None
        if "scopeOfLocality" in data.keys():
            scopeOfLocality = LocalityType(data.pop("scopeOfLocality"))

        return ServiceInfo(
            state=state,
            transportInfo=transportInfo,
            serializer=serializer,
            scopeOfLocality=scopeOfLocality,
            **data,
            **identifier_data,
        )

    def to_json(self):
        return ignore_none_value(
            dict(
                version=self.version,
                serInstanceId=self.serInstanceId,
                serName=self.serName,
                serCategory=self.serCategory,
                serializer=self.serializer,
                _links=self._links,
                scopeOfLocality=self.scopeOfLocality,
                transportInfo=self.transportInfo,
                state=self.state,
                livenessInterval=self.livenessInterval,
                consumedLocalOnly=self.consumedLocalOnly,
                isLocal=self.isLocal,
            )
        )

    def to_filtering_criteria_json(self):
        """
        Used with the $or mongodb operator which requires a list of dictionaries for each "or" operation
        Example we want to get an object that can have serName="a" or serInstanceId="b"
        {$or:[{"serName":a},{"serInstanceId":"b"}]}

        Due to serInstancesIds,serNames,serCategories and states being addressable by various values we transform
        them into a list so that we can use the $in operator
        """
        tmp_ret = ignore_none_value(
            dict(
                serInstanceIds=[self.serInstanceId],
                serNames=[self.serName],
                serCategories=[self.serCategory],
                states=[self.state],
                isLocal=self.isLocal,
            )
        )

        return {
            "$and": [
                {
                    "$or": [
                        {f"filteringCriteria.{key}": {"$exists": False}},
                        {f"filteringCriteria.{key}": val},
                    ]
                }
                for key, val in list(tmp_ret.items())
            ]
        }


####################################
# Classes used by support api      #
####################################

# In theory this class doesn't need to exist but since ETSI defined a post request body
# it may be useful in the future (i.e new indications etc...)
class AppReadyConfirmation:
    def __init__(self, indication: IndicationType):
        self.indication = indication

    @staticmethod
    def from_json(data: dict) -> AppReadyConfirmation:
        # Validate the json via json schema
        validate(instance=data, schema=appreadyconfirmation_schema)
        indication = IndicationType(data["indication"])
        return AppReadyConfirmation(indication=indication)

    def to_json(self):
        return ignore_none_value(dict(indication=self.indication))


# In theory this class doesn't need to exist but since ETSI defined a post request body
# it may be useful in the future (i.e new indications etc...)
class AppTerminationConfirmation:
    def __init__(self, operationAction: OperationActionType):
        self.operationAction = operationAction

    @staticmethod
    def from_json(data: dict) -> AppTerminationConfirmation:
        # Validate the json via json schema
        validate(instance=data, schema=appterminationconfirmation_schema)
        operationAction = OperationActionType(data["operationAction"])
        return AppTerminationConfirmation(operationAction=operationAction)

    def to_json(self):
        return ignore_none_value(dict(operationAction=self.operationAction))
