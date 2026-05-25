from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.events.models import Event, Category
from apps.registrations.models import Registration

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'role', 'avatar', 'bio', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'color']


class EventListSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    available_spots = serializers.ReadOnlyField()
    occupancy_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'organizer', 'category',
            'event_type', 'start_date', 'end_date', 'location', 'max_capacity',
            'current_attendees', 'available_spots', 'occupancy_percentage',
            'cover_image', 'status', 'is_public', 'is_free', 'price', 'created_at'
        ]


class EventDetailSerializer(EventListSerializer):
    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ['description', 'address', 'virtual_link', 'virtual_platform', 'tags', 'updated_at']


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'category', 'event_type',
            'start_date', 'end_date', 'location', 'address', 'virtual_link',
            'virtual_platform', 'max_capacity', 'cover_image', 'is_public',
            'is_free', 'price', 'tags', 'status'
        ]

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError('La fecha de fin debe ser posterior al inicio.')
        return data

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    event = EventListSerializer(read_only=True)
    event_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'event', 'event_id', 'status', 'checked_in', 'confirmation_code', 'registration_date']
        read_only_fields = ['id', 'status', 'checked_in', 'confirmation_code', 'registration_date']

    def create(self, validated_data):
        from apps.events.models import Event
        from apps.registrations.services import RegistrationService
        event = Event.objects.get(id=validated_data['event_id'])
        user = self.context['request'].user
        return RegistrationService.register_user(user, event)
