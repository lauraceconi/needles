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
                        Recomendacao,
                        Notificacao)
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
                             DetalhePerfilSerializer,
                             RecomendacaoSerializer,
                             NotificacaoSerializer)

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
        return self.request.user.usuario.grupo_set.all()

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
    list_serializer_class = RecomendacaoSerializer
    detail_serializer_class = RecomendacaoSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        # TODO: COMPARTILHAR COM GRUPOS
        # grupo = serializer.get('grupo', None)
        serializer.save(autor=self.request.user.usuario)

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(RecomendacaoViewSet, self).dispatch(request, pk=pk)

    def get_queryset(self):        
        super(RecomendacaoViewSet, self).get_queryset()
        return self.request.user.usuario.recomendacoes.all()

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class


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
    queryset = Usuario.objects.all()
    serializer_class = PerfilSerializer
    list_serializer_class = PerfilSerializer
    detail_serializer_class = DetalhePerfilSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        return Response(self.list_serializer_class(instance=request.user.usuario).data,
                        status=status.HTTP_200_OK)

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

        return Response(self.detail_serializer_class(instance=instance).data,
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
        """
        Função para criar um Local de Interesse em um Diário
        """
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


class LocalViewSet(viewsets.ModelViewSet):
    queryset = LocalDeInteresse.objects
    list_serializer_class = LocalDeInteresseSerializer
    detail_serializer_class = LocalDeInteresseSerializer
    #permission_classes = permissions.IsAuthenticated

    def dispatch(self, request, pk=None):
        self.pk = pk
        return super(LocalViewSet, self).dispatch(request, pk=pk)

    def get_serializer_class(self):
        return self.list_serializer_class \
            if not self.pk else self.detail_serializer_class


class FeedViewSet(viewsets.ViewSet):
    def list(self, request):
        seguindo = [usuario.seguindo.id for usuario in Relacionamento.objects.filter(usuario=request.user.usuario)]
        diarios_seguindo = Diario.objects.filter(autor__in=seguindo)
        diarios_serializer = DiarioSerializer(data=diarios_seguindo)
        return Response(diarios_serializer)


class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects
    serializer_class = NotificacaoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):        
        serializer.save(usuario=self.request.user.usuario,
                        user_id=serializer.validated_data['user_id'])