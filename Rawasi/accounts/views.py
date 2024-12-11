from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import CustomUser , Investor , Leader
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime , date
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string



# Create your views here.

def choose_role(request):
    return render(request, 'accounts/choose_role.html')


def registration(request):
    role = request.GET.get('role')
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profile_image = request.FILES.get('profile_image') 
        email = request.POST.get('email') 
       
        try:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, 'تاريخ الميلاد غير صحيح.')
            return redirect('accounts:registration')
        today = date.today()
        age = today.year - date_of_birth.year
        if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1

        if age < 18:
            messages.error(request, 'يجب أن يكون عمرك 18 سنة أو أكثر للتسجيل.')
            return redirect('accounts:registration')
        
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'رقم الهاتف المدخل موجود بالفعل. الرجاء استخدام رقم مختلف.')
            return redirect('accounts:registration')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل. الرجاء اختيار اسم آخر.')
            return redirect('accounts:registration')
        if len(password) < 8:
            messages.error(request, 'كلمة المرور يجب أن تكون على الأقل 8 أحرف.')
            return redirect('accounts:registration')
        if not any(char.isupper() for char in password):
            messages.error(request, 'كلمة المرور يجب أن تحتوي على حرف كبير على الأقل.')
            return redirect('accounts:registration')
        if not any(char.isdigit() for char in password):
            messages.error(request, 'كلمة المرور يجب أن تحتوي على رقم على الأقل.')
            return redirect('accounts:registration')
        if not any(char in '!@#$%^&*' for char in password):
            messages.error(request, 'كلمة المرور يجب أن تحتوي على رمز خاص مثل !@#$%^&*')
            return redirect('accounts:registration')

        user = CustomUser.objects.create_user(
            username=username, password=password, full_name=full_name,
            date_of_birth=date_of_birth, phone_number=phone_number ,email=email,
        )

        if profile_image:
            user.profile_image = profile_image  
            user.save()

        if role == 'leader':
            print("Creating leader record...")
            leader = Leader.objects.create(user=user)  
            print(f"Leader created: {leader.user.full_name}")
        elif role == 'investor':
            print("Creating investor record...")
            investor = Investor.objects.create(user=user) 
            print(f"Investor created: {investor.user.full_name}")
        messages.success(request, f'تم التسجيل بنجاح !')
        return redirect('accounts:login')

    return render(request, 'accounts/registration.html', {'role': role})


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
    return render(request, 'profile/profile.html', {
        'user': request.user
    })

@login_required
def update_profile(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        profile_picture = request.FILES.get('profile_picture')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        user = request.user 

        if full_name:
            user.full_name = full_name
        if email:
            user.email = email
        if phone_number:
            user.phone_number = phone_number
        if date_of_birth:
            user.date_of_birth = date_of_birth
        if profile_picture:
            user.profile_picture = profile_picture 

        if password and password == password_confirm:
            user.set_password(password)  

        user.save()

        messages.success(request, 'تم حفظ التعديلات بنجاح!')
        return redirect('accounts:profile') 

    return render(request, 'profile/update_profile.html')


