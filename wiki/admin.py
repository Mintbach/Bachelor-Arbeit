
# Register your models here.
from django.contrib import admin
from .models import Issue, Argument, Premise, Conclusion


admin.site.register(Issue)
admin.site.register(Argument)
admin.site.register(Premise)
admin.site.register(Conclusion)
