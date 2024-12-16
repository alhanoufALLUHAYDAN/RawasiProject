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
from investment_fund.models import InvestmentFund, Wallet
from investment_fund.forms import InvestmentFundForm 
from investments.models import InvestmentFund
from investments.models import InvestorFund
from accounts.models import Investor
# Create your views here.

def home_view(request:HttpRequest):
    if request.method=="POST":
        
        contact_form=ContactForm(request.POST)
        
        if contact_form.is_valid():
              contact_form.save()
              #send confirmation email
              content_html = render_to_string("main/confirmation.html",{"username":contact_form.cleaned_data['full_name']})
              send_to = contact_form.cleaned_data['email']
              print(send_to)
              print(settings.EMAIL_HOST_USER)
              email_message = EmailMessage("confiramation", content_html, settings.EMAIL_HOST_USER, [send_to])
              email_message.content_subtype = "html"
              #email_message.connection = email_message.get_connection(True)
              email_message.send()
              messages.success(request, 'شكرا لتواصلك معنا')
              request.session['show_message'] = 'success'  # Store the message type in session
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


def fund_dashboard_view(request):
    # Ensure user is authenticated
    if not request.user.is_authenticated or not hasattr(request.user, 'leader'):
        messages.error(request, 'مصرح فقط للأعضاء المسجلين', "danger")
        return redirect("main:home_view")

    # Fetch the related leader instance
    leader_instance = request.user.leader

    # Check if an investment fund exists for the leader
    try:
        investment_fund = InvestmentFund.objects.get(leader=leader_instance)
    except InvestmentFund.DoesNotExist:
        investment_fund = None
    # Fetch the user's wallet
    wallet = getattr(request.user, 'wallet', None)  # Safe access to wallet
    # Handle new join code generation
    if request.method == "POST" and "new_code" in request.POST:
        new_code = generate_unique_code()
        if investment_fund:
            investment_fund.join_code = new_code
            investment_fund.save()
            messages.success(request, f"تم إنشاء رمز الانضمام: {new_code}")
    else:
        new_code = investment_fund.join_code if investment_fund else None

    context = {
        "leader": leader_instance,
        "investment_fund": investment_fund,
        "unique_code": new_code,
        "wallet": wallet,
    }
    return render(request, 'dashboard/fund_dashboard.html', context)

    
def investor_dashboard_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'مصرح فقط للأعضاء المسجلين', "danger")
        return redirect("main:home_view")

    # Ensure wallet exists for the user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        join_code = request.POST.get('join_code', None) 

        if join_code:

            try:

                fund = InvestmentFund.objects.get(join_code=join_code, is_active='Active')
                if InvestorFund.objects.filter(fund=fund, investor__user=request.user).exists():
                    messages.warning(request, 'أنت بالفعل عضو في هذا الصندوق.', "warning")
                else:
                    investor = Investor.objects.get(user=request.user)
                    InvestorFund.objects.create(
                        fund=fund,
                        investor=investor, 
                        amount_invested=0 
                    )

                    messages.success(request, f'تم الانضمام بنجاح إلى الصندوق: {fund.name}', "success")
            except InvestmentFund.DoesNotExist:
                messages.error(request, 'كود الانضمام غير صحيح أو الصندوق غير نشط.', "danger")

    return render(request, 'dashboard/investor_dashboard.html', {"investor": request.user,"wallet": wallet,})
