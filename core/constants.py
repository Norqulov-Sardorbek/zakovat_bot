from click_up import ClickUp
from decouple import config
from rest_framework.pagination import PageNumberPagination
from sms_service.models import SMSToken
import requests
CLICK_SERVICE_ID = config("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = config("CLICK_MERCHANT_ID")
ESKIZ_EMAIL = config("ESKIZ_EMAIL")
ESKIZ_PASSWORD = config("ESKIZ_PASSWORD")

click_up = ClickUp(service_id=CLICK_SERVICE_ID, merchant_id=CLICK_MERCHANT_ID)
class CustomPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    
COLOR_CHOICES = (
    ("white", "Oq"),
    ("black", "Qora"),
    ("gray", "Kulrang"),
    ("red", "Qizil"),
    ("green", "Yashil"),
    ("blue", "Ko‘k"),
    ("yellow", "Sariq"),
    ("orange", "To‘q sariq"),
    ("pink", "Pushti"),
    ("violet", "Binafsha"),
    ("brown", "Jigarrang"),
    ("gold", "Oltin"),
    ("silver", "Kumush"),
)


def get_eskiz_token():
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {
        "email": ESKIZ_EMAIL,
        "password": ESKIZ_PASSWORD
    }
    response = requests.post(url, json=payload)
    response_data = response.json()
    token = response_data.get("data", {}).get("token")
    SMSToken.objects.create(token=token, is_active=True)
    return token
    