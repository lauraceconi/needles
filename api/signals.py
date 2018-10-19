from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Relacionamento
from api.utils import enviar_notificacao


@receiver(post_save, sender=Relacionamento)
def criar_notificacao_relacionamento(sender, **kwargs):
    from IPython import embed;embed()
    enviar_notificacao()

