# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from api.models import Diario, LocalDeInteresse

# Register your models here.

class LocalDeInteresseInline(admin.TabularInline):
    model = LocalDeInteresse


class DiarioAdmin(admin.ModelAdmin):
    model = Diario
    inlines = [
        LocalDeInteresseInline,
    ]

admin.site.register(Diario, DiarioAdmin)