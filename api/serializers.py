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
        fields = ('id', 'username', 'diarios')


#class DiarioExemploSerializer(serializers.ModelSerializer):
#    """
#    Serializer de exemplo
#    """
#    autor = serializers.ReadOnlyField(source='autor.username')
#    locais_de_interesse = LocalDeInteresseSerializer(many=True, read_only=True)
#
#    class Meta:
#        model = Diario
#        fields = ('id', 'titulo', 'autor', 'locais_de_interesse')


class CadastroUsuariosSerializer(serializers.ModelSerializer):
    """
    Serializer de cadastro de usuário
    - Username deve ser criado automaticamente, estilo UCS
    - Precisa incluir foto
    - Tentar mandar o nome completo e dps separar aqui
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')


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