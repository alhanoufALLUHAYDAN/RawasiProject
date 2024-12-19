from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InvestmentOpportunity
from investment_fund.models import InvestmentFund
from accounts.models import Leader
from django.contrib import messages
from investments.forms import InvestmentOpportunityForm
from datetime import datetime
from .models import InvestorFund, Voting , BuySellTransaction
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from decimal import Decimal



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

        fund = leader.managed_fund
        print(fund.is_active)
        if not fund:
            messages.error(request, "لا يوجد صندوق استثماري في النظام. يرجى إضافة صندوق استثماري أولاً.")
            return redirect(f'/dashboard/fund/?section={active_section}')

        '''if fund.leader != leader:
            messages.error(request, "لا يمكنك إضافة فرصة استثمارية لأنك لست المسؤول عن هذا الصندوق.")
            return redirect(f'/dashboard/fund/?section={active_section}')'''

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

    buy_votes_accepted = investment_opportunity.votes.filter(vote_type='Buy', vote='Accepted').count()
    sell_votes_accepted = investment_opportunity.votes.filter(vote_type='Sell', vote='Accepted').count()
    total_investors = InvestorFund.objects.filter(fund=fund).count()

    approval_percentage_buy = (buy_votes_accepted / total_investors) * 100 if total_investors else 0
    approval_percentage_sell = (sell_votes_accepted / total_investors) * 100 if total_investors else 0
    


    user_vote = None
    if request.user.is_authenticated:
        user_vote = investment_opportunity.votes.filter(user=request.user).first()


    if not is_leader and not is_investor:
        messages.error(request, "ليس لديك صلاحية للوصول إلى تفاصيل هذه الفرصة الاستثمارية.")
        return redirect('/')
    # calculates days
    left_days = (investment_opportunity.end_date - investment_opportunity.start_date).days

    
    

    return render(request, 'investments/investment_opportunity_detail.html', {
        'investment_opportunity': investment_opportunity,
        'approval_percentage': approval_percentage,
        'user_vote': user_vote,
        "left_days":left_days,
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
    try:
        voting_start_time = datetime.strptime(voting_start_time, '%Y-%m-%d')
        voting_end_time = datetime.strptime(voting_end_time, '%Y-%m-%d')
        if voting_start_time >= voting_end_time:
         messages.error(request, "تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء.")
    except ValueError:
         messages.error(request, "تاريخ البدء والانتهاء غير صحيح.")
    
    if request.method == 'POST':
        form = InvestmentOpportunityForm(request.POST, request.FILES, instance=investment_opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الفرصة الاستثمارية بنجاح.")
            return redirect('investments:investment_opportunity_detail', id=investment_opportunity.id)
    else:
        form = InvestmentOpportunityForm(instance=investment_opportunity)
    
    return render(request, 'investments/update_investment_opportunity.html', {'form': form})


@login_required
def add_voting(request):
    active_section = 'section2' 
    try:
        leader = request.user.leader 
        fund = leader.managed_fund
    except Leader.DoesNotExist:
        fund = None
    if not fund:
        raise PermissionDenied("ليس لديك صلاحية للوصول إلى هذا الصندوق الاستثماري.")
    
    '''try:
            investor_fund = InvestorFund.objects.get(investor__user=request.user, fund=fund)
        except InvestorFund.DoesNotExist:
            messages.error(request, "لم تقم بالاستثمار في هذا الصندوق بعد. لا يمكنك التصويت.")
            return redirect('investments:opportunity_list')'''

    if request.method == "POST":
        opportunity_id = request.POST.get('opportunity')
        required_approval_percentage = float(request.POST.get('required_approval_percentage'))
        voting_start_time = request.POST.get('voting_start_time')
        voting_end_time = request.POST.get('voting_end_time')
        total_amount = request.POST.get('total_amount')
        vote_type = 'Buy'

        try:
            opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)
            
            if opportunity.fund != fund:
                raise PermissionDenied("ليس لديك صلاحية لوضع تصويت على هذه الفرصة الاستثمارية.")

            if Voting.objects.filter(opportunity=opportunity, vote_type='Sell', vote='Accepted').exists():
                messages.error(request, "تمت الموافقة على تصويت البيع لهذه الفرصة. لا يمكن إضافة تصويت جديد للبيع.")
                return redirect('investments:add_voting')
            
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
            print(f"قبل إضافة التصويت، حالة الفرصة: {opportunity.status}")

            print(f"فرصة الاستثمار: {opportunity}")
            print(f"البيانات الخاصة بالتصويت: {voting}")            

            messages.success(request, "تم إضافة التصويت بنجاح!")
            return redirect(f'/dashboard/fund/?section={active_section}') 

        except InvestmentOpportunity.DoesNotExist:
            messages.error(request, "الفرصة الاستثمارية المحددة غير موجودة.")
            return redirect('investments:add_voting')
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('investments:add_voting')

    opportunities = InvestmentOpportunity.objects.filter(fund=fund)
    return render(request, 'investments/add_voting.html', {'opportunities': opportunities})


@login_required
def opportunity_list(request):
    opportunities = []
    user_investor = False  

    if hasattr(request.user, 'leader'):  
        leader = request.user.leader
        opportunities = InvestmentOpportunity.objects.filter(fund__leader=leader)
    
    elif hasattr(request.user, 'investor'):
        investor = request.user.investor
        funds_invested_in = InvestorFund.objects.filter(investor=investor).values_list('fund', flat=True)
        opportunities = InvestmentOpportunity.objects.filter(fund__in=funds_invested_in)
        
        user_investor = True 

    for opportunity in opportunities:
        if hasattr(request.user, 'leader'):
            total_investors = InvestorFund.objects.filter(fund=opportunity.fund).exclude(investor__user=request.user).count()
        else:
            total_investors = InvestorFund.objects.filter(fund=opportunity.fund).count()

        total_accepted = Voting.objects.filter(opportunity=opportunity, vote='Accepted').count()
        total_rejected = Voting.objects.filter(opportunity=opportunity, vote='Rejected').count()
        approval_percentage = (total_accepted / total_investors) * 100 if total_investors else 0
        
        try:
            required_percentage = Voting.objects.filter(opportunity=opportunity).first().required_approval_percentage
        except AttributeError:
            required_percentage = 0  

        opportunity.approval_percentage = approval_percentage
        opportunity.required_approval_percentage = required_percentage
        opportunity.pending_votes = Voting.objects.filter(opportunity=opportunity, vote='Pending').count()
        opportunity.accepted_votes = total_accepted
        opportunity.rejected_votes = total_rejected
        
        if approval_percentage >= required_percentage:
            opportunity.status = 'Closed'  
        else:
            opportunity.status = 'Open'

        opportunity.buy_vote_completed = approval_percentage >= required_percentage
        opportunity.sell_vote_completed = Voting.objects.filter(opportunity=opportunity, vote_type='Sell', vote='Accepted').exists()


        opportunity.sell_vote_opened = (opportunity.status == 'Open' and
                                        Voting.objects.filter(opportunity=opportunity, vote_type='Sell').exists())
        
        if opportunity.status == 'Closed' and request.user == opportunity.fund.leader.user:
            if 'reopen_vote' in request.POST:
                opportunity.status = 'Open'
                opportunity.save()

                Voting.objects.filter(opportunity=opportunity).delete()

                if not Voting.objects.filter(opportunity=opportunity, vote_type='Sell').exists():
                    Voting.objects.create(
                        opportunity=opportunity,
                        user=request.user,
                        vote_type='Sell',
                        vote='Pending',
                        required_approval_percentage=opportunity.required_approval_percentage,
                    )
                
                messages.success(request, "تم إعادة فتح التصويت وإضافة تصويت البيع بنجاح.")
                return redirect('investments:opportunity_list')

    return render(request, 'investments/opportunity_list.html', {
        'opportunities': opportunities,
        'user_investor': user_investor, 
    })


@login_required
def vote_on_opportunity(request, id):
    active_section = 'section2'
    try:
        opportunity = InvestmentOpportunity.objects.get(id=id)
    except InvestmentOpportunity.DoesNotExist:
        messages.error(request, "الفرصة الاستثمارية غير موجودة.")
        return redirect('investments:opportunity_list')
    
    if opportunity.status != 'Open':
        messages.error(request, "التصويت مغلق لهذه الفرصة.")
        return redirect('investments:opportunity_list')
    
    existing_vote = Voting.objects.filter(opportunity=opportunity, user=request.user).first()  
    
    if existing_vote:
        if existing_vote.vote == 'Pending':
            pass  
        else:
            messages.error(request, "لقد قمت بالتصويت مسبقًا.")
            return redirect('investments:opportunity_list')

    vote_choice = request.POST.get('vote_choice')
    if vote_choice not in ['Accepted', 'Rejected']:
        messages.error(request, "التصويت غير صالح.")
        return redirect('investments:opportunity_list')
   
    if existing_vote:
        existing_vote.vote = vote_choice  
        existing_vote.save()
        messages.success(request, f"تم تحديث التصويت بنجاح: {vote_choice}")
    else:
        Voting.objects.create(
            opportunity=opportunity,
            user=request.user,
            vote=vote_choice
        )
        messages.success(request, f"تم التصويت بنجاح: {vote_choice}")
    
    return redirect(f'/dashboard/fund/?section={active_section}')


def update_voting_time(request, id):
    vote = get_object_or_404(Voting, id=id)

    if request.method == 'POST':
        new_end_time = request.POST.get('new_end_time')
        
        if new_end_time:
            vote.end_time = new_end_time
            vote.save()
            messages.success(request, "تم تحديث وقت التصويت بنجاح.")
        else:
            messages.error(request, "الوقت غير صالح.")

        return redirect('investments:opportunity_list')

    return render(request, 'investments/update_voting_time.html', {'vote': vote})

from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from decimal import Decimal
from .models import InvestmentFund, InvestmentOpportunity, BuySellTransaction

@login_required
def buy_opportunity(request, opportunity_id):
    try:
        fund = InvestmentFund.objects.get(leader__user=request.user)

        if not fund:
            raise PermissionDenied("ليس لديك صلاحية للوصول.")
        
        opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)

        if BuySellTransaction.objects.filter(opportunity=opportunity, transaction_type='Buy', status='Approved').exists():
            messages.add_message(request, messages.ERROR, 'تم شراء هذه الفرصة بالفعل.')
            return redirect('investments:investment_opportunity_detail', id=opportunity.id)

        total_balance = Decimal(fund.total_balance)
        total_investment = Decimal(opportunity.total_investment)

        if total_balance >= total_investment:
            fund.total_balance = total_balance - total_investment
            fund.save()

            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Buy',
                amount=opportunity.total_investment,
                status='Approved'
            )

            messages.add_message(request, messages.SUCCESS, f"تم شراء الفرصة {opportunity.title} بنجاح.")

            return redirect('investments:investment_opportunity_detail', id=opportunity.id)
        else:
            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Buy',
                amount=opportunity.total_investment,
                status='Rejected'
            )

            messages.add_message(request, messages.ERROR, 'رصيد الصندوق غير كافٍ لإتمام عملية الشراء.')

            return redirect('investments:investment_opportunity_detail', id=opportunity.id)

    except InvestmentOpportunity.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'الفرصة الاستثمارية غير موجودة.')
        return redirect('investments:opportunity_list')

@login_required
def sell_opportunity(request, opportunity_id):
    fund = InvestmentFund.objects.get(leader__user=request.user)
    
    if not fund:
        raise PermissionDenied("ليس لديك صلاحية للوصول.")

    try:
        opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)

        if BuySellTransaction.objects.filter(opportunity=opportunity, transaction_type='Sell', status='Approved').exists():
            messages.add_message(request, messages.ERROR, 'تم بيع هذه الفرصة بالفعل.')
            return redirect('investments:investment_opportunity_detail', id=opportunity.id)

        investment = InvestorFund.objects.filter(fund=fund, amount_invested__gte=opportunity.total_investment)

        if investment:
            profit = calculate_profit_for_sale(opportunity.total_investment, opportunity.expected_return)

            fund.total_balance = Decimal(fund.total_balance) + Decimal(opportunity.total_investment)
            fund.save()

            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Sell',  
                amount=Decimal(opportunity.total_investment),  
                status='Approved' 
            )

            messages.add_message(request, messages.SUCCESS, f"تم بيع الفرصة {opportunity.title} بنجاح. الربح المحقق: {profit} ريـال.")

            return redirect('investments:investment_opportunity_detail', id=opportunity.id)
        else:
            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Sell', 
                amount=Decimal(opportunity.total_investment),
                status='Rejected' 
            )

            messages.add_message(request, messages.ERROR, 'ليس لديك استثمار كافي لإتمام عملية البيع.')

            return redirect('investments:investment_opportunity_detail', id=opportunity.id)

    except InvestmentOpportunity.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'الفرصة الاستثمارية غير موجودة.')
        return redirect('investments:opportunity_list')


def calculate_profit_for_sale(amount_invested, expected_return):

    amount_invested = Decimal(amount_invested)
    expected_return = Decimal(expected_return)
    
    profit = amount_invested * (expected_return / Decimal(100))
    
    return round(profit, 2)


