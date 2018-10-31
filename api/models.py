# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.dispatch import receiver

class Usuario(User):
    user = models.OneToOneField(User)
    foto = models.ImageField(upload_to='images', 
                             blank=True, 
                             null=True)


class Grupo(Group):
    group = models.OneToOneField(Group)
    dono = models.ForeignKey('Usuario')
    membros = models.ManyToManyField('Usuario', 
                                     related_name='membros')

    def recomendacoes(self):
        return self.recomendacao_set.all()


class Recomendacao(models.Model):
    """
    Model que representa uma solicitação de recomendação,
    que deve ser enviada aos seguidores do usuário ou
    para um grupo específico
    """
    autor = models.ForeignKey('Usuario', 
                              related_name='recomendacoes',
                              on_delete=models.CASCADE)
    descricao = models.TextField('Descrição')
    grupos = models.ManyToManyField('Grupo')
    seguidores = models.BooleanField(default=True)
    # diarios = models.ManyToManyField('Diario')

    def __unicode__(self):
        return self.descricao


class Classificacao(models.Model):
    """
    Classificação da relação entre os usuários
    """
    CLASSIFICACAO_CHOICES = (
        (1, 'Amigo'),
        (2, 'Conhecido'),
        (3, 'Não conheço'),
        (4, 'Inimigo')
    )
    descricao = models.CharField(
        'Descrição', 
        max_length=30,
        choices=CLASSIFICACAO_CHOICES
    )

    def __unicode__(self):
        return self.descricao


class Relacionamento(models.Model):
    """
    Relacionamento entre os usuários (seguindo/seguidores)
    """
    usuario = models.ForeignKey(Usuario)
    seguindo = models.ForeignKey(Usuario, related_name='seguindo')
    classificacao = models.ForeignKey(Classificacao)
    
    class Meta:
        unique_together = ('usuario', 'seguindo')


class Diario(models.Model):
    """
    Representação de um Diário de Viagens
    """
    autor = models.ForeignKey(Usuario, 
                              related_name='diarios', 
                              on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)

    def __unicode__(self):
        return self.titulo


class LocalDeInteresse(models.Model):
    """
    Representação de um Local de Interesse,
    que é associado a um Diário
    """
    diario = models.ForeignKey(Diario,
                               on_delete=models.CASCADE,
                               verbose_name='Diário',
                               related_name='locais_de_interesse')
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True, null=True)
    latitude = models.FloatField('Latitude', blank=True, null=True)
    longitude = models.FloatField('Longitude', blank=True, null=True)
    foto = models.ImageField(upload_to='images', 
                             blank=True, 
                             null=True) 

    def __unicode__(self):
        return self.nome


class Notificacao(models.Model):
    usuario = models.ForeignKey(Usuario,
                                on_delete=models.CASCADE)
    user_id = models.CharField('User ID',
                               max_length=100)
    ativo = models.BooleanField(default=True)

    def __unicode__(self):
        return self.usuario.get_full_name()

    class Meta:
        verbose_name_plural = 'Notificações'