from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extends the built-in User with the role needed across all 24 user stories."""

    ROLE_JOB_SEEKER = "job_seeker"
    ROLE_RECRUITER = "recruiter"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_JOB_SEEKER, "Job Seeker"),
        (ROLE_RECRUITER, "Recruiter"),
        (ROLE_ADMIN, "Administrator"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_JOB_SEEKER)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_recruiter(self):
        return self.role == self.ROLE_RECRUITER

    @property
    def is_job_seeker(self):
        return self.role == self.ROLE_JOB_SEEKER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
