import json
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

class ResponseWrapper(Response):
    def __init__(self, data=None, error_code=None, error_msg=None, msg=None, response_success=True, status=None, data_type=None, **kwargs):
        if error_code is not None or (status is not None and (status < 200 or status >= 300)):
            response_success = False

        pagination = {}
        if isinstance(data, dict) and "results" in data:
            pagination = {
                "count": data.get("count"),
                "page_size": data.get("page_size"),
                "next": data.get("next"),
                "previous": data.get("previous")
            }
            data = data.get("results")
        elif data is not None:
            pagination = None

        error = {"code": error_code, "error_details": json.dumps(error_msg)} if error_code is not None else None

        output_data = {
            "error": error,
            "pagination": pagination,
            "data": data,
            "status": response_success,
            "status_code": status,
            "msg": msg if msg else str(error_msg) if error_msg else "Success" if response_success else "Failed",
        }

        if data_type is not None:
            output_data["data_type"] = data_type

        super().__init__(data=output_data, status=status, **kwargs)


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        if "error" not in data and response.status_code >= 400 and response.status_code < 500:
            # error
            error_code = response.status_code
            if isinstance(data, list):
                error_msg = str(data)
            else:
                error_msg = data.get("detail")
            response_success = response.status_text
            msg = response.status_text

            # response parse
            pagination = {
                "count": None,
                "page_size": None,
                "next": None,
                "previous": None
            }

            output_data = {
                "error": {"code": error_code, "error_details": error_msg},
                "pagination": pagination,
                "data": None,
                "status": False,
                "status_code": 400,
                # "status_code": response.status_code,
                "msg": msg if msg else str(error_msg) if error_msg else "Success" if response_success else "Failed",
            }
            return super().render(output_data, accepted_media_type, renderer_context)
        return super().render(data, accepted_media_type, renderer_context)