from django.contrib import admin
from .models import Attendance, Student,Session,Class,Record,Teacher,Term,Arm,NOK,Profile,Role,CSV,Subject,AllClass,Card
# Register your models here.

admin.site.register(Student)
admin.site.register(Session)
admin.site.register(Class)
admin.site.register(Record)
admin.site.register(Teacher)
admin.site.register(Arm)
admin.site.register(Term)
admin.site.register(NOK)
admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(CSV)
admin.site.register(Subject)
admin.site.register(AllClass)
admin.site.register(Attendance)
admin.site.register(Card)