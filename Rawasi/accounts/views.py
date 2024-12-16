from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login ,logout , get_user_model
from django.contrib import messages
from accounts.models import CustomUser , Investor , Leader
from django.contrib.auth.decorators import login_required
from datetime import datetime , date
from django.http import JsonResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

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
            return redirect('main:investor_dashboard_view')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح!")
    return redirect('main:home_view')

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

        return JsonResponse({
            'full_name': user.full_name,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth,
            'profile_picture_url': user.profile_picture.url if user.profile_picture else None
        })
    
    return render(request, 'profile/profile.html', {
        'user': request.user
    })


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = get_user_model().objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            reset_link = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'إعادة تعيين كلمة المرور'
            message = render_to_string('accounts/reset_password/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            
            send_mail(
                subject, 
                message, 
                settings.EMAIL_HOST_USER, 
                [email], 
                fail_silently=False,
                html_message=message  
            )

            return redirect('accounts:reset_password_done')

        except get_user_model().DoesNotExist:
            return render(request, 'accounts/reset_password/password_reset.html', {'error': 'البريد الإلكتروني غير موجود في النظام.'})
    
    return render(request, 'accounts/reset_password/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except Exception as e:
        return redirect('accounts:reset_password')

    if default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            return redirect('accounts:login')
        
        return render(request, 'accounts/reset_password/password_reset_confirm.html', {'uid': uid, 'token': token})
    return redirect('accounts:reset_password')
    

def reset_password_done(request):
    return render(request, 'accounts/reset_password/password_reset_done.html')
