from rest_framework import serializers


def validate_username(value):
    if value == 'me':
        raise serializers.ValidationError(
            ('Имя me не может быть использовано.')
        )
