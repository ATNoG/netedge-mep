# Service Management Controllers
from mp1.service_mgmt.controllers.app_subscriptions_controller import (
    ApplicationSubscriptionsController,
)
from mp1.service_mgmt.controllers.app_services_controller import (
    ApplicationServicesController,
)
from mp1.service_mgmt.controllers.services_controller import ServicesController
from mp1.service_mgmt.controllers.transports_controller import TransportsController

# Application Support Controllers
from mp1.application_support.controllers.app_confirmation_controller import (
    ApplicationConfirmationController,
)

import cherrypy

if __name__ == "__main__":
    mgmt_dispatcher = cherrypy.dispatch.RoutesDispatcher()
    #############################################
    # Application service management interface  #
    #############################################

    # Todo load from config file
    #######################################
    # Application Subscription Controller #
    #######################################

    mgmt_dispatcher.connect(
        name="Get an applicationInstanceId Subscriptions",
        action="applications_subscriptions_get",
        controller=ApplicationSubscriptionsController,
        route="/applications/:appInstanceId/subscriptions",
        conditions=dict(method=["GET"]),
    )

    mgmt_dispatcher.connect(
        name="Get an applicationInstanceId Subscriptions",
        action="applications_subscriptions_get_with_subscription_id",
        controller=ApplicationSubscriptionsController,
        route="/applications/:appInstanceId/subscriptions/:subscriptionId",
        conditions=dict(method=["GET"]),
    )

    mgmt_dispatcher.connect(
        name="Create applicationInstanceId Subscriptions",
        action="applications_subscriptions_post",
        controller=ApplicationSubscriptionsController,
        route="/applications/:appInstanceId/subscriptions",
        conditions=dict(method=["POST"]),
    )

    mgmt_dispatcher.connect(
        name="Delete applicationInstanceID Subscriptions with subscriptionId",
        action="applications_subscriptions_delete",
        controller=ApplicationSubscriptionsController,
        route="/applications/:appInstanceId/subscriptions/:subscriptionId",
        conditions=dict(method=["DELETE"]),
    )

    ###################################
    # Application Services Controller #
    ###################################

    mgmt_dispatcher.connect(name='Get service from InstanceId and parameters',
                            action='applications_services_get',
                            controller=ApplicationServicesController,
                            route='/applications/:appInstanceId/services',
                            conditions=dict(method=["GET"]))

    mgmt_dispatcher.connect(name="Create service for InstanceId",
                            action="applications_services_post",
                            controller=ApplicationServicesController,
                            route="/applications/:appInstanceId/services",
                            conditions=dict(method=["POST"]))

    mgmt_dispatcher.connect(name="Get service from InstanceId and ServiceId",
                            action="applicaton_services_get_with_service_id",
                            controller=ApplicationServicesController,
                            route="/applications/:appInstanceId/services/:serviceId",
                            conditions=dict(method=["GET"]))

    mgmt_dispatcher.connect(name="Put data into existing service",
                            action="application_services_put",
                            controller=ApplicationServicesController,
                            route="/applications/:appInstanceId/services/:serviceId",
                            conditions=dict(method=["PUT"]))

    mgmt_dispatcher.connect(name="Delete service",
                            action="application_services_delete",
                            controller=ApplicationServicesController,
                            route="/applications/:appInstanceId/services/:serviceId",
                            conditions=dict(method=["DELETE"]))

    #######################
    # Services Controller #
    #######################

    mgmt_dispatcher.connect(
        name="Get services",
        action="services_get",
        controller=ServicesController,
        route="/services",
        conditions=dict(method=["GET"]),
    )

    mgmt_dispatcher.connect(
        name="Get services with serviceId",
        action="services_get_with_serviceId",
        controller=ServicesController,
        route="/services/:serviceId",
        conditions=dict(method=["GET"]),
    )

    ########################
    # Transport Controller #
    ########################
    mgmt_dispatcher.connect(
        name="Get transports",
        action="transports_get",
        controller=TransportsController,
        route="/transports",
        conditions=dict(method=["GET"]),
    )

    ##################################
    # Application support interface  #
    ##################################

    support_dispatcher = cherrypy.dispatch.RoutesDispatcher()

    #####################################
    # Application ready and termination #
    #####################################

    support_dispatcher.connect(
        name="Application Ready request",
        action="applications_confirm_ready",
        controller=ApplicationConfirmationController,
        route="/applications/:appInstanceId/confirm_ready",
        conditions=dict(method=["POST"]),
    )

    support_dispatcher.connect(
        name="Application termination request",
        action="applications_confirm_termination",
        controller=ApplicationConfirmationController,
        route="/applications/:appInstanceId/confirm_termination",
        conditions=dict(method=["POST"]),
    )

    mgmt_conf = {"/": {"request.dispatch": mgmt_dispatcher}}
    cherrypy.tree.mount(None, "/mec_service_mgmt/v1", config=mgmt_conf)
    supp_conf = {"/": {"request.dispatch": support_dispatcher}}
    cherrypy.tree.mount(None, "/mec_app_support/v1", config=supp_conf)
    cherrypy.engine.start()
