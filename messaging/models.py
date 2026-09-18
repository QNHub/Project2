from django.conf import settings
from django.db import models
from django.urls import reverse


class Conversation(models.Model):
    """
    A private in-platform thread between one Recruiter and one Candidate.
    Story 14: recruiters message candidates without needing personal emails.
    """

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_recruiter",
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_candidate",
    )
    subject = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("recruiter", "candidate")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recruiter} \u2194 {self.candidate}"

    def get_absolute_url(self):
        return reverse("messaging:conversation_detail", args=[self.pk])

    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def other_participant(self, user):
        return self.candidate if user_id_matches(user, self.recruiter) else self.recruiter

    def unread_count_for(self, user):
        return self.messages.exclude(sender=user).filter(is_read=False).count()


def user_id_matches(user, other):
    return user.pk == other.pk


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.body[:30]}"
