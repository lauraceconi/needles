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
                             RelacionamentoSerializer,
                             PerfilSerializer)

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset para listar todos os usuários (viewset de exemplo)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    detail_serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class CadastroViewSet(viewsets.ModelViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer

    def perform_create(request, serializer):
        # Faz o username ser igual ao email
        # para facilitar o login, que requer username
        username = serializer.validated_data['email']
        instance = serializer.save(username=username)
        instance.set_password(instance.password)
        instance.save()


class PerfilViewSet(viewsets.ViewSet):
    queryset = User.objects
    serializer_class = PerfilSerializer
    list_serializer_class = PerfilSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        return Response(self.list_serializer_class(instance=request.user).data,
                        status=status.HTTP_200_OK)


class RelacionamentoViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar a relação de seguidor
    entre os usuários
    """
    queryset = Relacionamento.objects
    serializer_class = RelacionamentoSerializer
    list_serializer_class = RelacionamentoSerializer
    #update_serializer_class = RelacionamentoUpdateSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST', 'PATCH'], 
            detail=True, 
            url_path='seguir', 
            permission_classes=[permissions.IsAuthenticated])
    def seguir(self, request, pk=None):
        relacao = Relacionamento.objects.filter(usuario=request.user,
                                                seguindo=pk).first()
        if relacao and request.method == 'PATCH':
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid():
                relacao.classificacao_id = serializer.data['classificacao_id']
                relacao.save()
                resposta = 'Sucesso! A classificação foi modificada. '
                status_resposta = status.HTTP_200_OK
            else:
                resposta = serializer.errors
                status_resposta = status.HTTP_400_BAD_REQUEST
        elif not relacao and request.method == 'POST':
            usuario_seguir = get_object_or_404(User, id=pk)
            self.queryset.create(
                usuario=request.user,
                seguindo=usuario_seguir,
                classificacao_id=1
            )
            resposta = 'Sucesso! Agora você está seguindo ' \
                    '%s' % usuario_seguir.get_full_name()
            status_resposta = status.HTTP_200_OK
        else:
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
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

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
        diario = self.get_object()
        serializer = LocalDeInteresseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(diario=diario)
            resposta = 'Local de Interesse criado com sucesso!'
            status_resposta = status.HTTP_200_OK
        else:
            resposta = serializer.errors
            status_resposta = status.HTTP_400_BAD_REQUEST
        
        return Response(resposta, status=status_resposta)

