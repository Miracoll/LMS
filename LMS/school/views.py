from email import message
from email.headerregistry import Group
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.template import context
from .models import CSV, Card, Config, AllSubject, Arm, Attendance, Profile, Result, Role, Session, Student, AllClass, Term, Class, NOK, Teacher, Record, Subject,Comment
from .forms import CSVForm
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from random import randrange
import csv, io
from django.http import HttpResponse
from django.db.models import Sum, Count
from datetime import date
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template

# Create your views here.

@login_required(login_url='login')
def home(request):
    student = Student.objects.filter(active = 1).aggregate(active = Count('registration_number'))
    allstudent = Student.objects.all().aggregate(active = Count('registration_number'))
    context = {
        'student':student['active'],
        'allstudent':allstudent['active'],
    }
    return render(request, 'school/home.html', context)

def config(request):
    config = Config.objects.all()
    if 'submit' in request.POST and request.FILES['sch_logo']:
        sch_name = request.POST.get('sch')
        sch_init = request.POST.get('sch_init')
        result = request.POST.get('result')

        sch_logo = request.FILES.get('sch_logo')
        fss = FileSystemStorage()
        file = fss.save(sch_logo.name, sch_logo)

        online = request.POST.get('online_ass')
        ca_max = request.POST.get('ca_max')
        exam_max = request.POST.get('exam_max')
        jms = request.POST.get('jms')
        sms = request.POST.get('sms')

        student_unique = request.POST.get('stu_unique')
        staff_unique = request.POST.get('staff_unique')

        Config.objects.create(
            school_name = sch_name,
            school_initial = sch_init,
            school_logo = file,
            anual_result = result,
            online_ass = online,
            CA_max = ca_max,
            exam_max = exam_max,
            junior_no_of_subject = jms,
            senior_no_of_subject = sms,
            added_by = request.user,
            student_unique = student_unique,
            staff_unique =staff_unique

        )
        messages.success(request,'Configuration updated')
        return redirect('config')
    context = {'config':config}
    return render(request, 'school/config.html', context)

def configerror(request):
    return render(request, 'school/configerror.html')

def error404(request):
    return render(request, 'school/404.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def term(request):
    return render(request, 'school/term.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def viewterm(request):
    term = Term.objects.all()
    context = {'term':term}
    return render(request, 'school/termview.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def switchterm(request):
    term = Term.objects.all()
    try:
        activeterm = Term.objects.get(active = 1).term
    except Term.DoesNotExist:
        activeterm = 1
    if request.method == 'POST':
        term = request.POST.get('term')
        Term.objects.filter(active = 1).update(active = 0)
        Term.objects.filter(term=term).update(active = 1)
        messages.success(request,'Done')
        return redirect('term')
    context = {'term':term,'active':activeterm}
    return render(request, 'school/termswitch.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def createterm(request):
    if request.method == 'POST':
        term = request.POST.get('term')
        Term.objects.create(term=term, added_by=request.user)
        messages.success(request,'Created')
        return redirect('createterm')
    return render(request, 'school/termcreate.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def termerror(request):
    return render(request, 'school/termerror.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def session(request):
    return render(request, 'school/session.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def viewsession(request):
    session = Session.objects.all()
    context = {'session':session}
    return render(request, 'school/sessionview.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def switchsession(request):
    session = Session.objects.all()
    activeyear = 1

    try:
        activesession = Session.objects.get(active = 1).session
        activeyear = Session.objects.get(active = 1).year
    except Session.DoesNotExist:
        activesession = '1'
        activeyear = 1
    
    if request.method == 'POST':
        session = request.POST.get('session')
        # year = request.POST.get('year')
        Session.objects.filter(active = 1).update(active = 0)
        Session.objects.filter(session=session).update(active = 1)
        messages.success(request,'Done')
        return redirect('session')
    context = {'session':session, 'active':activesession, 'year':activeyear}
    return render(request, 'school/sessionswitch.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def createsession(request):
    if request.method == 'POST':
        session = request.POST.get('session')
        year = request.POST.get('year')
        Session.objects.create(session=session, year=year, added_by=request.user)
        messages.success(request,'Created')
        return redirect('createsession')
    return render(request, 'school/sessioncreate.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def group(request):
    group = AllClass.objects.all()
    allgroup = Class.objects.all()
    arm = Arm.objects.all
    firstarm = Arm.objects.get(id=1).arm
    # Create a classroom
    if 'submit' in request.POST:
        role = Role.objects.filter(role  = 'class teacher')
        if len(role) == 0:
            messages.warning(f"create 'class teacher' first" )
            return redirect('role')
        group = request.POST.get('group')
        Class.objects.create(group=group, added_by=request.user)
        AllClass.objects.create(group=group, arm=firstarm, teacher=group+firstarm, lock=0, active=1, added_by=request.user)
        user = User.objects.create_user(group + firstarm,group+firstarm+'@school.com','classteacher')

        # Assign previllage
        userid = User.objects.get(username=group+firstarm).id
        getusergroup = Group.objects.get(name='class-teacher')
        getusergroup.user_set.add(userid)

        user.is_staff = False
        user.first_name = group
        user.last_name = firstarm
        user.save()
        getuser = user.id

        getroleid = Role.objects.get(role = 'class teacher')
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
        messages.success(request,'Created')
        return redirect('class')
    # Create a unit class
    elif 'submit1' in request.POST:
        group = request.POST.get('allgroup')
        arm = request.POST.get('arm')
        teacher = request.POST.get('teacher')
        armexist = AllClass.objects.filter(group = group) & AllClass.objects.filter(arm = arm)
        if len(armexist) == 1:
            armexist.update(active = 1)
            messages.success(request,'Returned')
            return redirect('class')
        else:
            AllClass.objects.create(group=group,arm=arm,teacher= group+arm,owner=teacher,lock=0,active=1,added_by=request.user)
            user = User.objects.create_user(group + arm,group+arm+'@school.com','classteacher')
            user.is_staff = False
            user.first_name = group
            user.last_name = arm
            user.save()
            getuser = user.id

            # Assign previllage
            userid = User.objects.get(username=group+arm).id
            getusergroup = Group.objects.get(name='class-teacher')
            getusergroup.user_set.add(userid)

            getroleid = Role.objects.get(role = 'class teacher')
            Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
            Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
            email = Teacher.objects.get(registration_number = teacher).email
            ln = Teacher.objects.get(registration_number = teacher).last_name
            fn = Teacher.objects.get(registration_number = teacher).first_name
            subject = f'{group}{arm} class login'
            recipient = [email]
            text_content = f'GREEN PARK ACADEMY Hello {fn} {ln} thanks for choosing UNIBEN.Your login credential are:Application number:{group+arm} Password:classteacher'
            html_content = f'<div><h3 style="color:purple">GREEN PARK ACADEMY</h3></div><div><p>Hello {fn} {ln} thanks for choosing GREEN PARK ACADEMY.</p><p>Your login credential for {group}{arm} class is:</p><p>Class number: {group}{arm}</p><p>Password: classteacher</p></div>'
            message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
            # message.attach_alternative(html_content, 'text/html')
            # message.send()
            messages.success(request,'Done')
            return redirect('class')

    # Assign class to a staff
    elif 'submit2' in request.POST:
        staff = request.POST.get('reg2')
        group = request.POST.get('allgroup2')
        print(group)
        arm = request.POST.get('arm2')
        getstaff = Teacher.objects.filter(registration_number=staff)
        grouprow = AllClass.objects.filter(group = group) & AllClass.objects.filter(arm = arm) & AllClass.objects.filter(active = 1)
        alreadyexist = AllClass.objects.filter(teacher = staff)
        if len(grouprow) == 0:
            messages.error(request,'Such class/arm does not exist or not active')
            return redirect('class')
        else:
            if len(alreadyexist) >= 1:
                messages.error(request,'You have already assign a class to this person')
                return redirect('class')
            else:
                if len(getstaff) == 0:
                    messages.error(request,'Sorry i cant recongize this person as a staff')
                    return redirect('class')
                else:
                    grouprow.update(owner = staff, lock=0,active=1)
                    email = Teacher.objects.get(registration_number = staff).email
                    ln = Teacher.objects.get(registration_number = staff).last_name
                    fn = Teacher.objects.get(registration_number = staff).first_name
                    subject = f'{group}{arm} class login'
                    recipient = [email]
                    text_content = f'GREEN PARK ACADEMY Hello {fn} {ln} thanks for choosing UNIBEN.Your login credential are:Application number:{group+arm} Password:classteacher'
                    html_content = f'<div><h3 style="color:purple">GREEN PARK ACADEMY</h3></div><div><p>Hello {fn} {ln} thanks for choosing GREEN PARK ACADEMY.</p><p>Your login credential for {group}{arm} class is:</p><p>Class number: {group}{arm}</p><p>Password: classteacher</p></div>'
                    message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
                    # message.attach_alternative(html_content, 'text/html')
                    # message.send()
                    messages.success(request,'Done')
                    return redirect('class')
    context = {'class':group, 'allclass':allgroup, 'arm':arm}
    return render(request, 'school/class.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def removeclassteacher(request,pk):
    AllClass.objects.filter(id = pk).update(teacher = '')
    messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def deactivateclass(request,pk):
    AllClass.objects.filter(id = pk).update(active = 0)
    getuser = AllClass.objects.get(id=pk).teacher
    User.objects.filter(username = getuser).update(is_active = 0)
    messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def activateclass(request,pk):
    AllClass.objects.filter(id = pk).update(active = 1)
    getuser = AllClass.objects.get(id=pk).teacher
    User.objects.filter(username = getuser).update(is_active = 1)
    messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def arm(request):
    arm = Arm.objects.all()
    context = {'arm':arm}
    return render(request, 'school/arm.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def viewarm(request):
    arm = Arm.objects.all()
    context = {'arm':arm}
    return render(request, 'school/armview.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def createarm(request):
    if request.method == 'POST':
        arm = request.POST.get('arm')
        Arm.objects.create(arm=arm, added_by=request.user)
        messages.success(request,'Created')
        return redirect('createarm')
    return render(request, 'school/armcreate.html')

def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.warning(request,'username does not exist')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.warning(request,'username/password is incorrect or class not active(ask management)')
            return redirect('login')
    return render(request, 'school/login.html')

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def newrole(request):
    if 'submit' in request.POST:
        role = request.POST.get('role')
        checkrole = Role.objects.filter(role = role)
        if len(checkrole)  == 0:
            Role.objects.create(role=role, added_by=request.user)
            getkeyword = Role.objects.get(role = role).keyword
            Group.objects.create(name=getkeyword)
            messages.success(request,'Done')
            return redirect('role')
        else:
            messages.error(request,f'{role} already exist')
            return redirect('role')
            
    return render(request, 'school/addstaff.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def subject(request):
    allsubject = AllSubject.objects.all()
    subject = Subject.objects.all()
    group = Class.objects.all()
    arm = Arm.objects.all()
    if 'submit' in request.POST:
        subject = request.POST.get('subject')
        cat = request.POST.get('cat')
        AllSubject.objects.create(subject=subject, category=cat, added_by = request.user)
        messages.success(request,"Done: Click on 'view all subject' to see all available subjects")
        return redirect('subject')
    elif 'submit1' in request.POST:
        subject = request.POST.get('subject')
        cat = request.POST.get('cat')
        group = request.POST.get('group')
        arm = request.POST.get('arm')
        teacher = request.POST.get('teacher')
        Subject.objects.create(subject=subject, group=group, arm=arm, teacher=teacher, owner=group+arm, category=cat, added_by = request.user)
        messages.success(request,'Done')
        return redirect('subject')
    context = {'subject':subject,'allsubject':allsubject,'group':group,'arm':arm}
    return render(request, 'school/subject.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def student(request):
    return render(request, 'school/student.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def transferstudent(request):
    group = Class.objects.all()
    arm = Arm.objects.all()
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        getarm = request.POST.get('armget')
        getgroup = request.POST.get('group')
        oldgroup = Student.objects.get(registration_number = reg).group
        oldarm = Student.objects.get(registration_number = reg).arm

        Student.objects.filter(registration_number = reg).update(group=getgroup)
        Student.objects.filter(registration_number = reg).update(arm = getarm)
        # get current
        oldnos = len(Student.objects.filter(group = oldgroup, arm = oldarm, active = 1))
        AllClass.objects.filter(group=oldgroup, arm=oldarm).update(number_of_student = oldnos)
        # get new
        nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        messages.success(request,'Update successful')
        return redirect('transfer_student')
    context = {'group':group,'arm':arm}
    return render(request, 'school/studenttransfer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def disablestudent(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        getgroup = Student.objects.get(registration_number = reg).group
        getarm = Student.objects.get(registration_number = reg).arm
        student = Student.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        student.update(active=0)
        active.update(is_active = 0)
        nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        messages.success(request,'Update successful')
        return redirect('disable_student')
    return render(request, 'school/studentdisable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def enablestudent(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        getgroup = Student.objects.get(registration_number = reg).group
        getarm = Student.objects.get(registration_number = reg).arm
        student = Student.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        student.update(active=1)
        active.update(is_active = 1)
        nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        messages.success(request,'Update successful')
        return redirect('enable_student')
    return render(request, 'school/studentenable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def editreg(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        new_reg = request.POST.get('new_reg_num')
        student = Student.objects.filter(registration_number=reg)
        student.update(registration_number=new_reg)
        User.objects.filter(username = reg).update(username = new_reg)
        messages.success(request,'Update successful')
        return redirect('edit_reg')
    return render(request, 'school/studentregedit.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def registerstudent(request):
    today = date.today()
    pat = today.strftime("%Y-%m-%d")
    group = Class.objects.all()
    arm = Arm.objects.all()
    try:
        sch_init = Config.objects.get(id=1).school_initial
        unique = Config.objects.get(id=1).student_unique
    except Config.DoesNotExist:
        return redirect('configerror')
    try:
        term = Term.objects.get(active=1).term
    except Term.DoesNotExist:
        return redirect('termerror')

    if 'login' in request.POST and request.FILES['myfile']:
        upload = request.FILES.get('myfile')
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        # upload_url = fss.url(file)
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        other_name = request.POST.get('other_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')
        getgroup = request.POST.get('group')
        getarm = request.POST.get('arm')
        # myfile = request.FILES.get('myfile')
        print(file)

        rand = sch_init.upper() + str(unique) + str(randrange(123456,987654,5))
        # TODO: Check if app number already exist

        relate = request.POST.get('relate')
        full_name = request.POST.get('full_name')
        address1 = request.POST.get('address1')
        email1 = request.POST.get('email1')
        mobile1 = request.POST.get('mobile1')

        addtostudent = Student.objects.create(last_name=last_name,first_name=first_name,other_name=other_name,email=email,mobile=mobile,
        address=address,dob=dob,sex=sex,passport=file,group=getgroup,arm=getarm,registration_number=rand,added_by=request.user)
        # addtostudent.save()
        
        addtonok = NOK(relationship=relate,full_name=full_name,address=address1,mobile=mobile1,email=email1,student=addtostudent,added_by=request.user)
        addtonok.save()

        user = User.objects.create_user(rand,email,'student')
        user.is_staff = False
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        getuser = user.id

        role = Role.objects.filter(role  = 'student')
        if len(role) == 0:
            Role.objects.create(role='student',added_by=request.user)

        getroleid = Role.objects.get(role = 'Student')
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = file)

        userid = User.objects.get(username=rand).id
        getusergroup = Group.objects.get(name='student')
        getusergroup.user_set.add(userid)

        nos = Student.objects.filter(group = getgroup) & Student.objects.filter(arm = getarm) & Student.objects.filter(active = 1)
        cnos = nos.aggregate(available = Count('registration_number'))
        AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = cnos['available'])

        # Transfer to attendance table
        Attendance.objects.create(date=pat,student=rand,status=1,term=term,teacher=getgroup+getarm,lock=1,added_by=request.user)

        return redirect('register_student')
        # return redirect('print')
    context = {'group':group, 'arm':arm}
    return render(request, 'school/studentregister.html',context)

# Move table to else where
def registerstudentnok(request):
    getstudent = NOK.objects.get()
    student = NOK.objects.filter(student = getstudent)
    if request.method == 'POST':
        relate = request.POST.get('relate')
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        addtonok = NOK(full_name=full_name,address=address,mobile=mobile,email=email,added_by=request.user)
        addtonok.save()
        redirect('print')
    return render(request, 'school/studentnok.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def getstudent(request):
    errormsg = False
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        try:
            student = Student.objects.get(registration_number=reg).id
            return redirect('manage_student',student)
        except Student.DoesNotExist:
            errormsg = True
    return render(request, 'school/studentget.html',{'errormsg':errormsg})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def managestudent(request,pk):
    student = Student.objects.filter(id=pk)
    reg = Student.objects.get(id=pk).registration_number
    if 'submit1' in request.POST:
        last_name = request.POST.get('last_name1')
        first_name = request.POST.get('first_name1')
        other_name = request.POST.get('other_name1')
        address = request.POST.get('address1')
        phone = request.POST.get('phone1')
        email = request.POST.get('email1')
        # twitter = request.POST.get('twitter')
        # facebook = request.POST.get('facebook')
        # insta = request.POST.get('instagram')
        # linked = request.POST.get('linkedin')
        student.update(last_name=last_name,first_name=first_name,other_name=other_name,address=address,mobile=phone,
        email=email
        )
        messages.success(request,'Update successful')
        return redirect('manage_student',pk)

    context = {'student':student}
    return render(request, 'school/studentmanage.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal'])
def registerstaff(request):
    sch_init = Config.objects.get(id=1).school_initial
    unique = Config.objects.get(id=1).staff_unique
    staff = Role.objects.filter(active = 1).exclude(role__in = ['Admin','Student','subject teacher'])
    if 'submit' in request.POST and request.FILES['myfile']:
        upload = request.FILES['myfile']
        fss = FileSystemStorage(location='media/teacher_passport')
        file = fss.save(upload.name, upload)
        upload_url = fss.url(file)
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        other_name = request.POST.get('other_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')
        role = request.POST.get('role')


        rand = sch_init.upper() + str(unique) + str(randrange(123456,987654,5))
        # TODO: Check if app number already exist

        relate = request.POST.get('relate')
        full_name = request.POST.get('full_name')
        address1 = request.POST.get('address1')
        email1 = request.POST.get('email1')
        mobile1 = request.POST.get('mobile1')

        Teacher.objects.create(last_name=last_name,first_name=first_name,other_name=other_name,email=email,mobile=mobile,
        address=address,dob=dob,sex=sex,passport='teacher_passport/'+file,registration_number=rand,added_by=request.user,
        nok_relationship=relate,nok_full_name=full_name,nok_address=address1,nok_mobile=mobile1,nok_email=email1)
        # addtoteacher.save()

        # psw = 'GPAT' + str(randrange(123456,987654,5))
        user = User.objects.create_user(rand,email,mobile)
        user.is_staff = False
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        getuser = user.id
        getroleid = Role.objects.get(role = role).id
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = file)

        getkeyword = Role.objects.get(role = role).keyword
        userid = User.objects.get(username=rand).id
        getgroup = Group.objects.get(name=getkeyword)
        getgroup.user_set.add(userid)

        return redirect('register_teacher')
        # return redirect('print')
    context = {'staff':staff}
    return render(request, 'school/staffregister.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def disablestaff(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        staff = Teacher.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        staff.update(active=0)
        active.update(is_active = 0)
        messages.success(request,'Update successful')
        return redirect('disable_staff')
    return render(request, 'school/staffdisable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
def enablestaff(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        staff = Teacher.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        staff.update(active=1)
        active.update(is_active = 1)
        messages.success(request,'Update successful')
        return redirect('enable_staff')
    return render(request, 'school/staffenable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def getstaff(request):
    errormsg = False
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        try:
            staff = Teacher.objects.get(registration_number=reg).id
            return redirect('manage_staff',staff)
        except Teacher.DoesNotExist:
            errormsg = True
    return render(request, 'school/staffget.html',{'errormsg':errormsg})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def managestaff(request,pk):
    staff = Teacher.objects.filter(id=pk)
    reg = Teacher.objects.get(id=pk).registration_number
    if 'submit1' in request.POST:
        last_name = request.POST.get('last_name1')
        first_name = request.POST.get('first_name1')
        other_name = request.POST.get('other_name1')
        address = request.POST.get('address1')
        phone = request.POST.get('phone1')
        email = request.POST.get('email1')
        # twitter = request.POST.get('twitter')
        # facebook = request.POST.get('facebook')
        # insta = request.POST.get('instagram')
        # linked = request.POST.get('linkedin')
        staff.update(last_name=last_name,first_name=first_name,other_name=other_name,address=address,mobile=phone,
        email=email
        )
        messages.success(request,'Update successful')
        return redirect('manage_staff',pk)

    context = {'staff':staff}
    return render(request, 'school/staffmanage.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def editstaffreg(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        new_reg = request.POST.get('new_reg_num')
        staff = Teacher.objects.filter(registration_number=reg)
        staff.update(registration_number=new_reg)
        User.objects.filter(username = reg).update(username = new_reg)
        messages.success(request,'Update successful')
        return redirect('edit_staff_reg')
    return render(request, 'school/staffregedit.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def assessment(request):
    form = CSVForm()
    term = Term.objects.get(active = 1).term
    groupsel = Subject.objects.filter(teacher = request.user).values('group').distinct()
    armsel = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()
    if 'manualupload' in request.POST:
        group = request.POST.get('group')
        arm = request.POST.get('arm')
        ass = request.POST.get('ass')
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')
        getsubject = request.POST.get('subject')
        
        if ass == 'CA1':
            new_value = {'CA1':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=group,arm=arm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'CA2':
            new_value = {'CA2':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=group,arm=arm,subject=getsubject,student=reg_num,defaults=new_value)
        else:
            new_value = {'CA3':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=group,arm=arm,subject=getsubject,student=reg_num,defaults=new_value)

        messages.success(request,f'Added successful')
        redirect('assessment')

    # For csv upload

    if 'csvupload' in request.POST:
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    ca1 = line[6]
                    ca2 = line[7]
                    ca3 = line[8]
                    student_class = line[3]
                    student_arm = line[4]
                    reg = line[2]
                    getsubject = line[5]
                    user = request.user
                    record = Record.objects.filter(subject=getsubject) & Record.objects.filter(student=reg) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
                    if len(record) == 1:
                        # Update
                        record.update(CA1=ca1,CA2=ca2,CA3=ca3)
                    else:
                        Record.objects.create(
                            CA1=ca1,CA2=ca2,CA3=ca3,group=student_class,subject=getsubject,term=term,arm=student_arm,
                            student=reg,added_by=user
                        )
                    print(line)
                obj.active = True
                obj.save()
        messages.success(request,f'Added successful')
        redirect('assessment')

    # Get template
    if 'submit' in request.POST:
        group = request.POST.get('group')
        arm =request.POST.get('arm')
        sub = request.POST.get('subject')

        studentand = Student.objects.filter(group = group) & Student.objects.filter(arm = arm) & Student.objects.filter(active = 1)
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','CA1','CA2','CA3'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('assessment')
        else:
            for student in student:
                stud = list(student)
                stud.extend([sub,0,0,0])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} CA.csv"'
            return response

    context = {'form':form, 'group':groupsel, 'arm':armsel, 'subject':subject}
    return render(request, 'school/assessment.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def project(request):
    form = CSVForm()
    term = Term.objects.get(active = 1).term
    group = Subject.objects.filter(teacher = request.user).values('group').distinct()
    arm = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()
    if 'manualupload' in request.POST:
        sub = request.POST.get('subject')
        student_class = request.POST.get('group')
        student_arm = request.POST.get('arm')
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')

        record = Record.objects.filter(subject=sub) & Record.objects.filter(student=reg_num) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
        if len(record) == 1:
            # Update
            record.update(project = score)
        else:
            Record.objects.create(exam=score,group=student_class,term=term,subject=sub,arm=student_arm,student=reg_num,added_by=request.user)
        student = Record.objects.filter(student = reg_num)
        messages.success(request,f'Added successful')
        redirect('project')

    # For csv upload
    if 'csvupload' in request.POST:
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    project = line[6]
                    getsubject = line[5]
                    student_class = line[3]
                    student_arm = line[4]
                    reg = line[2]
                    user = request.user

                    record = Record.objects.filter(subject=getsubject) & Record.objects.filter(student=reg) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
                    if len(record) == 1:
                        # Update
                        record.update(project = project)
                    else:
                        Record.objects.create(
                            project=project,group=student_class,term=term,subject=getsubject,arm=student_arm,student=reg,added_by=user)
                    print(line)
                obj.active = True
                obj.save()
        messages.success(request,f'Added successful')
        redirect('project')

    # Get template
    if 'submit' in request.POST:
        group = request.POST.get('group')
        arm =request.POST.get('arm')
        sub = request.POST.get('subject')

        studentand = Student.objects.filter(group = group) & Student.objects.filter(arm = arm) & Student.objects.filter(active = 1)
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','Project'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('project')
        else:
            for student in student:
                stud = list(student)
                stud.extend([sub,0])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} project.csv"'
            return response
    context = {'form':form, 'group':group, 'arm':arm, 'subject':subject}
    return render(request, 'school/project.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def test(request):
    form = CSVForm()
    term = Term.objects.get(active = 1).term
    group = Subject.objects.filter(teacher = request.user).values('group').distinct()
    arm = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()
    # For manual upload
    if 'manualupload' in request.POST:
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')
        sub = request.POST.get('subject')
        student_class = request.POST.get('group')
        student_arm = request.POST.get('arm')

        record = Record.objects.filter(subject=sub) & Record.objects.filter(student=reg_num) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
        if len(record) == 1:
            # Update
            record.update(test = score)
        else:
            Record.objects.create(test=score,group=student_class,term=term,subject=sub,arm=student_arm,student=reg_num,added_by=request.user)
        messages.success(request,f'Added successful')
        redirect('test')

    # For csv upload
    if 'csvupload' in request.POST:
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    test = line[6]
                    student_class = line[3]
                    student_arm = line[4]
                    reg = line[2]
                    getsubject = line[5]
                    user = request.user

                    record = Record.objects.filter(subject=getsubject) & Record.objects.filter(student=reg) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
                    if len(record) == 1:
                        # Update
                        record.update(test = test)
                    else:
                        Record.objects.create(test=test,group=student_class,term=term,subject=getsubject,arm=student_arm,student=reg,added_by=user)
                    print(line)
                obj.active = True
                obj.save()
        messages.success(request,f'Added successful')
        redirect('test')

    # Get template
    if 'submit' in request.POST:
        group = request.POST.get('group')
        arm =request.POST.get('arm')
        sub = request.POST.get('subject')

        studentand = Student.objects.filter(group = group) & Student.objects.filter(arm = arm) & Student.objects.filter(active = 1)
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','Test'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('result_template')
        else:
            for student in student:
                stud = list(student)
                stud.extend([sub,0])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} test.csv"'
            return response
    context = {'form':form, 'group':group, 'arm':arm, 'subject':subject}
    return render(request, 'school/test.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def exam(request):
    form = CSVForm()
    term = Term.objects.get(active = 1).term
    group = Subject.objects.filter(teacher = request.user).values('group').distinct()
    arm = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()
    # For manual upload
    if 'manualupload' in request.POST:
        sub = request.POST.get('subject')
        student_class = request.POST.get('group')
        student_arm = request.POST.get('arm')
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')

        record = Record.objects.filter(subject=sub) & Record.objects.filter(student=reg_num) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
        if len(record) == 1:
            # Update
            record.update(exam = score)
        else:
            Record.objects.create(exam=score,group=student_class,term=term,subject=sub,arm=student_arm,student=reg_num,added_by=request.user)
        student = Record.objects.filter(student = reg_num)
        messages.success(request,f'Added successful')
        redirect('exam')

    # For csv upload
    elif 'csvupload1' in request.POST:
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    exam = line[6]
                    student_class = line[3]
                    student_arm = line[4]
                    reg = line[2]
                    sub = line[5]
                    user = request.user
                    record = Record.objects.filter(subject=sub) & Record.objects.filter(student=reg) & Record.objects.filter(group=student_class) & Record.objects.filter(arm=student_arm)
                    if len(record) == 1:
                        # Update
                        record.update(exam = exam)
                    else:
                        Record.objects.create(
                            exam=exam,group=student_class,term=term,subject=sub,arm=student_arm,student=reg,added_by=user)
                    print(line)
                obj.active = True
                obj.save()
            messages.success(request,f'Added successful')
            redirect('exam')
        else:
            messages.error(request,'Not successful')

    # Get template
    elif 'submit' in request.POST:
        group = request.POST.get('group')
        arm =request.POST.get('arm')
        sub = request.POST.get('subject')

        studentand = Student.objects.filter(group = group) & Student.objects.filter(arm = arm) & Student.objects.filter(active = 1)
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','Exam'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('exam')
        else:
            for student in student:
                stud = list(student)
                stud.extend([sub,0])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} exam.csv"'
            return response
    context = {'form':form, 'group':group, 'arm':arm, 'subject':subject}
    return render(request, 'school/exam.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def resulttemplate(request):
    allgroup = AllClass.objects.filter(teacher = request.user)
    group = Subject.objects.filter(teacher = request.user).values('group').distinct()
    arm = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()
    if 'submit' in request.POST:
        getgroup = request.POST.get('group')
        getarm =request.POST.get('arm')
        subject = request.POST.get('subject')

        studentand = Student.objects.filter(group = getgroup, arm=getarm, active = 1)
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        # print(student)

        # nondata = ['','','','','=sum(d2:g2)','=AVERAGE(D2:G2)','=IF(I2>=70,"A",IF(I2>=55,"C",IF(I2>=40,"P","F")))','=IF(I2>=70,"Excellent",IF(I2>=55,"Good",IF(I2>=40,"Pass","Fail")))','=RANK(I2,$I$2:$I$50)']
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','CA1','CA2','CA3','Project','Test','Exam','Total','Grade','Remark','Position','Subject'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('result_template')
        else:
            count = 2
            for student in student:
                countd = 'f'+str(count)
                countg = 'k'+str(count)
                counti = 'l'+str(count)
                stud = list(student)
                ca1 = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).CA1
                ca2 = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).CA2
                ca3 = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).CA3
                project = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).project
                test = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).test
                exam = Record.objects.get(student=stud[2],subject=subject,group=getgroup,arm=getarm).exam
                # print(ca1)
                stud.extend([ca1,ca2,ca3,project,test,exam,'=sum('+countd+':'+countg+')','=IF('+counti+'>=70,"A",IF('+counti+'>=55,"C",IF('+counti+'>=40,"P","F")))','=IF('+counti+'>=70,"Excellent",IF('+counti+'>=55,"Good",IF('+counti+'>=40,"Pass","Fail")))','=RANK('+counti+',$L$2:$L$50)',subject])
                writer.writerow(stud)
                count += 1
            response['Content-Disposition'] = f'attachment; filename="{getgroup}{getarm} record.csv"'
            return response
    if 'submit1' in request.POST:
        resultsta = Config.objects.get(id=1).result_start
        if resultsta == 1:
            getgroup = request.POST.get('group1')
            getarm =request.POST.get('arm1')
            # subject = request.POST.get('subject1')

            studentand = Student.objects.filter(group = getgroup, arm=getarm, active = 1)
            student = studentand.values_list('last_name','first_name','registration_number')
            # print(student)
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Registration Number','Total','Average','Position'])
            if len(student) == 0:
                messages.error(request,'No record found')
                return redirect('result_template')
            else:
                count = 2
                for student in student:
                    countd = 'd'+str(count)
                    counte = 'e'+str(count)
                    counti = 'l'+str(count)
                    stud = list(student)
                    studtotal = Record.objects.filter(student = stud[2]).aggregate(total = Sum('total'))
                    stud.extend([studtotal['total'],'='+countd+'/14','=RANK('+counte+',$E$2:$E$50)'])
                    writer.writerow(stud)
                    count += 1
                response['Content-Disposition'] = f'attachment; filename="{getgroup}{getarm} result.csv"'
                return response
        else:
            messages.error(request,'The principal/vp/admin need to start result computation first')
            return redirect('result_template')
    context = {'group':allgroup, 'subject':group, 'arm':arm, 'sub':subject}
    return render(request, 'school/resulttemplate.html', context)

def termresult(request):
    return render(request, 'school/termresult.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def resultupload(request):
    form = CSVForm()
    term = Term.objects.get(active=1).term
    # Record upload
    if 'csvupload' in request.POST:

        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    ca1 = line[5]
                    ca2 = line[6]
                    ca3 = line[7]
                    project = line[8]
                    test = line[9]
                    exam = line[10]
                    student_class = line[3]
                    student_arm = line[4]
                    reg = line[2]
                    total = line[11]
                    grade = line[12]
                    remark = line[13]
                    position = line[14]
                    sub = line[15]
                    user = request.user

                    record = Record.objects.filter(subject=sub,student=reg,group=student_class,arm=student_arm)
                    if len(record) == 1:
                        # Update
                        try:
                            record.update(total = total,grade=grade,remark=remark,position=position)
                        except TypeError:
                            messages.warning(request, 'Save(ctrl + s) the template first before uploading')
                            return redirect('assessment')
                    else:
                        Record.objects.create(
                            CA1=ca1,CA2=ca2,CA3=ca3,project=project,test=test,exam=exam,group=student_class,arm=student_arm,
                            student=reg,total=total,grade=grade, term=term,remark=remark,position=position,subject=sub,added_by=user
                        )
                    print(line)
                    upload = Subject.objects.get(group=student_class, arm=student_arm,subject=sub).upload
                    Subject.objects.filter(group=student_class, arm=student_arm,subject=sub).update(upload=upload+1)
                
                obj.active = True
                obj.save()
        messages.success(request,f'Added successful')
        redirect('assessment')

    # Result upload
    if 'csvupload1' in request.POST:
        form = CSVForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = CSVForm()
            obj = CSV.objects.get(active = False)

            with open(obj.upload_file.path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)
                for line in csv_reader:
                    reg = line[2]
                    total = line[3]
                    ave = line[4]
                    position = line[5]
                    user = request.user

                    present = len(Attendance.objects.filter(student = reg,status = 1,term = term))
                    absent = len(Attendance.objects.filter(student = reg,status = 0,term = term))

                    Result.objects.create(
                        student=reg,total=total,average=ave,position=position,present=present,absent=absent,term=term,added_by=user,group=request.user.first_name,arm=request.user.last_name
                    )
                    print(line)
                obj.active = True
                obj.save()
        messages.success(request,f'Added successful')
        redirect('result_upload')

    context = {'form':form}
    return render(request, 'school/resultupload.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','subject-teacher'])
def getstudentresult(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        student = Student.objects.get(registration_number=reg).id
        return redirect('display_result',student)
    return render(request, 'school/studentgetresult.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','subject-teacher'])
def displayresult(request,pk):
    avgagg = 0
    reg = Student.objects.get(id=pk).registration_number
    avg = Result.objects.get(student=reg).average
    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39
    comment = Comment.objects.filter(score = avgagg)
    student = Student.objects.filter(registration_number=reg)
    record = Record.objects.filter(student = reg)
    result = Result.objects.filter(student = reg)
    print(avg)
    context = {
        'student':student,
        'record':record,
        'result':result,
        'average':avg,
        'comment':comment,
    }
    return render(request, 'school/resultdisplay.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','hostel-manager','guildance-and-cousellor','class-teacher'])
def resultcomment(request):
    # Execute if result status is competed by the class teacher
    if 'submit' in request.POST:
        comment70 = request.POST.get('comment70')
        comment55 = request.POST.get('comment55')
        comment40 = request.POST.get('comment40')
        comment39 = request.POST.get('comment39')
        Comment.objects.create(comment = comment70, score = 70, owner = request.user.profile.role, added_by=request.user)
        Comment.objects.create(comment = comment55, score = 55, owner = request.user.profile.role, added_by=request.user)
        Comment.objects.create(comment = comment40, score = 40, owner = request.user.profile.role, added_by=request.user)
        Comment.objects.create(comment = comment39, score = 39, owner = request.user.profile.role, added_by=request.user)

        messages.success(request, 'Done')
        return redirect('result_comment')
    if 'submit1' in request.POST:
        reg = request.POST.get('reg')
        comment = request.POST.get('comment')
        # print(request.user.profile.role)
        if request.user.profile.role == 'Principal':
            Result.objects.filter(student = reg).update(principalcomment = comment)
        if request.user.profile.role == 'Guildance and Cousellor':
            Result.objects.filter(student = reg).update(gccomment = comment)
        if request.user.profile.role == 'Hostel manager':
            Result.objects.filter(student = reg).update(hostelcomment = comment)
        if request.user.profile.role == 'Subject teacher':
            Result.objects.filter(student = reg).update(teachercomment = comment)
        messages.success(request, 'Done')
        return redirect('result_comment')
    return render(request, 'school/resultcomment.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def removeresult(request):
    group = Subject.objects.filter(teacher = request.user).values('group').distinct()
    arm = Subject.objects.filter(teacher = request.user).values('arm').distinct()
    subject = Subject.objects.filter(teacher = request.user).values('subject').distinct()

    if 'submit' in request.POST:
        group = request.POST.get('group')
        sub = request.POST.get('subject')
        arm = request.POST.get('arm')

        getstatus = Subject.objects.get(group = group, arm=arm, subject=sub).approve_result

        if getstatus == 0:
            record = Record.objects.filter(group=group,arm=arm,subject=sub,added_by=request.user)
            record.update(active=0)

            messages.success(request, 'Done')
            return redirect('result_remove')
        else:
            messages.error(request, 'Result has been approve already')
            return redirect('result_remove')
    
    context = {'group':group, 'arm':arm, 'subject':subject}
    return render(request, 'school/resultremove.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def approveresult(request):
    unitsubject = Subject.objects.filter(teacher = request.user)
    allgroup = AllClass.objects.filter(active = 1)
    context = {
        'allgroup':allgroup,
        'unitsubject':unitsubject,
    }
    return render(request, 'school/resultapprove.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def resultstatus(request):
    unitsubject = Subject.objects.filter(owner = request.user)
    context = {
        'unitsubject':unitsubject,
    }
    return render(request, 'school/resultstatus.html', context)

def approveclassresult(request):
    term = Term.objects.get(active=1).term
    group = request.user.first_name
    arm = request.user.last_name
    Subject.objects.filter(owner = request.user).update(lock=1)
    Result.objects.filter(group=group,arm=arm,term=term).update(approve=1)
    messages.success(request,f'{group}{arm} students can check their result now')
    return redirect('result_status')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def approveresultclick(request,pk):
    Subject.objects.filter(id = pk).update(approve_result = 1)
    messages.success(request,'Done')
    return redirect('result_approve')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def resultcomputation(request):
    config = Config.objects.get(id=1).result_start
    context = {'config':config}
    return render(request, 'school/resultcomputation.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def startresult(request):
    subject = Subject.objects.all()
    Config.objects.filter(id=1).update(result_start=1)

    # Send mail to all staff

    # Get total students
    for i in subject:
        nos = len(Student.objects.filter(group=i.group,arm=i.arm))
        Subject.objects.filter(group=i.group, arm=i.arm).update(total_student=nos)
    messages.success(request, 'Done')
    return redirect('result_compute')



def superadmin(request):
    if request.method == 'POST':
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.create_user(username,email,password)
        user.is_staff = True
        user.is_superuser = True
        user.last_name = last_name
        user.first_name = first_name
        user.save()
        getuser = user.id

        role = Role.objects.filter(keyword__iexact  = 'admin')
        if len(role) == 0:
            Role.objects.create(role='admin',added_by=user)
            Group.objects.create(name='admin')

        getroleid = Role.objects.get(role = 'admin').id
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
            
        userid = User.objects.get(username=username).id
        getgroup = Group.objects.get(name='admin')
        getgroup.user_set.add(userid)
        messages.success(request, 'Creation successful')
        return redirect('logout')
    return render(request, 'school/superadmin.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def attendance(request):
    profile = request.user
    print(profile)
    try:
        getclass = AllClass.objects.get(teacher = profile).group
        getarm = AllClass.objects.get(teacher = profile).arm
        student = Student.objects.filter(group = getclass) & Student.objects.filter(arm = getarm) & Student.objects.filter(active = 1)
    except AllClass.DoesNotExist:
        return redirect('error404')
    context = {'student':student}
    return render(request, 'school/attendance.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def present(request, id):
    today = date.today()
    pat = today.strftime("%Y-%m-%d")
    profile = request.user
    term = Term.objects.get(active=1).term
    Attendance.objects.filter(teacher = profile)
    last = Attendance.objects.filter(student = id).last()

    if(len(Attendance.objects.filter(student = id) & Attendance.objects.filter(lock = 0)) == 0):
        if(str(pat) != str(last.date)):
            Attendance.objects.create(student=id, teacher=request.user, term=term, status=1, lock=1, added_by=request.user)
            messages.success(request, 'marked')
            return redirect('attendance')
    
    if((Attendance.objects.filter(student = id).last()).lock == 0 ):
        if(str(pat) == str(last.date)):
            Attendance.objects.filter(student = id).update(status = 1)
            Attendance.objects.filter(student = id).update(lock = 1)
            messages.success(request, 'updated')
            return redirect('attendance')
        else:
            Attendance.objects.create(student=id, teacher=request.user, term=term, status=1, lock=1, added_by=request.user)
            messages.success(request, 'marked')
            return redirect('attendance')
    else:
        messages.warning(request, 'Student already marked')
        return redirect('attendance')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def absent(request, id):
    today = date.today()
    pat = today.strftime("%Y-%m-%d")
    profile = request.user
    term = Term.objects.get(active=1).term
    Attendance.objects.filter(teacher = profile)
    last = Attendance.objects.filter(student = id).last()
    if(len(Attendance.objects.filter(student = id) & Attendance.objects.filter(lock = 0)) == 0):
        if(str(pat) != str(last.date)):
            Attendance.objects.create(student=id, teacher=request.user, term=term, status=0, lock=1, added_by=request.user)
            messages.success(request, 'marked')
            return redirect('attendance')
    
    if((Attendance.objects.filter(student = id).last()).lock == 0 ):
        if(str(pat) == str(last.date)):
            Attendance.objects.filter(student = id).update(status = 0)
            Attendance.objects.filter(student = id).update(lock = 1)
            messages.success(request, 'updated')
            return redirect('attendance')
        else:
            Attendance.objects.create(student=id, teacher=request.user, term=term, status=0, lock=1, added_by=request.user)
            messages.success(request, 'marked')
            return redirect('attendance')
    else:
        messages.warning(request, 'Student already marked')
        return redirect('attendance')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def unlockattendance(request):
    today = date.today()
    pat = today.strftime("%Y-%m-%d")
    reg = Attendance.objects.filter(student='')
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        print(reg)
        last = Attendance.objects.filter(student = reg).last()
        print(pat)
        print(last.date)
        if str(pat) == str(last.date):
            student = Attendance.objects.filter(student = reg) & Attendance.objects.filter(date = pat)
            student.update(lock = 0)
            messages.success(request, 'unlock')
            return redirect('attendance')
    return render(request, 'school/attendanceunlock.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def generatecard(request):
    if 'submit' in request.POST:
        pin = request.POST.get('pin')
        serial = request.POST.get('serial')
        Card.objects.create(pin=pin,serial=serial)
        messages.success(request, 'Created')
        return redirect('generatecard')
    return render(request, 'school/cardgenerate.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def userprofile(request):
    role = Role.objects.filter(active = 1)
    context = {'role':role}
    return render(request, 'school/userprofile.html', context)