from rest_framework import serializers
from .models import *


class PersonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Person
        fields = ['id']


class InfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'is_vector']