from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import ContactForm
# Create your views here.

def home_view(request:HttpRequest):
    if request.method=="POST":
        
        contact_form=ContactForm(request.POST)
        
        if contact_form.is_valid():
              contact_form.save()
              #send confirmation email
              #content_html = render_to_string("main/mail/confirmation.html")
              #send_to = contact_form.cleaned_data['email']
              #print(send_to)
              #email_message = EmailMessage("confiramation", content_html, settings.EMAIL_HOST_USER, [send_to])
              #email_message.content_subtype = "html"
              #email_message.connection = email_message.get_connection(True)
              #email_message.send()
 
              messages.success(request, 'شكرا لتواصلك معنا')
              return redirect('main:home_view')
        else:
            print("form is not valid")
            print(contact_form.errors)   
    return render(request,'main/home.html')



def about_view(request:HttpRequest):
    return render(request,'main/about_us.html')
