from rest_framework.exceptions import APIException
from core.exceptions.error_messages import ErrorCodes, get_error_details
from datetime import datetime

class CustomApiException(APIException):

    def __init__(self, 
                 error_code: ErrorCodes, 
                 message: str = None, 
                 ok: bool = False, 
                 extra_data: dict = None):
        error_details = get_error_details(error_code)

        self.status_code = error_details['status']
        self.detail = {
            'detail': message or error_details['message'],
            'ok': ok,
            'error_code': error_code.value,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }

        if extra_data:
            self.detail.update(extra_data)
