import sys
sys.path.append('../../')
from mp1.models import *

class ApplicationSubscriptionsController:

    @json_out(cls=NestedEncoder)
    def applications_subscriptions_get(self,appInstanceId: str):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :return: MecServiceMgmtApiSubscriptionLinkList or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        if cherrypy.request.method == "GET":
            #TODO CREATE REALLY CONNECTION
            data = {"_links":{"self":{"href":"http://google.com"},"subscriptions":[{"href":"http://google.com","subscriptionType":"data"}]}}
            service = MecServiceMgmtApiSubscriptionLinkList.from_json(data)
            return service
        else:
            # TODO PROPERLY FIX INVALID REQUESTS
            cherrypy.response.status = 400
            problem_detail = ProblemDetails(type="",
                                            title="Invalid HTTP Request Method",
                                            status=400,
                                            detail="Endpoint only accepts GET requests",
                                            instance="")

            return vars(problem_detail)

    @cherrypy.tools.json_in()
    @json_out(cls=NestedEncoder)
    def applications_subscriptions_post(self,appInstanceId: str):
        """
        The GET method may be used to request information about all subscriptions for this requestor. Upon success, the response contains entity body with all the subscriptions for the requestor.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str

        :request body: Entity body in the request contains a subscription to the MEC application termination notifications that is to be created.

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 201, 400, 403, 404
        """
        if cherrypy.request.method == "POST":
            # TODO VALIDATE THE JSON and use Instance ID
            input_json = cherrypy.request.json
            try:
                availability_notification = SerAvailabilityNotificationSubscription.from_json(input_json)

                return availability_notification
            except TypeError as e:
                cherrypy.response.status = 400
                problem_detail = ProblemDetails(type="",
                                                title="Invalid href",
                                                status=400,
                                                detail="Resource URI didn't meet specifications",
                                                instance="")
                return problem_detail
            except KeyError as e:
                cherrypy.response.status = 400
                problem_detail = ProblemDetails(type="",
                                                title="Invalid Request Data",
                                                status=400,
                                                detail="The request data contained one or more invalid parameters" ,
                                                instance="")
                return problem_detail
        # TODO MISSING CALLBACK

    @json_out(cls=NestedEncoder)
    def applications_subscriptions_get_with_subscription_id(self,appInstanceId: str, subscriptionId: str):
        """
        The GET method requests information about a subscription for this requestor. Upon success, the response contains entity body with the subscription for the requestor.

        :param appInstanceId:  Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: SerAvailabilityNotificationSubscription or ProblemDetails
        HTTP STATUS CODE: 200, 400, 403, 404
        """
        data = json.loads("{\"subscriptionType\":\"string\",\"callbackReference\":\"http://www.google1.com\",\"_links\":{\"self\":{\"href\":\"http://www.google.com\"},\"subscriptions\":[{\"href\":\"http://www.google.com\",\"subscriptionType\":\"Normal\"}]},\"filteringCriteria\":{\"serInstanceIds\":[\"string\"],\"serNames\":[\"string\"],\"serCategories\":[{\"href\":\"http://www.google.com\",\"id\":\"string\",\"name\":\"string\",\"version\":\"string\"}],\"states\":[\"ACTIVE\"],\"isLocal\":true}}")
        availability_notification = SerAvailabilityNotificationSubscription.from_json(data)
        return availability_notification

    def applications_subscriptions_delete(self,appInstanceId: str, subscriptionId: str):
        """
        This method deletes a mecSrvMgmtSubscription. This method is typically used in "Unsubscribing from service availability event notifications" procedure.

        :param appInstanceId: Represents a MEC application instance. Note that the appInstanceId is allocated by the MEC platform manager.
        :type appInstanceId: str
        :param subscriptionId: Represents a subscription to the notifications from the MEC platform.
        :type subscriptionId: str

        :return: No Content or ProblemDetails
        HTTP STATUS CODE: 204, 403, 404
        """
        # TODO LOGIC
        cherrypy.response.status = 204
        return
