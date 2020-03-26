from django.db import models
from mesika_utils.RandomTransactionIds import generate_sso_token

# Create your models here.


class Channel(models.Model):
    channel_name = models.CharField(max_length=120, default="SMS")
    channel_description = models.TextField(default="N/A")
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.channel_name}"


class Messages(models.Model):

    CHOICES = (
        ('PENDING', 'Pending Message'),
        ('SUBMITTED', 'Submitted Message'),
        ('DELIVERED', 'Delivered Message'),
        ('FAILED', 'Failed Message'),
    )

    message_id = models.CharField(primary_key=True, max_length=120, default=generate_sso_token, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    subject = models.CharField(max_length=120, default="MeSika")
    source = models.CharField(max_length=120, default="MeSika")
    content = models.TextField("N/A")
    destination = models.CharField(max_length=120)
    trx_id = models.CharField(max_length=120, blank=True, null=True, default=generate_sso_token)
    app_id = models.CharField(max_length=120, null=True, blank=True, default=generate_sso_token)
    message_status = models.CharField(max_length=120, default="PENDING", choices=CHOICES)
    date_submitted = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_details(self):

        details = {
            "channel": self.channel.channel_name,
            "message_id": self.message_id,
            "content": self.content,
            "source": self.source,
            "destination": self.destination,
            "date_submitted": self.date_submitted,
            "message_status": self.message_status,
            "last_update": self.last_update
        }

        return details

    def __str__(self):
        return f"{self.message_id} {self.content} {self.destination} {self.message_status}"

    class Meta:
        verbose_name_plural = "Messages"
        verbose_name = "Messages"
