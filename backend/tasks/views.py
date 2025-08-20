from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User, Category, Task
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    CategorySerializer, TaskSerializer, TaskCreateSerializer,
    TaskUpdateSerializer, TaskStatisticsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own profile"""
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class CategoryViewSet(viewsets.ModelViewSet):
    """Category management viewset"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return categories for current user only"""
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Auto-assign current user when creating category"""
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """Task management viewset"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-priority', 'due_date', '-created_at']

    def get_queryset(self):
        """Return tasks for current user only"""
        queryset = Task.objects.filter(user=self.request.user)

        # Additional filtering options
        status_filter = self.request.query_params.get('status_filter', None)
        if status_filter == 'overdue':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )
        elif status_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date=today)
        elif status_filter == 'this_week':
            start_week = timezone.now().date()
            end_week = start_week + timedelta(days=7)
            queryset = queryset.filter(due_date__date__range=[
                                       start_week, end_week])

        return queryset

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """Auto-assign current user when creating task"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
        """Mark task as pending"""
        task = self.get_object()
        task.status = 'pending'
        task.completed_at = None
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics for current user"""
        user_tasks = Task.objects.filter(user=request.user)

        total_tasks = user_tasks.count()
        pending_tasks = user_tasks.filter(status='pending').count()
        in_progress_tasks = user_tasks.filter(status='in_progress').count()
        completed_tasks = user_tasks.filter(status='completed').count()

        # Calculate overdue tasks
        overdue_tasks = user_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()

        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks *
                           100) if total_tasks > 0 else 0

        # Tasks by priority
        priority_stats = user_tasks.values(
            'priority').annotate(count=Count('id'))
        tasks_by_priority = {str(item['priority']): item['count']
                             for item in priority_stats}

        # Tasks by category
        category_stats = user_tasks.filter(category__isnull=False).values(
            'category__name'
        ).annotate(count=Count('id'))
        tasks_by_category = {item['category__name']                             : item['count'] for item in category_stats}

        statistics_data = {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round(completion_rate, 2),
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_category': tasks_by_category,
        }

        serializer = TaskStatisticsSerializer(statistics_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today"""
        today = timezone.now().date()
        today_tasks = self.get_queryset().filter(due_date__date=today)
        serializer = self.get_serializer(today_tasks, many=True)
        return Response(serializer.data)

# Authentication Views


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create auth token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """User logout endpoint"""
    try:
        # Delete the token to force re-authentication
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """Get dashboard summary data"""
    user_tasks = Task.objects.filter(user=request.user)
    user_categories = Category.objects.filter(user=request.user)

    # Recent tasks (last 5)
    recent_tasks = user_tasks.order_by('-created_at')[:5]

    # Upcoming tasks (next 5 by due date)
    upcoming_tasks = user_tasks.filter(
        due_date__gte=timezone.now(),
        status__in=['pending', 'in_progress']
    ).order_by('due_date')[:5]

    summary_data = {
        'total_tasks': user_tasks.count(),
        'total_categories': user_categories.count(),
        'completed_today': user_tasks.filter(
            completed_at__date=timezone.now().date()
        ).count(),
        'overdue_count': user_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count(),
        'recent_tasks': TaskSerializer(recent_tasks, many=True).data,
        'upcoming_tasks': TaskSerializer(upcoming_tasks, many=True).data,
    }

    return Response(summary_data)
