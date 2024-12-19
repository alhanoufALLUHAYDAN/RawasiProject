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
from django.http import JsonResponse


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
    fund = InvestmentFund.objects.filter(leader__user=request.user).first()
    if not fund:
        raise PermissionDenied("ليس لديك صلاحية للوصول إلى هذا الصندوق الاستثماري.")

    if request.method == "POST":
        opportunity_id = request.POST.get('opportunity')
        required_approval_percentage = float(request.POST.get('required_approval_percentage'))
        voting_start_time = request.POST.get('voting_start_time')
        voting_end_time = request.POST.get('voting_end_time')
        total_amount = request.POST.get('total_amount')
        vote_type = request.POST.get('vote_type') 

        try:
            opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)
            
            if opportunity.fund != fund:
                raise PermissionDenied("ليس لديك صلاحية للتصويت على هذه الفرصة الاستثمارية.")

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

            messages.success(request, "تم إضافة التصويت بنجاح!")
            return redirect('investments:opportunity_list') 

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
    opportunities = InvestmentOpportunity.objects.filter()

    for opportunity in opportunities:
        user_investor = InvestorFund.objects.filter(fund=opportunity.fund, investor__user=request.user).exists()
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

        if opportunity.status == 'Closed' and request.user == opportunity.fund.leader.user:
            if 'reopen_vote' in request.POST:  
                opportunity.status = 'Open' 
                opportunity.save()

                Voting.objects.filter(opportunity=opportunity).update(vote='Pending')

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

        if request.method == 'POST' and 'vote_choice' in request.POST:
            vote_choice = request.POST['vote_choice']
            vote_id = request.POST['vote_id']

            existing_vote = Voting.objects.filter(opportunity=opportunity, user=request.user).first()
            if existing_vote:
                messages.error(request, "لقد قمت بالتصويت مسبقًا.")
            else:
                Voting.objects.create(
                    user=request.user,
                    opportunity=opportunity,
                    vote=vote_choice
                )
                messages.success(request, "تم التصويت بنجاح!")
                return redirect('investments:opportunity_list')

    return render(request, 'investments/opportunity_list.html', {
        'opportunities': opportunities,
        'user_investor': user_investor, 
    })

@login_required
def vote_on_opportunity(request, id):
    try:
        opportunity = InvestmentOpportunity.objects.get(id=id)
    except InvestmentOpportunity.DoesNotExist:
        messages.error(request, "الفرصة الاستثمارية غير موجودة.")
        return redirect('investments:opportunity_list')
    if opportunity.status not in ['Open', 'Reopened']:
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
    return redirect('investments:opportunity_list')


@login_required
def buy_opportunity(request, opportunity_id):
    fund = InvestmentFund.objects.filter(leader__user=request.user).first()
    if not fund:
        raise PermissionDenied("ليس لديك صلاحية للوصول.")

    try:
        opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)

        fund = InvestmentFund.objects.get(id=opportunity.fund.id)

        if fund.total_balance >= opportunity.total_investment:
            fund.total_balance -= opportunity.total_investment
            fund.save()

            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Buy',
                amount=opportunity.total_investment,
                status='Approved' 
            )

            return JsonResponse({
                'status': 'success',
                'message': f'تم شراء الفرصة {opportunity.title} بنجاح.'
            })
        else:
         
            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Buy',
                amount=opportunity.total_investment,
                status='Rejected'  
            )

            return JsonResponse({
                'status': 'error',
                'message': 'رصيد الصندوق غير كافٍ لإتمام عملية الشراء.'
            })

    except InvestmentOpportunity.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الفرصة الاستثمارية غير موجودة.',
        })


@login_required
def sell_opportunity(request, opportunity_id):
    fund = InvestmentFund.objects.filter(leader__user=request.user).first()
    
    if not fund:
        raise PermissionDenied("ليس لديك صلاحية للوصول.")

    try:
        opportunity = InvestmentOpportunity.objects.get(id=opportunity_id)

        investment = InvestorFund.objects.filter(fund=fund, amount_invested__gte=opportunity.total_investment).first()

        if investment:
            profit = calculate_profit_for_sale(opportunity.total_investment, opportunity.expected_return)

            fund.total_balance += opportunity.total_investment
            fund.save()

            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Sell',  
                amount=opportunity.total_investment,  
                status='Approved' 
            )

          
            return JsonResponse({
                'status': 'success',
                'message': f'تم بيع الفرصة {opportunity.title} بنجاح. الربح المحقق: {profit} ريـال.',
                'profit': profit 
            })
        else:
          
            BuySellTransaction.objects.create(
                opportunity=opportunity,
                transaction_type='Sell', 
                amount=opportunity.total_investment,
                status='Rejected' 
            )

            

    except InvestmentOpportunity.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'الفرصة الاستثمارية غير موجودة.',
        })

def calculate_profit_for_sale(amount_invested, expected_return):
   
    profit = float(amount_invested) * (expected_return / 100)
    return round(profit, 2)


