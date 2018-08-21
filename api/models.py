# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Diario(models.Model):
    autor = models.ForeignKey('auth.User', related_name='diarios', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)

    def __unicode__(self):
        return self.titulo


class LocalDeInteresse(models.Model):
    diario = models.ForeignKey(Diario,
                               on_delete=models.CASCADE,
                               verbose_name='Diário')
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True, null=True)
    latitude = models.FloatField('Latitude', blank=True, null=True)
    longitude = models.FloatField('Longitude', blank=True, null=True)
    #fotos

    def __unicode__(self):
        return self.nome


    


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)