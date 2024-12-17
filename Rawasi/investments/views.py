from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InvestmentOpportunity
from investment_fund.models import InvestmentFund
from accounts.models import Leader
from django.contrib import messages
from investments.forms import InvestmentOpportunityForm
from datetime import datetime
from .models import InvestorFund, Voting , BuySellTransaction
from django.utils import timezone 
from datetime import timedelta
from accounts.models import CustomUser , Investor
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


# Create your views here.

@login_required
def add_investment_opportunity(request):
    leader = Leader.objects.filter(user=request.user).first()
    active_section = 'section4' 

    if not leader:
        messages.error(request, "فقط المسؤول يمكنه إضافة فرص استثمارية.")
        return redirect('dashboard:fund_dashboard_view') 

    if request.method == "POST":

        title = request.POST.get('title')
        description = request.POST.get('description')
        company_name = request.POST.get('company_name')
        investment_type = request.POST.get('investment_type')
        total_investment = request.POST.get('total_investment')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        expected_return = request.POST.get('expected_return')
        pdf_file = request.FILES.get('pdf_file')
        image = request.FILES.get('image')

        if not all([title, description, company_name, investment_type, total_investment, start_date, end_date, expected_return]):
            messages.error(request, "جميع الحقول مطلوبة.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        fund = InvestmentFund.objects.first()
        if not fund:
            messages.error(request, "لا يوجد صندوق استثماري في النظام. يرجى إضافة صندوق استثماري أولاً.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        if fund.leader != leader:
            messages.error(request, "لا يمكنك إضافة فرصة استثمارية لأنك لست المسؤول عن هذا الصندوق.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        if fund.is_active != 'Active':
            messages.error(request, "لا يمكن إضافة فرص استثمارية لأن الصندوق غير نشط.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date >= end_date:
                messages.error(request, "تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء.")
                return redirect(f'/dashboard/fund/?section={active_section}')
        except ValueError:
            messages.error(request, "تاريخ البدء والانتهاء غير صحيح.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        investment_opportunity = InvestmentOpportunity(
            title=title,
            description=description,
            company_name=company_name,
            investment_type=investment_type,
            total_investment=total_investment,
            start_date=start_date,
            end_date=end_date,
            expected_return=expected_return,
            fund=fund,
            pdf_file=pdf_file,
            image=image,
        )

        try:
            investment_opportunity.save()
            messages.success(request, "تم إضافة الفرصة الاستثمارية بنجاح!")
            return redirect(f'/dashboard/fund/?section={active_section}')
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء إضافة الفرصة الاستثمارية: {str(e)}")
            return redirect(f'/dashboard/fund/?section={active_section}')



    return render(request, 'investments/add_investment_opportunity.html')


@login_required
def investment_opportunity_detail(request, id):

    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)
    
    fund = investment_opportunity.fund
    is_leader = hasattr(request.user, 'leader') and request.user.leader.managed_fund == fund
    is_investor = InvestorFund.objects.filter(investor__user=request.user, fund=fund).exists()
    total_votes = investment_opportunity.votes.count()
    accepted_votes = investment_opportunity.votes.filter(vote='Accepted').count()

    if total_votes > 0:
        approval_percentage = (accepted_votes / total_votes) * 100
    else:
        approval_percentage = 0  

    user_vote = None
    if request.user.is_authenticated:
        user_vote = investment_opportunity.votes.filter(user=request.user).first()


    if not is_leader and not is_investor:
        messages.error(request, "ليس لديك صلاحية للوصول إلى تفاصيل هذه الفرصة الاستثمارية.")
        return redirect('/')

    return render(request, 'investments/investment_opportunity_detail.html', {
        'investment_opportunity': investment_opportunity,
        'approval_percentage': approval_percentage,
        'user_vote': user_vote,
    })

@login_required
def delete_investment_opportunity(request, id):
    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)

    leader = Leader.objects.filter(user=request.user).first()
    
    if not leader:
        messages.error(request, "ليس لديك صلاحية لحذف هذه الفرصة الاستثمارية.")
        return redirect('/')

    if investment_opportunity.fund.leader != leader:
        messages.error(request, "لا يمكنك حذف هذه الفرصة الاستثمارية لأنك لست المسؤول عن هذا الصندوق.")
        return redirect('/')

    investment_opportunity.delete()

    messages.success(request, "تم حذف الفرصة الاستثمارية بنجاح.")
    return redirect('/')
 

@login_required
def update_investment_opportunity(request, id):
    investment_opportunity = get_object_or_404(InvestmentOpportunity, id=id)
    
    leader = Leader.objects.filter(user=request.user).first()
    
    if not leader:
        messages.error(request, "ليس لديك صلاحية لتحديث هذه الفرصة الاستثمارية.")
        return redirect('/') 

    if investment_opportunity.fund.leader != leader:
        messages.error(request, "لا يمكنك تحديث هذه الفرصة الاستثمارية لأنك لست المسؤول عن هذا الصندوق.")
        return redirect('/')  
    
    if request.method == 'POST':
        form = InvestmentOpportunityForm(request.POST, request.FILES, instance=investment_opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الفرصة الاستثمارية بنجاح.")
            return redirect('investments:investment_opportunity_detail', id=investment_opportunity.id)
    else:
        form = InvestmentOpportunityForm(instance=investment_opportunity)
    
    return render(request, 'investments/update_investment_opportunity.html', {'form': form})


def add_voting(request):
    fund = InvestmentFund.objects.filter(leader__user=request.user).first()
    if not fund:
        raise PermissionDenied("You are not authorized to create a vote for any investment opportunity.")

    if request.method == "POST":
        opportunity_id = request.POST.get('opportunity')
        required_approval_percentage = request.POST.get('required_approval_percentage')
        voting_start_time = request.POST.get('voting_start_time')
        voting_end_time = request.POST.get('voting_end_time')
        total_amount = request.POST.get('total_amount')
        vote_type = request.POST.get('vote_type')  

        try:
            opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)
            
            if opportunity.fund != fund:
                raise PermissionDenied("You do not have permission to vote for this investment opportunity.")
            
            voting_start_time = datetime.strptime(voting_start_time, '%Y-%m-%dT%H:%M')
            voting_end_time = datetime.strptime(voting_end_time, '%Y-%m-%dT%H:%M')
            
            if voting_start_time >= voting_end_time:
                messages.error(request, "تاريخ بداية التصويت يجب أن يكون قبل تاريخ نهايته.")
                return redirect('add_voting')

            voting = Voting(
                opportunity=opportunity,
                user=request.user,
                required_approval_percentage=required_approval_percentage,
                voting_start_time=voting_start_time,
                voting_end_time=voting_end_time,
                total_amount=total_amount,
                vote_type=vote_type, 
            )
            voting.save()

            messages.success(request, "تم إضافة التصويت بنجاح!")
            return redirect('investments:add_voting')

        except InvestmentOpportunity.DoesNotExist:
            messages.error(request, "الفرصة الاستثمارية المحددة غير موجودة.")
            return redirect('investments:add_voting')
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('investments:add_voting')

    opportunities = InvestmentOpportunity.objects.filter(fund=fund, status='Open')
    
    return render(request, 'investments/add_voting.html', {'opportunities': opportunities})


