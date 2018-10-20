# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Usuario, Relacionamento, Notificacao
from api.utils import enviar_notificacao


@receiver(post_save, sender=Usuario)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Relacionamento)
def criar_notificacao_relacionamento(sender, instance=None, created=False, **kwargs):
    try:
        user_enviar = Notificacao.objects.get(usuario=instance.seguindo)
        notificacao = {
            'titulo': 'Novo seguidor',
            'mensagem': u'%s começou a seguir você' % instance.usuario.get_full_name(),
            'url': 'perfil/%s' % instance.usuario.id,
            'user_id': user_enviar.user_id
        }
        enviar_notificacao(notificacao)
    except Exception as inst:
        print inst

