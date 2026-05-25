from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.events.models import Event, Category
from apps.registrations.models import Registration
from .serializers import (
    EventListSerializer, EventDetailSerializer, EventCreateSerializer,
    CategorySerializer, RegistrationSerializer
)
from .permissions import IsOrganizerOrReadOnly, IsOwnerOrReadOnly


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'event_type', 'status', 'is_public', 'is_free']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at', 'title']
    ordering = ['start_date']

    def get_queryset(self):
        qs = Event.objects.select_related('organizer', 'category')
        if self.request.user.is_authenticated and self.request.user.is_organizer:
            return qs
        return qs.filter(status='published', is_public=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        return EventDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        from apps.registrations.services import RegistrationService
        try:
            reg = RegistrationService.register_user(request.user, event)
            return Response(RegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_admin:
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
        regs = Registration.objects.filter(event=event).select_related('user')
        from .serializers import RegistrationSerializer
        return Response(RegistrationSerializer(regs, many=True).data)


class RegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return (
            Registration.objects
            .filter(user=self.request.user)
            .select_related('event', 'event__organizer', 'event__category')
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        from apps.registrations.services import RegistrationService
        try:
            RegistrationService.cancel_registration(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
