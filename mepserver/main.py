from mp1.service_mgmt.controllers.app_subscriptions_controller import ApplicationSubscriptionsController
from mp1.service_mgmt.controllers.app_services_controller import ApplicationServicesController
from mp1.service_mgmt.controllers.services_controller import ServicesController
from mp1.service_mgmt.controllers.transports_controller import TransportsController

import cherrypy

if __name__ == "__main__":
    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    # Todo load from config file
    #######################################
    # Application Subscription Controller #
    #######################################

    dispatcher.connect(name='Get an applicationInstanceId Subscriptions',
                       action='applications_subscriptions_get',
                       controller=ApplicationSubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name='Get an applicationInstanceId Subscriptions',
                       action='applications_subscriptions_get_with_subscription_id',
                       controller=ApplicationSubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions/:subscriptionId',
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name='Create applicationInstanceId Subscriptions',
                       action='applications_subscriptions_post',
                       controller=ApplicationSubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions',
                       conditions=dict(method=["POST"]))

    dispatcher.connect(name='Delete applicationInstanceID Subscriptions with subscriptionId',
                       action='applications_subscriptions_delete',
                       controller=ApplicationSubscriptionsController,
                       route='/applications/:appInstanceId/subscriptions/:subscriptionId',
                       conditions=dict(method=["DELETE"]))

    ###################################
    # Application Services Controller #
    ###################################

    dispatcher.connect(name='Get service from InstanceId',
                      action='applications_services_get',
                      controller=ApplicationServicesController,
                      route='/applications/:appInstanceId/services',
                      conditions=dict(method=["GET"]))

    dispatcher.connect(name="Create service for InstanceId",
                       action="applications_services_post",
                       controller=ApplicationServicesController,
                       route="/applications/:appInstanceId/services",
                       conditions=dict(method=["POST"]))

    dispatcher.connect(name="Get service from InstanceId and ServiceId",
                       action="applicaton_services_get_with_service_id",
                       controller=ApplicationServicesController,
                       route="/applications/:appInstanceId/services/:serviceId",
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name="Put data into existing service",
                       action="application_services_put",
                       controller=ApplicationServicesController,
                       route="/applications/:appInstanceId/services/:serviceId",
                       conditions=dict(method=["PUT"]))

    dispatcher.connect(name="Delete service",
                       action="application_services_delete",
                       controller=ApplicationServicesController,
                       route="/applications/:appInstanceId/serviecs/:serviceId",
                       conditions=dict(method=["DELETE"]))

    #######################
    # Services Controller #
    #######################

    dispatcher.connect(name="Get services",
                       action="services_get",
                       controller=ServicesController,
                       route="/services",
                       conditions=dict(method=["GET"]))

    dispatcher.connect(name="Get services with serviceId",
                       action="services_get_with_serviceId",
                       controller=ServicesController,
                       route="/services/:serviceId",
                       conditions=dict(method=["GET"]))

    ########################
    # Transport Controller #
    ########################
    dispatcher.connect(name="Get services with serviceId",
                       action="transports_get",
                       controller=TransportsController,
                       route="/transports",
                       conditions=dict(method=["GET"]))

    conf = {'/':{'request.dispatch':dispatcher}}
    cherrypy.tree.mount(None,'/mec_service_mgmt/v1',config=conf)
    cherrypy.engine.start()