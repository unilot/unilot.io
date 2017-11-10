from rest_framework import response as rf_response
from rest_framework import status
import semantic_version as sv


from sportloto import settings


class ApiVersionControlMiddleware(object):
    HTTP_API_VERSION = 'HTTP_API_VERSION'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        """
        :param request:
        :type rest_framework.request.Request:
        :param args:
        :type list:
        :param kwargs:
        :type dict:
        :return:
        """

        requested_api_version = sv.Spec(request.META.get(self.HTTP_API_VERSION, settings.VERSION))

        if not requested_api_version.match(sv.Version(settings.VERSION)):
            response = rf_response.Response(status=status.HTTP_417_EXPECTATION_FAILED)
            response._is_rendered = True
        else:
            response = self.get_response(request)


        return response
