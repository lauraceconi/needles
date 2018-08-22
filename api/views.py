# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action, list_route
from rest_framework.response import Response
from api.models import Diario, LocalDeInteresse
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (DiarioSerializer, 
                             UserSerializer, 
                             CadastroUsuariosSerializer,
                             LocalDeInteresseSerializer,
                             DetalheDiarioSerializer)

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

    @action(methods=['POST'], detail=True, url_path='cria-local')
    def cria_local(self, request, pk=None):
        diario = Diario.objects.filter(autor=request.user,
                                       id=pk).first()
        if diario:
            serializer = LocalDeInteresseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(diario=diario)
            resposta = 'Local de Interesse criado com sucesso!'
            status_resposta = status.HTTP_200_OK
        else:
            resposta = 'Você não tem permissão para criar ' \
                       'um Local de Interesse neste Diário.'
            status_resposta = status.HTTP_400_BAD_REQUEST
        
        return Response(resposta, status=status_resposta)


class CadastroViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer


