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
from django.contrib.auth.decorators import login_required
from investment_fund.models import InvestmentFund, Wallet 
from investments.models import InvestmentFund
from investments.models import InvestorFund , InvestmentOpportunity
from investment_fund.models import InvestmentFund, Wallet
from investment_fund.forms import InvestmentFundForm 
from investments.models import InvestorFund,InvestmentOpportunity,InvestmentFund
from accounts.models import Investor
from django.contrib.auth.decorators import login_required
from datetime import date
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
    investments_list=[]
    fund_investors_list=[]
    CHlables_fund=[]
    CHdata_fund=[]
    # Check if an investment fund exists for the leader
    try:
        investment_fund = InvestmentFund.objects.get(leader=leader_instance)
        CHlables_fund.append('الاجمالي')
        CHlables_fund.append('الربح')
        CHdata_fund.append(investment_fund.total_balance)
        CHdata_fund.append(investment_fund.profit_balance)

        if investment_fund.investment_opportunities:
            investments=investment_fund.investment_opportunities.all()
            p=Paginator(investments,4)
            page=request.GET.get('page',1)
            investments_list=p.get_page(page)
        if investment_fund.fund_investments:    
            fund_investors = investment_fund.fund_investments.all().select_related('investor') 
            p=Paginator(fund_investors,6)
            page=request.GET.get('page',1)
            fund_investors_list=p.get_page(page)
            # Calculate the investor's age
            # Calculate the investor's age for each investor
            today = date.today()
            for investor_fund in fund_investors_list:
                birth_date = investor_fund.investor.user.date_of_birth
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                investor_fund.investor.age = age 
        
    except InvestmentFund.DoesNotExist:
        investment_fund = None

    # Fetch the user's wallet or create it if it doesn't exist
    wallet = getattr(request.user, 'wallet', None)  # Safe access to wallet
    if wallet is None:
        wallet = Wallet.objects.create(user=request.user)
        messages.info(request, "تم إنشاء محفظة جديدة لك.")

    # Ensure `total_balance` exists and is correctly updated in your fund model
    total_balance = investment_fund.total_balance if investment_fund else 0.0

    # Calculate the total profit from investment opportunities
    total_profit = 0
    if investment_fund:
        # Loop through all open opportunities in the fund
        for opportunity in investment_fund.investment_opportunities.filter(status='Open'):
            # Calculate profit based on total investment and expected return
            total_profit += (opportunity.expected_return * total_balance / 100)

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
        "investments":investments_list,
        "total_balance": total_balance,
        "total_profit": total_profit,
        "fund_investors":fund_investors_list,
        "CHlables_fund":CHlables_fund,
        "CHdata_fund":CHdata_fund,

    }

    return render(request, 'dashboard/fund_dashboard.html', context)

from decimal import Decimal
@login_required
def investor_dashboard_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'مصرح فقط للأعضاء المسجلين', "danger")
        return redirect("main:home_view")

    # Ensure wallet exists for the user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    CHlables_funds=[]
    CHdata_funds=[]
    if wallet.transactions.exists():
        transactions = wallet.transactions.order_by('-created_at')[:3]



    joined_funds = InvestorFund.objects.filter(investor__user=request.user)

    # Prepare profit data for each fund the investor has joined
    profit_data = []
    for investor_fund in joined_funds:
        # Fetch the related investment opportunity for each fund
        opportunity = InvestmentOpportunity.objects.filter(fund=investor_fund.fund).first()
        if opportunity:
            # Convert expected_return to Decimal to ensure consistency in data types
            expected_return = Decimal(opportunity.expected_return)
            # Calculate the investment period (in days) and the profit
            investment_period_days = (opportunity.end_date - opportunity.start_date).days
            profit = (investor_fund.amount_invested * expected_return * investment_period_days) / Decimal(365) / Decimal(100)
            profit_data.append({
                "fund_name": investor_fund.fund.name,
                "amount_invested": investor_fund.amount_invested,
                "profit": round(profit, 2),
                "status": opportunity.status if opportunity else 'No Opportunity'
            })
        else:
            # No investment opportunity for this fund
            profit_data.append({
                "fund_name": investor_fund.fund.name,
                "amount_invested": investor_fund.amount_invested,
                "profit": 0.0,
                "status": 'No Opportunity'
            })
        for data in profit_data:
            CHlables_funds.append(data['fund_name'])
        CHdata_funds = [float(data['profit']) for data in profit_data]

    # Handle joining a new fund via join_code
    if request.method == 'POST':
        join_code = request.POST.get('join_code', None)
        if join_code:
            try:
                # Fetch the investment fund using the join code and check if it's active
                fund = InvestmentFund.objects.get(join_code=join_code)
                if fund.is_active=='Inactive':
                    messages.warning(request, 'الصندوق غير نشط حاليا, لا يمكنك الانضمام', "warning")
                if InvestorFund.objects.filter(fund=fund, investor__user=request.user).exists():
                    messages.warning(request, 'أنت بالفعل عضو في هذا الصندوق.', "warning")
                else:
                    # If the user isn't already a member, allow them to join
                    investor = Investor.objects.get(user=request.user)
                    InvestorFund.objects.create(
                        fund=fund,
                        investor=investor,
                        amount_invested=0  # Default investment of 0 for new join
                    )
                    messages.success(request, f'تم الانضمام بنجاح إلى الصندوق: {fund.name}', "success")
            except InvestmentFund.DoesNotExist:
                messages.error(request, 'كود الانضمام غير صحيح أو الصندوق غير نشط.', "danger")

    return render(
        request, 
        'dashboard/investor_dashboard.html', 
        {
            "investor": request.user, 
            "wallet": wallet,
            "transactions": transactions,
            "joined_funds": joined_funds,  # Pass the joined funds
            "profit_data": profit_data,  # Pass the profit data with the correct status
            "CHlables_funds":CHlables_funds,
            "CHdata_funds":CHdata_funds,
        }
    )
