# Create your models here.

from django.db import models
from django.urls import reverse

class Meeting(models.Model):
    name = models.CharField("Meeting Name", max_length=100)
    bot_name = models.CharField("Bot Name", max_length=100)
    meeting_link = models.URLField("Link", blank=True)
    join_time = models.TimeField("Join Time", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.bot_name})"

    def get_absolute_url(self):
        return reverse('meeting_page', kwargs={'meeting_id': self.pk})