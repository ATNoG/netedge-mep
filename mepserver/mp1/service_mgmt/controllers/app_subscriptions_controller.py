
def applications_subscriptions_get(appInstanceId: int):
    """
    The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

    :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
    :type appInstanceId: str

    :return: MecServiceMgmtApiSubscriptionLinkList or ProblemDetails
    HTTP STATUS CODE: 200, 400, 403, 404
    """
    return None

def applications_subscriptions_post(appInstanceId: int):
    """
    The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

    :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
    :type appInstanceId: str

    :request body: Entity body in the request contains a subscription to the MEC application termination notifications that is to be created.

    :return: SerAvailabilityNotificationSubscription or ProblemDetails
    HTTP STATUS CODE: 201, 400, 403, 404
    """
    return None

def applications_subscriptions_get(appInstanceId: int, subscriptionId: int):
    """
    The GET method requests information about a subscription for this requestor. Upon success, the response contains entity body with the subscription for the requestor.

    :param appInstanceId:  Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
    :type appInstanceId: str
    :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
    :type subscriptionId: str

    :return: SerAvailabilityNotificationSubscription or ProblemDetails
    HTTP STATUS CODE: 200, 400, 403, 404
    """

    return None

def applications_subscriptions_delete(appInstanceId: int, subscriptionId: int):
    """
    This method deletes a mecSrvMgmtSubscription. This method is typically used in "Unsubscribing from service availability event notifications" procedure.

    :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
    :type appInstanceId: str
    :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
    :type subscriptionId: str

    :return: No Content or ProblemDetails
    HTTP STATUS CODE: 204, 403, 404
    """
    return None

