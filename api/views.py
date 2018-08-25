# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action, list_route
from rest_framework.response import Response
from api.models import (Diario, 
                        LocalDeInteresse,
                        Relacionamento)
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (DiarioSerializer, 
                             UserSerializer, 
                             CadastroUsuariosSerializer,
                             LocalDeInteresseSerializer,
                             DetalheDiarioSerializer,
                             RelacionamentoSerializer)

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset para listar todos os usuários (viewset de exemplo)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class RelacionamentoViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar a relação de seguidor
    entre os usuários
    """
    queryset = Relacionamento.objects
    serializer_class = RelacionamentoSerializer
    list_serializer_class = RelacionamentoSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST'], detail=True, url_path='seguir')
    def seguir(self, request, pk=None):
        usuario_seguir = get_object_or_404(User, id=pk)
        try:
            self.queryset.create(
                usuario=request.user,
                seguindo=usuario_seguir,
                classificacao_id=1
            )
            resposta = 'Sucesso! Agora você está seguindo ' \
                       '%s' % usuario_seguir.get_full_name()
            status_resposta = status.HTTP_200_OK
        except IntegrityError:
            resposta = 'Você já está seguindo esta pessoa.'
            status_resposta = status.HTTP_400_BAD_REQUEST
        
        return Response(resposta, status=status_resposta)


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


#class CadastroViewSet(mixins.CreateModelMixin,
#                      viewsets.GenericViewSet):
class CadastroViewSet(viewsets.ModelViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer

    def perform_create(request, serializer):
        #username = serializer.validated_data['first_name'][0] + serializer.validated_data['last_name']
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


