import uuid
from django.db import models


class Club(models.Model):
    """Represents a student club or organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('pending_approval', 'Pending Approval'),
            ('inactive', 'Inactive'),
        ],
        default='pending_approval',
    )
    member_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    """Represents a user's membership in a club."""
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('officer', 'Officer'),
        ('advisor', 'Advisor'),
    ]
    id = models.AutoField(primary_key=True)
    club = models.ForeignKey(Club, related_name='members', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('club', 'user_id')

    def save(self, *args, **kwargs) -> None:
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            Club.objects.filter(pk=self.club_id).update(member_count=models.F('member_count') + 1)

    def __str__(self) -> str:
        return f"{self.user_name} ({self.role})"