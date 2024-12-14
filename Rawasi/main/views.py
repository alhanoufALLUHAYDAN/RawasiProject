from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import ContactForm
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import random
import string
# Create your views here.

def home_view(request:HttpRequest):
    if request.method=="POST":
        
        contact_form=ContactForm(request.POST)
        
        if contact_form.is_valid():
              contact_form.save()
              #send confirmation email
              content_html = render_to_string("main/confirmation.html")
              send_to = contact_form.cleaned_data['email']
              print(send_to)
              print(settings.EMAIL_HOST_USER)
              email_message = EmailMessage("confiramation", content_html, settings.EMAIL_HOST_USER, [send_to])
              email_message.content_subtype = "html"
              #email_message.connection = email_message.get_connection(True)
              email_message.send()
 
              messages.success(request, 'شكرا لتواصلك معنا')
              return redirect(request.GET.get("next", "/"))
        else:
            print("form is not valid")
            print(contact_form.errors)   
    return render(request,'main/home.html')



def about_view(request:HttpRequest):
    return render(request,'main/about_us.html')



def generate_unique_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))



def fund_dashboard_view(request:HttpRequest):
    if not request.user.is_authenticated and request.user.leader :
        messages.error(request, 'مصرح فقط للاعضاء المسجلين',"danger")
        return redirect("main:home_view")
    
    unique_code = None
    if request.method == "POST" and "new_code" in request.POST:
        unique_code = generate_unique_code()
        print("Generated unique code:", unique_code)

    return render(request,'dashboard/fund_dashboard.html',
                  {"leader":request.user,
                   "unique_code":unique_code})


def investor_dashboard_view(request:HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, 'مصرح فقط للاعضاء المسجلين',"danger")
        return redirect("main:home_view")
    

    return render(request,'dashboard/investor_dashboard.html',
                  {"investor":request.user,
                   })
