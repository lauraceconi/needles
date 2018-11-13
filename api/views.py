# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.core.exceptions import SuspiciousOperation
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
                        Recomendacao,
                        Notificacao)
from api.permissions import (IsOwnerOrReadOnly, 
                             IsGrupoDono, 
                             IsGrupoMembro, 
                             PermissaoDiario,
                             PermissaoRecomendacao)
from api.serializers import (UsuarioSerializer, 
                             GrupoSerializer,
                             DetalheGrupoSerializer,
                             DiarioSerializer,
                             CadastroUsuariosSerializer,
                             LocalDeInteresseSerializer,
                             DetalheDiarioSerializer,
                             RelacionamentoSerializer,
                             PerfilSerializer,
                             DetalhePerfilSerializer,
                             RecomendacaoSerializer,
                             DetalheRecomendacaoSerializer,
                             NotificacaoSerializer,
                             FeedSerializer)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Viewset para listar todos os usuários
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    detail_serializer_class = UsuarioSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UsuarioLogadoViewSet(viewsets.ViewSet):
    """
    Viewset para listar os dados do usuário logado
    """
    queryset = Usuario.objects.all()
    list_serializer_class = UsuarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        return Response(self.list_serializer_class(instance=request.user.usuario).data,
                        status=status.HTTP_200_OK)


class GrupoViewSet(viewsets.ModelViewSet):
    """
    Viewset para criar um grupo
    """
    queryset = Grupo.objects.all()
    list_serializer_class = GrupoSerializer
    detail_serializer_class = DetalheGrupoSerializer
    permission_classes = (IsGrupoMembro,)        

    def perform_create(self, serializer):
        (serializer.validated_data['membros']).append(self.request.user.usuario)
        membros = serializer.validated_data['membros']        
        serializer.save(dono=self.request.user.usuario,
                        membros=membros)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(GrupoViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):
        super(GrupoViewSet, self).get_queryset()        
        return Grupo.objects.filter(membros__id=self.request.user.usuario.id)

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class


class RecomendacaoViewSet(viewsets.ModelViewSet):
    """
    Viewset para cadastro de uma recomendação
    """
    queryset = Recomendacao.objects.all()
    serializer_class = RecomendacaoSerializer
    list_serializer_class = RecomendacaoSerializer
    detail_serializer_class = DetalheRecomendacaoSerializer
    permission_classes = (permissions.IsAuthenticated,
                          PermissaoRecomendacao)

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user.usuario)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(RecomendacaoViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):        
        if not self.pk:
            return self.request.user.usuario.recomendacoes.all()
        return super(RecomendacaoViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class

    @action(methods=['POST'], 
            detail=True, 
            url_path='sugerir-diario', 
            permission_classes=[
                permissions.IsAuthenticated,
            ])
    def sugerir_diario(self, request, pk=None):
        recomendacao = self.get_object()
        recomendacao.diarios = request.data['diarios']
        recomendacao.save()
        resposta = 'Sucesso! A sugestão foi salva. '
        status_resposta = status.HTTP_200_OK
        return Response(resposta, status=status_resposta)


class CadastroViewSet(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    Viewset para cadastrar um novo usuário
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = CadastroUsuariosSerializer

    def perform_create(self, serializer):
        # Faz o username ser igual ao email
        # para facilitar o login, que requer username
        username = serializer.validated_data['email']
        instance = serializer.save(username=username)
        instance.set_password(instance.password)
        instance.save()


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = PerfilSerializer
    list_serializer_class = PerfilSerializer
    detail_serializer_class = DetalhePerfilSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, id=pk)
        try:
            sigo = instance.seguindo.get(usuario=request.user.usuario)
            instance.sigo = True
            instance.classificacao_id = sigo.classificacao_id
        except Relacionamento.DoesNotExist:
            instance.sigo = False

        try:
            me_segue = request.user.usuario.seguindo.get(usuario=instance)
            instance.me_segue = True
        except Relacionamento.DoesNotExist:
            instance.me_segue = False

        return Response(
            self.detail_serializer_class(
                instance=instance, 
                context = { 'request': request }
            ).data,
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
            if serializer.is_valid(raise_exception=True):
                relacao.classificacao_id = serializer.validated_data['classificacao_id']
                relacao.save()
                resposta = 'Sucesso! A classificação foi modificada. '
                status_resposta = status.HTTP_200_OK
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
    permission_classes = (permissions.IsAuthenticated, 
                          PermissaoDiario)

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user.usuario)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(DiarioViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):
        if not self.pk:
            return self.queryset.filter(autor=self.request.user.usuario)
        return super(DiarioViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class

    @action(methods=['POST'], detail=True, url_path='cria-local')
    def cria_local(self, request, pk=None):
        """
        Função para criar um Local de Interesse em um Diário
        """
        diario = self.get_object()
        serializer = LocalDeInteresseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(diario=diario)
            resposta = 'Local de Interesse criado com sucesso!'
            status_resposta = status.HTTP_200_OK        
        return Response(resposta, status=status_resposta)


class LocalViewSet(viewsets.ModelViewSet):
    queryset = LocalDeInteresse.objects
    list_serializer_class = LocalDeInteresseSerializer
    detail_serializer_class = LocalDeInteresseSerializer

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(LocalViewSet, self).dispatch(request, pk=pk)

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class


class FeedViewSet(viewsets.ViewSet):
    def list(self, request):
        dados = { 'recomendacoes': [] }
        grupos = Grupo.objects.filter(membros__id=self.request.user.usuario.id)
        for grupo in grupos:
            for recomendacao in grupo.recomendacao_set.all():
                dados['recomendacoes'].append(recomendacao)
        dados_serializados = FeedSerializer(
            dados, 
            context = { 'request': request }
        ).data
        return Response(
            dados_serializados['recomendacoes'], 
            status=status.HTTP_200_OK
        )


class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects
    serializer_class = NotificacaoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):        
        serializer.save(usuario=self.request.user.usuario,
                        user_id=serializer.validated_data['user_id'])