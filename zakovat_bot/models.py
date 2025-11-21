from django.db import models
from core.models.basemodel import SafeBaseModel
# Create your models here.




class TelegramAdminsID(SafeBaseModel):
    tg_id = models.BigIntegerField()

    def __str__(self):
        return self.tg_id

class Users(SafeBaseModel):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    tg_id = models.BigIntegerField()

    def __str__(self):
        return self.tg_id

class Questions(SafeBaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    questioned_at = models.DateTimeField(auto_now_add=True)
    answers_file_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Question from chat_id: {self.chat_id}"
    
class Answers(SafeBaseModel):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='answers')
    answer = models.CharField(max_length=100)
    answered_at = models.DateTimeField(auto_now_add=True)
    