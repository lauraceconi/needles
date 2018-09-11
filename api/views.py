# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action, list_route
from rest_framework.response import Response
from api.models import (Usuario,
                        Grupo,
                        Diario, 
                        LocalDeInteresse,
                        Relacionamento,
                        Recomendacao)
from api.permissions import IsOwnerOrReadOnly, IsGrupoDono, IsGrupoMembro
from api.serializers import (UsuarioSerializer, 
                             GrupoSerializer,
                             DetalheGrupoSerializer,
                             DiarioSerializer,
                             CadastroUsuariosSerializer,
                             LocalDeInteresseSerializer,
                             DetalheDiarioSerializer,
                             RelacionamentoSerializer,
                             PerfilSerializer,
                             RecomendacaoSerializer)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Viewset para listar todos os usuários (viewset de exemplo)
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    detail_serializer_class = UsuarioSerializer
    permission_classes = (permissions.AllowAny,)


class GrupoViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar um grupo
    """
    queryset = Grupo.objects.all()
    serializer_class = GrupoSerializer
    detail_serializer_class = DetalheGrupoSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsGrupoMembro)

    def perform_create(self, serializer):
        serializer.save(dono=self.request.user.usuario,
                        membros=[self.request.user.usuario])

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(GrupoViewSet, self).dispatch(request, pk=pk)

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class

    # @action(methods=['PATCH'], 
    #         detail=True, 
    #         url_path='add-membros', 
    #         permission_classes=[permissions.IsAuthenticated], isGrupoDono)
    # def seguir(self, request, pk=None):


class RecomendacaoViewSet(viewsets.ModelViewSet):
    """
    Viewset para cadastro de uma recomendação
    """
    queryset = Recomendacao.objects
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RecomendacaoSerializer

    def perform_create(self, serializer):
        grupo = serializer.get('grupo', None)
        serializer.save(autor=self.request.user.usuario,
                        grupo=grupo)


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
    queryset = Usuario.objects
    serializer_class = PerfilSerializer
    list_serializer_class = PerfilSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        return Response(self.list_serializer_class(instance=request.user.usuario).data,
                        status=status.HTTP_200_OK)


class RelacionamentoViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar a relação de seguidor
    entre os usuários
    """
    queryset = Relacionamento.objects
    serializer_class = RelacionamentoSerializer
    list_serializer_class = RelacionamentoSerializer
    permission_classes = (permissions.AllowAny,)

    @action(methods=['POST', 'PATCH'], 
            detail=True, 
            url_path='seguir', 
            permission_classes=[permissions.IsAuthenticated])
    def seguir(self, request, pk=None):
        relacao = Relacionamento.objects.filter(usuario=request.user.usuario,
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
            usuario_seguir = get_object_or_404(Usuario, id=pk)
            self.queryset.create(
                usuario=request.user.usuario,
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
        serializer.save(autor=self.request.user.usuario)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(DiarioViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):
        queryset = super(DiarioViewSet, self).get_queryset()
        return queryset.filter(autor=self.request.user.usuario)

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


class FeedViewSet(viewsets.ViewSet):
    def list(self, request):
        seguindo = [usuario.seguindo.id for usuario in Relacionamento.objects.filter(usuario=request.user.usuario)]
        diarios_seguindo = Diario.objects.filter(autor__in=seguindo)
        from IPython import embed;embed()
        diarios_serializer = DiarioSerializer(data=diarios_seguindo)
        return Response(diarios_serializer)
