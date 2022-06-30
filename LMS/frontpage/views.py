from django.shortcuts import redirect, render
from school.models import Config, Card, Student, Result, Record, Comment, Term, Class

# Create your views here.

def home(request):
    config = Config.objects.all()
    group = Class.objects.all()
    term = Term.objects.all()
    sch_name = Config.objects.get(id=1).school_name
    error = False
    if 'submit' in request.POST:
        reg = request.POST.get('student')
        pin = request.POST.get('pin')
        serial = request.POST.get('serial')

        if Student.objects.filter(registration_number=reg).exists():
            getpinserial = Card.objects.filter(pin=pin,serial=serial)
            try:
                usage = Card.objects.get(pin = pin).usage
            except Card.DoesNotExist:
                error=True
            if len(getpinserial) == 1:
                if usage == 0:
                    student = Student.objects.get(registration_number = reg).id
                    return redirect('result',student)
                else:
                    error = True
            else:
                error = True
        else:
            error = True
    context = {
        'config':config,
        'name':sch_name.upper(),
        'error':error,
    }
    return render(request, 'frontpage/index.html', context)

def result(request,pk):
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
    return render(request,'frontpage/result.html',context)