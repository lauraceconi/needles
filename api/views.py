# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.shortcuts import render
from api.models import Diario
from api.permissions import IsOwnerOrReadOnly
from api.serializers import DiarioSerializer, UserSerializer, CadastroUsuariosSerializer
from rest_framework import viewsets, permissions, mixins

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset para listar todos os usuários (viewset de exemplo)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class DiarioViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar um Diário de Viagem
    """
    queryset = Diario.objects
    serializer_class = DiarioSerializer

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

    def get_queryset(self):
        queryset = super(DiarioViewSet, self).get_queryset()
        return queryset.filter(autor=self.request.user)


class CadastroViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer


