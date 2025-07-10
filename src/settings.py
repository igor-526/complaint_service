import os

YA_CLOUD_IAM_TOKEN = os.environ.get('YA_CLOUD_IAM_TOKEN')
YA_CLOUD_OAUTH_TOKEN = os.environ.get('YA_CLOUD_OAUTH_TOKEN')
YA_CLOUD_CATALOG_ID = os.environ.get('YA_CLOUD_CATALOG_ID')
AI_COMPLAINT_CATEGORY_PROMT = os.environ.get(
    'AI_COMPLAINT_CATEGORY_PROMT', 'Определи категорию жалобы'
)
AI_COMPLAINT_SENTIMENT_PROMT = os.environ.get(
    'AI_COMPLAINT_SENTIMENT_PROMT', 'Определи тональность жалобы'
)
AI_SPAM_PROMT = os.environ.get(
    'AI_SPAM_PROMT', 'Это сервис для приёма жалоб. '
                     'Определи наличие спама в тексте'
)

HTTP_CONNECTION_TIMEOUT = float(os.environ.get('HTTP_CONNECTION_TIMEOUT', 5))
HTTP_CONNECTION_RETRY_DELAY = float(os.environ.get(
    'HTTP_CONNECTION_RETRY_DELAY', 5
))
HTTP_CONNECTION_RETRIES = int(os.environ.get('HTTP_CONNECTION_RETRIES', 5))
