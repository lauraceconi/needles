# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from api.models import Diario, LocalDeInteresse, Relacionamento

# Register your models here.

class DiarioAdmin(admin.ModelAdmin):
    model = Diario

admin.site.register(Diario, DiarioAdmin)

class LocalDeInteresseAdmin(admin.ModelAdmin):
    model = LocalDeInteresse

admin.site.register(LocalDeInteresse, LocalDeInteresseAdmin)

class RelacionamentoAdmin(admin.ModelAdmin):
    model = Relacionamento

admin.site.register(Relacionamento, RelacionamentoAdmin)