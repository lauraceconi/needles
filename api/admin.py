# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from api.models import Diario, LocalDeInteresse

# Register your models here.

class DiarioAdmin(admin.ModelAdmin):
    model = Diario

admin.site.register(Diario, DiarioAdmin)

class LocalDeInteresseAdmin(admin.ModelAdmin):
    model = LocalDeInteresse

admin.site.register(LocalDeInteresse, LocalDeInteresseAdmin)
