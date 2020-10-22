from django.contrib import admin

from .models import Person


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'is_vector')
    empty_value_display = '-пусто-'

admin.site.register(Person, PersonAdmin)