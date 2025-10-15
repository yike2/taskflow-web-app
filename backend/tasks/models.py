from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Extended user model with additional fields"""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Task category model"""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color code
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'user']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    """Core task model"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    # Basic fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)

    # Relationship fields
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    # Time fields
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']

        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'due_date']),
        ]

    def save(self, *args, **kwargs):
        """Auto-set completion time when task is marked as completed"""
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False

    def __str__(self):
        return self.title
