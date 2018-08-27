# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Diario, LocalDeInteresse, Relacionamento


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer de exemplo
    """
    diarios = serializers.PrimaryKeyRelatedField(many=True, queryset=Diario.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username')


class CadastroUsuariosSerializer(serializers.ModelSerializer):
    """
    - Precisa incluir foto
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')


class LocalDeInteresseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalDeInteresse
        fields = ('id', 'nome', 'descricao', 'latitude', 'longitude')


class DiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diario
        fields = ('id', 'titulo')


class DetalheDiarioSerializer(serializers.ModelSerializer):
    locais_de_interesse = LocalDeInteresseSerializer(many=True, read_only=True)

    class Meta:
        model = Diario
        fields = ('id', 'titulo', 'locais_de_interesse')


class RelacionamentoSerializer(serializers.ModelSerializer):
    classificacao_id = serializers.IntegerField()

    class Meta:
        model = Relacionamento
        fields = ('classificacao_id',)


class PerfilSerializer(serializers.ModelSerializer):
    seguindo = serializers.SerializerMethodField()
    seguidores = serializers.SerializerMethodField()

    def get_seguindo(self, obj):
        return obj.relacionamento_set.count()

    def get_seguidores(self, obj):
        return Relacionamento.objects.filter(seguindo=obj).count()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 
                  'email', 'seguindo', 'seguidores')