from enum import Enum
from rest_framework import status

class ErrorCodes(Enum):
    UNAUTHORIZED = 'unauthorized'
    INVALID_INPUT = 'invalid_input'
    FORBIDDEN = 'forbidden'
    NOT_FOUND = 'not_found'
    ALREADY_EXISTS = 'already_exists'
    USER_DOES_NOT_EXIST = 'user_does_not_exist'
    INCORRECT_PASSWORD = 'incorrect_password'
    INVALID_TOKEN = 'invalid_token'
    EXPIRED_TOKEN = 'expired_token'
    VALIDATION_FAILED = 'validation_failed'
    USER_BLOCKED = 'user_blocked'
    PERMISSION_DENIED = 'permission_denied'
    METHOD_NOT_ALLOWED = 'method_not_allowed'
    NOT_VERIFIED = 'not_verified'
    TEST_ALREADY_TAKEN = 'test_already_taken'
    OTP_EXPIRED='otp_expired'

ERROR_MESSAGES = {
    ErrorCodes.UNAUTHORIZED: {
        "message": "Unauthorized access.",
        "status": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCodes.INVALID_INPUT: {
        "message": "Invalid input provided.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.FORBIDDEN: {
        "message": "Permission denied.",
        "status": status.HTTP_403_FORBIDDEN,
    },
    ErrorCodes.NOT_FOUND: {
        "message": "Resource not found.",
        "status": status.HTTP_404_NOT_FOUND,
    },
    ErrorCodes.ALREADY_EXISTS: {
        "message": "Resource already exists.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.USER_DOES_NOT_EXIST: {
        "message": "User does not exist.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.INCORRECT_PASSWORD: {
        "message": "Incorrect password.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.INVALID_TOKEN: {
        "message": "Invalid token provided.",
        "status": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCodes.EXPIRED_TOKEN: {
        "message": "Token has expired.",
        "status": status.HTTP_401_UNAUTHORIZED,
    },
    ErrorCodes.VALIDATION_FAILED: {
        "message": "Validation failed for the provided input.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.USER_BLOCKED: {
        "message": "User account is blocked.",
        "status": status.HTTP_403_FORBIDDEN,
    },
    ErrorCodes.PERMISSION_DENIED: {
        "message": "You do not have permission to perform this action.",
        "status": status.HTTP_403_FORBIDDEN,
    },
    ErrorCodes.METHOD_NOT_ALLOWED: {
        "message": "Method not allowed.",
        "status": status.HTTP_405_METHOD_NOT_ALLOWED,
    },
    ErrorCodes.NOT_VERIFIED: {
        "message": "User not verified.",
        "status": status.HTTP_403_FORBIDDEN,
    },
    ErrorCodes.TEST_ALREADY_TAKEN: {
        "message": "Test has already been taken by the user.",
        "status": status.HTTP_400_BAD_REQUEST,
    },
    ErrorCodes.OTP_EXPIRED:{
        "message":"OTP muddati tugagan yoki mavjud emas.",
        "status":status.HTTP_400_BAD_REQUEST,
    }
}

def get_error_details(error_code: ErrorCodes):
    return ERROR_MESSAGES.get(
        error_code,
        {"message": "An unknown error occurred.", "status": status.HTTP_500_INTERNAL_SERVER_ERROR},
    )
