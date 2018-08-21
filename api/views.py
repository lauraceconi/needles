# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.shortcuts import render
from api.models import Diario
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (DiarioSerializer, 
                             UserSerializer, 
                             CadastroUsuariosSerializer,
                             DetalheDiarioSerializer)
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
    list_serializer_class = DiarioSerializer
    detail_serializer_class = DetalheDiarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(DiarioViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):
        queryset = super(DiarioViewSet, self).get_queryset()
        return queryset.filter(autor=self.request.user)

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class


class CadastroViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer


