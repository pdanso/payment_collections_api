from django.db import models
from mesika_utils.RandomTransactionIds import generate_application_no


class Messages(models.Model):
    CHOICES = (
        ('PENDING', 'Pending Message'),
        ('SUBMITTED', 'Submitted Message'),
        ('DELIVERED', 'Delivered Message'),
        ('FAILED', 'Failed Message'),
    )

    message_id = models.CharField(max_length=120, default=generate_application_no, primary_key=True, unique=True)
    transaction_id = models.CharField(max_length=250)
    subject = models.CharField(max_length=120, default="MESIKA")
    notification_content = models.TextField(default="N/A")
    notification_destination = models.CharField(max_length=120)
    notification_type = models.CharField(max_length=120)
    message_status = models.CharField(max_length=120, default="PENDING", choices=CHOICES)
    message_status_description = models.CharField(max_length=120, default="PENDING")
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.message_id} || {self.notification_content} || {self.notification_destination} || {self.message_status} || {self.date_added}"

    class Meta:
        verbose_name_plural = "Notifications"
        verbose_name = "Notifications"
