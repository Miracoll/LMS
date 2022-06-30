from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.template.defaultfilters import slugify
import uuid

# Create your models here.
today = date.today()
pat = today.strftime("%Y-%m-%d")

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    other_name = models.CharField(max_length=20)
    sex = models.CharField(max_length=20)
    dob = models.DateField()
    address = models.TextField(max_length=150)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    level = models.IntegerField(default=0)
    group = models.CharField(max_length=5, default='JS1')
    arm = models.CharField(max_length=5, default='A')
    active = models.IntegerField(default=1)
    passport = models.ImageField(upload_to='passport', default='passport.jpg')
    registration_number = models.CharField(max_length=10)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class NOK(models.Model):
    relationship = models.CharField(max_length=10)
    full_name = models.CharField(max_length=100)
    address = models.TextField(max_length=150)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

class Class(models.Model):
    group = models.CharField(max_length=10)
    category = models.CharField(max_length=20, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.group

class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    other_name = models.CharField(max_length=20)
    sex = models.CharField(max_length=20)
    dob = models.DateField()
    # subject = models.CharField(max_length=50)
    address = models.TextField(max_length=150)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    registration_number = models.CharField(max_length=10)
    active = models.IntegerField(default=1)
    passport = models.ImageField(upload_to='teacher_passport', default='passport.jpg')
    nok_relationship = models.CharField(max_length=10)
    nok_full_name = models.CharField(max_length=100)
    nok_address = models.TextField(max_length=150)
    nok_mobile = models.CharField(max_length=15)
    nok_email = models.EmailField(blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instangram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Subject(models.Model):
    subject = models.CharField(max_length=20)
    category = models.CharField(max_length=20, blank=True, null=True)
    teacher = models.CharField(max_length=15, blank=True, null=True)
    group = models.CharField(max_length=5, blank=True, null=True)
    arm = models.CharField(max_length=5, blank=True, null=True)
    owner = models.CharField(max_length=7, blank=True, null=True)
    upload = models.IntegerField(default=0)
    lock = models.IntegerField(default=0)
    total_student = models.IntegerField(blank=True, null=True)
    approve_result = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.group}{self.arm} {self.subject}'

class AllSubject(models.Model):
    subject = models.CharField(max_length=20)
    category = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject

class Term(models.Model):
    term = models.IntegerField()
    active = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.term} term'

class Arm(models.Model):
    # group = models.ForeignKey(Class, on_delete=models.CASCADE)
    arm = models.CharField(max_length=10)
    # class_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.arm} term'

class Session(models.Model):
    session = models.CharField(max_length=20)
    year = models.IntegerField()
    active = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.session

class Record(models.Model):
    CA1 = models.IntegerField(default=0, blank=True, null=True)
    CA2 = models.IntegerField(default=0, blank=True, null=True)
    CA3 = models.IntegerField(default=0, blank=True, null=True)
    project = models.IntegerField(default=0, blank=True, null=True)
    test = models.IntegerField(default=0, blank=True, null=True)
    exam = models.IntegerField(default=0, blank=True, null=True)
    total = models.IntegerField(default=0, blank=True, null=True)
    # average = models.IntegerField(default=0, blank=True, null=True)
    grade = models.CharField(max_length=15, blank=True, null=True)
    remark = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=3, blank=True, null=True)
    group = models.CharField(max_length=5)
    arm = models.CharField(max_length=5)
    subject = models.CharField(max_length=20)
    term = models.IntegerField()
    student = models.CharField(max_length=10)
    # active = models.IntegerField(default=1, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    student = models.CharField(max_length=10)
    total = models.IntegerField(default=0, blank=True, null=True)
    average = models.FloatField(default=0.0, blank=True, null=True)
    position = models.CharField(max_length=3, blank=True, null=True)
    present = models.IntegerField(blank=True, null=True)
    absent = models.IntegerField(blank=True, null=True)
    term = models.IntegerField()
    group = models.CharField(max_length=5)
    arm = models.CharField(max_length=5)
    principalcomment = models.TextField(max_length=200, blank=True, null=True)
    gccomment = models.TextField(max_length=200, blank=True, null=True)
    hostelcomment = models.TextField(max_length=200, blank=True, null=True)
    teachercomment = models.TextField(max_length=200, blank=True, null=True)
    approve = models.IntegerField(default=0, blank=True, null=True)
    active = models.IntegerField(default=1, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Attendance(models.Model):
    date = models.DateField(default=pat)
    student = models.CharField(max_length=10)
    status = models.BooleanField()
    teacher = models.CharField(max_length=10)
    lock = models.IntegerField(default=0)
    term = models.IntegerField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Role(models.Model):
    role = models.CharField(max_length=30)
    keyword = models.SlugField()
    active = models.IntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.keyword = slugify(self.role)
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return self.role

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,blank=True,null=True)
    passport = models.ImageField(upload_to='passport', default='passport.jpg')

class CSV(models.Model):
    upload_file = models.FileField(upload_to='csv')
    active = models.BooleanField(default=False)
    date_uploaded = models.DateTimeField(default=timezone.now)

class AllClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    group = models.CharField(max_length=5)
    arm = models.CharField(max_length=5)
    teacher = models.CharField(max_length=10, null=True, blank=True)
    owner = models.CharField(max_length=10, null=True, blank=True)
    number_of_student = models.IntegerField(default=0, null=True, blank=True)
    lock = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Comment(models.Model):
    comment = models.TextField(max_length=200)
    score = models.IntegerField(null=True, blank=True)
    owner = models.CharField(max_length=20, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Config(models.Model):
    school_name = models.CharField(max_length=100)
    school_initial = models.CharField(max_length=5)
    school_logo = models.ImageField(blank=True, null=True)
    anual_result = models.CharField(max_length=8, blank=True, null=True)
    online_ass = models.CharField(max_length=8, blank=True, null=True)
    CA_max = models.IntegerField(blank=True, null=True)
    exam_max = models.IntegerField(blank=True, null=True)
    subject_max_score = models.IntegerField(blank=True, null=True)
    junior_no_of_subject = models.IntegerField(blank=True, null=True)
    senior_no_of_subject = models.IntegerField(blank=True, null=True)
    start_result = models.BooleanField(default=False)
    student_unique = models.IntegerField()
    staff_unique = models.IntegerField()
    result_start = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    pin = models.CharField(max_length=20)
    serial = models.CharField(max_length=20)
    usage = models.IntegerField(default=0)
    student = models.CharField(max_length=15)
    created = models.DateTimeField(default=timezone.now)