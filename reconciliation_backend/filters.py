import logging


class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Implement logic to filter or mask sensitive data
            sensitive_keywords = [
                'business_name',
                'admin_name',
                'business_registration_number',
                'email',
                'password',
                'gampID',
            ]
            for keyword in sensitive_keywords:
                if keyword in record.msg:
                    record.msg = record.msg.replace(keyword, '[SENSITIVE DATA]')
        return True
