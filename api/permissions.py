# -*- coding: utf-8 -*-
from rest_framework import permissions
from api.models import Grupo


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.autor == request.user.usuario


class IsGrupoDono(permissions.BasePermission):
    """
    Verifica se o usuário é dono do grupo
    """
    def has_object_permission(self, request, view, obj):
        return obj.dono == request.user.usuario


class IsGrupoMembro(permissions.BasePermission):
    """
    Verifica se o usuário é membro do grupo
    """
    def has_object_permission(self, request, view, obj):
        return request.user.usuario in obj.membros.all()


class PermissaoRecomendacao(permissions.BasePermission):
    """
    Verifica se o usuário faz parte de algum grupo que
    pode visualizar a recomendação
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        grupos_recomendacao = obj.grupos.all()
        grupos_usuario = Grupo.objects.filter(
            membros__id=request.user.usuario.id
        )
        for grupo in grupos_recomendacao:
            return grupo in grupos_usuario
        
class PermissaoDiario(permissions.BasePermission):
    """
    Verifica se o usuário faz parte de algum grupo que tem
    visualização sobre a recomendação em que foi 
    associado esse diário
    """
    def has_object_permission(self, request, view, obj):
        grupos_usuario = Grupo.objects.filter(
            membros__id=request.user.usuario.id
        )
        for recomendacao in obj.recomendacao_set.all():
            for grupo in recomendacao.grupos.all():
                return grupo in grupos_usuario
