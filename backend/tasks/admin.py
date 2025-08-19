from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Task


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin interface"""
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin interface"""
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    ordering = ['-created_at']

    # Hide user field from the form
    fields = ['name', 'color']

    def save_model(self, request, obj, form, change):
        """Auto-assign current user when creating new category"""
        if not obj.pk:  # Only for new objects (no primary key yet)
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Filter categories by current user if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Task admin interface"""
    list_display = [
        'title',
        'user',
        'status',
        'priority',
        'category',
        'due_date',
        'created_at'
    ]
    list_filter = [
        'status',
        'priority',
        'category',
        'created_at',
        'due_date',
        'user'
    ]
    search_fields = ['title', 'description', 'user__username']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # Custom fieldsets without user field
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Task Details', {
            'fields': ('status', 'priority', 'category')
        }),
        ('Time Information', {
            'fields': ('due_date',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-assign current user when creating new task"""
        if not obj.pk:  # Only for new objects (no primary key yet)
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Filter tasks by current user if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
