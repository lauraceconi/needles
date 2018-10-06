# -*- coding: utf-8 -*-
from rest_framework import serializers
from api.models import (Usuario,
                        Grupo,
                        Diario, 
                        LocalDeInteresse, 
                        Relacionamento,
                        Recomendacao)


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer de exemplo
    """
    diarios = serializers.PrimaryKeyRelatedField(many=True, queryset=Diario.objects.all())

    class Meta:
        model = Usuario
        fields = ('id', 'username', 'diarios')


class PerfilSerializer(serializers.ModelSerializer):
    seguindo = serializers.SerializerMethodField()
    seguidores = serializers.SerializerMethodField()

    def get_seguindo(self, obj):
        return obj.relacionamento_set.count()

    def get_seguidores(self, obj):
        return Relacionamento.objects.filter(seguindo=obj).count()

    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 
                  'email', 'foto', 'seguindo', 'seguidores')


class GrupoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grupo
        fields = ('id', 'name')


class DetalheGrupoSerializer(serializers.ModelSerializer):
    membros = PerfilSerializer(many=True)
    dono = PerfilSerializer()

    class Meta:
        model = Grupo
        fields = ('id', 'name', 'dono', 'membros')


class RecomendacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recomendacao
        fields = ('id', 'descricao', 'grupo')


class CadastroUsuariosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ('id', 'email', 'password', 'first_name', 'last_name')


class LocalDeInteresseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalDeInteresse
        fields = ('id', 'nome', 'descricao', 'latitude', 'longitude', 'foto')


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