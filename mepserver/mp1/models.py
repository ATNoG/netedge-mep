from typing import List
from utils import *
from enum import Enum

class LinkType:
    """
    This type represents a type of link and may be referenced from data structures.

    Section 6.3.2 - MEC 011
    """
    def __init__(self,href):
        self.href = validate_uri(href)

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

class Links:
    """
    Internal structure to be compliant with MEC 011

    Section 6.2.2
    """

    def __init__(self, _self: LinkType, subscriptions: List[Subscription]):
        self.self = _self
        self.subscriptions = subscriptions


class MecServiceMgmtApiSubscriptionLinkList:
    """
    This type represents a list of links related to currently existing subscriptions for a MEC application instance. This information is returned when sending a request to receive current subscriptions.

    Section 6.2.2 - MEC 011
    """
    def __init__(self,_links: Links):
        self._links = _links

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

class ServiceState(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class FilteringCriteria:
    def __init__(self, states: List[ServiceState], isLocal: bool, serInstancesId: List[str] = None, serNames: List[str] = None, serCategories: List[CategoryRef] = None):
        """
        :param states: States of the services about which to report events. If the event is a state change, this filter represents the state after the change
        :type states: List[ServiceState]
        :param isLocal: Restrict event reporting to whether the service is local to the MEC platform where the subscription is managed.
        :type isLocal: Boolean
        :param serInstancesId: Identifiers of service instances about which to report events
        :type serInstancesId: String
        :param serNames: Names of services about which to report events
        :type serNames: String
        :param serCategories: Categories of services about which to report events.
        :type serCategories: List of CategoryRef

        Note serCategories, serInstanceId and serNames are mutually-exclusive
        Section 8.1.3.2
        """
        self.states = states
        self.isLocal = isLocal
        self.serInstancesId = serInstancesId
        self.serNames = serNames
        self.serCategories = serCategories

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