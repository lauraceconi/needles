# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'cadastro', views.CadastroViewSet, base_name='cadastro')
router.register(r'grupos', views.GrupoViewSet)
router.register(r'diarios', views.DiarioViewSet)
router.register(r'locais', views.LocalViewSet)
router.register(r'relacionamentos', views.RelacionamentoViewSet)
router.register(r'recomendacoes', views.RecomendacaoViewSet)
#router.register(r'usuarios', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^perfil/', views.PerfilViewSet.as_view({ 'get': 'list' })),
    url(r'^feed/', views.FeedViewSet.as_view({ 'get': 'list' }))
]

#urlpatterns = format_suffix_patterns(urlpatterns)