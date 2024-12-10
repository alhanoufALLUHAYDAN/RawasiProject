from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import CustomUser , Investor , Leader
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

# Create your views here.

def choose_role(request):
    return render(request, 'accounts/choose_role.html')

def leader_registration(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, 'تاريخ الميلاد غير صحيح.')
            return redirect('accounts:leader_registration')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'رقم الهاتف المدخل موجود بالفعل. الرجاء استخدام رقم مختلف.')
            return redirect('accounts:leader_registration')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل. الرجاء اختيار اسم آخر.')
            return redirect('accounts:leader_registration')

        user = CustomUser.objects.create_user(username=username, password=password, full_name=full_name, date_of_birth=date_of_birth, phone_number=phone_number)

        try:
            user.clean()  
        except ValidationError as e:
            messages.error(request, f"خطأ في البيانات: {e.message}")
            return redirect('accounts:leader_registration')

        leader = Leader.objects.create(user=user)

        messages.success(request, 'تم التسجيل كمشرف بنجاح!')
        return redirect('accounts:login')

    return render(request, 'accounts/leader_registration.html')


def investor_registration(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, 'تاريخ الميلاد غير صحيح.')
            return redirect('accounts:investor_registration')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'رقم الهاتف المدخل موجود بالفعل. الرجاء استخدام رقم مختلف.')
            return redirect('accounts:investor_registration')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل. الرجاء اختيار اسم آخر.')
            return redirect('accounts:investor_registration')

        user = CustomUser(
            username=username,
            full_name=full_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )
        
        try:
            user.clean()  
        except ValidationError as e:
            messages.error(request, f"خطأ في البيانات: {e.message}")
            return redirect('accounts:investor_registration')

        user = CustomUser.objects.create_user(username=username, password=password, full_name=full_name, date_of_birth=date_of_birth, phone_number=phone_number)

        investor = Investor.objects.create(user=user)

        messages.success(request, 'تم التسجيل كمستثمر بنجاح!')
        return redirect('accounts:login')

    return render(request, 'accounts/investor_registration.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'تم تسجيل الدخول بنجاح!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح!")
    return redirect('accounts:login')

@login_required
def profile(request):
    return render(request, 'profile/profile.html')

@login_required
def update_profile(request):
    user = request.user 

    if request.method == 'POST':

        user.full_name = request.POST.get('full_name', user.full_name)
        user.date_of_birth = request.POST.get('date_of_birth', user.date_of_birth)
        user.phone_number = request.POST.get('phone_number', user.phone_number)

        try:
            user.clean() 
            user.save() 
            messages.success(request, 'تم تحديث البيانات بنجاح!')
            return redirect('accounts:profile')
        except ValidationError as e:
            messages.error(request, str(e))  

    return render(request, 'profile/update_profile.html', {
        'user': user 
    })