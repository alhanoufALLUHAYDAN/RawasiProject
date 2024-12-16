from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InvestmentOpportunity
from investment_fund.models import InvestmentFund
from accounts.models import Leader
from django.contrib import messages
from investments.forms import InvestmentOpportunityForm
# Create your views here.

@login_required
def add_investment_opportunity(request):

    # if not hasattr(request.user, 'leader'):
    #     messages.error(request, "ليس لديك صلاحية لإضافة فرصة استثمارية. فقط المسؤول يمكنه إضافة الفرص.")
    #     return redirect('/')

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        company_name = request.POST.get('company_name')
        investment_type = request.POST.get('investment_type')
        total_investment = request.POST.get('total_investment')
        required_approval_percentage = request.POST.get('required_approval_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        expected_return = request.POST.get('expected_return')
        pdf_file = request.FILES.get('pdf_file')
        image = request.FILES.get('image')

    #   fund = InvestmentFund.objects.first()

    #   if not fund:
    #      messages.error(request, "لا يوجد صندوق استثماري في النظام. يرجى إضافة صندوق استثماري أولاً.")
    #        return redirect('investments:add_investment_opportunity')
        leader = Leader.objects.filter(user=request.user).first()  
        if not leader:
            messages.error(request, "المستخدم لا يملك قائد مرتبط به.")
            return redirect('some_error_page') 

        fund = InvestmentFund.objects.first()

        if not fund:
            fund = InvestmentFund.objects.create(
                name="صندوق افتراضي", 
                description="صندوق استثماري افتراضي   ",
                total_balance=0.0 ,
                leader=leader  
            )

        investment_opportunity = InvestmentOpportunity(
            title=title,
            description=description,
            company_name=company_name,
            investment_type=investment_type,
            total_investment=total_investment,
            required_approval_percentage=required_approval_percentage,
            start_date=start_date,
            end_date=end_date,
            expected_return=expected_return,
            fund=fund,  
            pdf_file=pdf_file, 
            image=image, 
        )

        investment_opportunity.save()

        messages.success(request, "تم إضافة الفرصة الاستثمارية بنجاح!")

        return redirect('/') 

    return render(request, 'investments/add_investment_opportunity.html')


@login_required
def investment_opportunity_detail(request, id):
    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)
    
    fund = investment_opportunity.fund
    
    # is_leader = hasattr(request.user, 'leader') and request.user.leader.fund == fund
    # is_investor = InvestorFund.objects.filter(investor__user=request.user, fund=fund).exists()

    # if not is_leader and not is_investor:
    #     messages.error(request, "ليس لديك صلاحية للوصول إلى تفاصيل هذه الفرصة الاستثمارية.")
    #     return redirect('/') 
    
    return render(request, 'investments/investment_opportunity_detail.html', {
        'investment_opportunity': investment_opportunity,
    })

@login_required
def delete_investment_opportunity(request, id):
    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)
    
    # if investment_opportunity.created_by != request.user and not hasattr(request.user, 'leader'):
    #     messages.error(request, "ليس لديك صلاحية لحذف فرصة الاستثمار.")
    #     return redirect('/')  

    investment_opportunity.delete()

    messages.success(request, "تم حذف الفرصة الاستثمارية بنجاح.")
    return redirect('/') 


def update_investment_opportunity(request, id):
    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)
    
    if request.method == 'POST':
        form = InvestmentOpportunityForm(request.POST, request.FILES, instance=investment_opportunity)
        if form.is_valid():
            form.save()
            return redirect('investments:investment_opportunity_detail', id=investment_opportunity.id)
    else:
        form = InvestmentOpportunityForm(instance=investment_opportunity)
    
    return render(request, 'investments/update_investment_opportunity.html', {'form': form})
