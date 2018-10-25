# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from api.models import (Usuario, 
                        Grupo, 
                        Diario, 
                        LocalDeInteresse, 
                        Relacionamento,
                        Notificacao)

class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ('username', 'email', 'first_name', 'last_name')

admin.site.register(Usuario, UsuarioAdmin)

class GrupoAdmin(admin.ModelAdmin):
    model = Grupo
    list_display = ('name', 'dono')

admin.site.register(Grupo, GrupoAdmin)

class DiarioAdmin(admin.ModelAdmin):
    model = Diario

admin.site.register(Diario, DiarioAdmin)

class LocalDeInteresseAdmin(admin.ModelAdmin):
    model = LocalDeInteresse

admin.site.register(LocalDeInteresse, LocalDeInteresseAdmin)

class RelacionamentoAdmin(admin.ModelAdmin):
    model = Relacionamento

admin.site.register(Relacionamento, RelacionamentoAdmin)

class NotificacaoAdmin(admin.ModelAdmin):
    model = Notificacao

admin.site.register(Notificacao, NotificacaoAdmin)