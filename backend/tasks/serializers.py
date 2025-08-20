from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Category, Task


class UserSerializer(serializers.ModelSerializer):
    """User serializer for user information"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'password', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        """Create user with encrypted password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password', 'password_confirm']

    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials"""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError(
                        "User account is disabled")
            else:
                raise serializers.ValidationError(
                    "Invalid username or password")
        else:
            raise serializers.ValidationError(
                "Must provide username and password")

        return data


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    user = serializers.StringRelatedField(read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'user', 'task_count', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_task_count(self, obj):
        """Get number of tasks in this category"""
        try:
            return obj.task_set.count()
        except:
            return 0


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer - simplified version"""
    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'user', 'category', 'category_name',
            'due_date', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'completed_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Task creation serializer with minimal fields"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'status',
                  'priority', 'category', 'due_date']

    def validate_category(self, value):
        """Ensure category belongs to current user"""
        request = self.context.get('request')
        if value and value.user != request.user:
            raise serializers.ValidationError(
                "You can only assign tasks to your own categories")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Task update serializer"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'status',
                  'priority', 'category', 'due_date']

    def validate_category(self, value):
        """Ensure category belongs to current user"""
        request = self.context.get('request')
        if value and value.user != request.user:
            raise serializers.ValidationError(
                "You can only assign tasks to your own categories")
        return value


class TaskStatisticsSerializer(serializers.Serializer):
    """Task statistics serializer"""
    total_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    tasks_by_priority = serializers.DictField()
    tasks_by_category = serializers.DictField()
