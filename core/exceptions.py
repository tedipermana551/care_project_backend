from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data if isinstance(response.data, dict) else {'detail': response.data}
        message = errors.pop('detail', 'an error occurred')
        if hasattr(message, 'code'):
            message = str(message)

        response.data = {
            'success': False,
            'message': message,
            'errors': errors,
        }

    return response

def success_response(data=None, message= 'Success', status=200):
    return Response({'success': True, 'message': message, 'data': data or {}}, status=status)