
def services_get():
    """
    This method retrieves information about a list of mecService resources. This method is typically used in "service availability query" procedure

    Query Params
    :param ser_instance_id: A MEC application instance may use multiple ser_instance_ids as an input parameter to query the availability of a list of MEC service instances. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
    :type ser_instance_id: List[String]
    :param ser_name: A MEC application instance may use multiple ser_names as an input parameter to query the availability of a list of MEC service instances. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
    :type ser_name: List[String]
    :param ser_category_id: A MEC application instance may use ser_category_id as an input parameter to query the availability of a list of MEC service instances in a serCategory. Either "ser_instance_id" or "ser_name" or "ser_category_id" or none of them shall be present.
    :type ser_category_id: String
    :param consumed_local_only: Indicate whether the service can only be consumed by the MEC applications located in the same locality (as defined by scopeOfLocality) as this service instance.
    :type consumed_local_only: boolean
    :param is_local: Indicate whether the service is located in the same locality (as defined by scopeOfLocality) as the consuming MEC application.
    :type is_local: boolean
    :param scope_of_locality: A MEC application instance may use scope_of_locality as an input parameter to query the availability of a list of MEC service instances with a certain scope of locality.
    :type scope_of_locality: String

    :note: ser_name, ser_category_id, ser_instance_id are mutually-exclusive only one should be used

    :return: ServiceInfo or ProblemDetails
    HTTP STATUS CODE: 200, 400, 403, 404, 414
    """

    return None

def services_get(serviceId: str):
    """
    This method retrieves information about a mecService resource. This method is typically used in "service availability query" procedure

    :param serviceId: Represents a MEC service instance.
    :type serviceId: String

    :return: ServiceInfo or ProblemDetails
    """

    return None
