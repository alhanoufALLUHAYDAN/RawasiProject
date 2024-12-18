from django.shortcuts import render, get_object_or_404, redirect
from .forms import InvestmentFundForm  
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Wallet, InvestmentFund, Transactions
from investments.models import InvestorFund,InvestmentOpportunity,BuySellTransaction
from accounts.models import Investor

def create_investment_fund(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        # total_balance = request.POST.get("total_balance")
        is_active = request.POST.get("is_active")  # Convert string to boolean

        # Check if the leader already has an investment fund
        if hasattr(request.user, 'leader') and hasattr(request.user.leader, 'managed_fund'):
            messages.error(request, "لا يمكنك إنشاء أكثر من صندوق استثماري.")
            return redirect("main:fund_dashboard_view")

        # Validate the inputs
        if not all([name, description]):
            messages.error(request, "الرجاء ملء جميع الحقول المطلوبة.")
            return redirect("main:fund_dashboard_view")

        # Create the investment fund
        try:
            InvestmentFund.objects.create(
                name=name,
                description=description,
                # total_balance=total_balance,
                is_active=is_active,
                leader=request.user.leader  # Link the fund to the current leader
            )
            # investor = Investor.objects.get(user=request.user)
            # InvestorFund.objects.create(
            #             fund=fund,
            #             investor=investor,
            #             amount_invested=0
            #         )
            messages.success(request, "تم إنشاء الصندوق الاستثماري بنجاح!")
        except Exception as e:
            messages.error(request, f"حدث خطأ: {e}")
        
        return redirect("main:fund_dashboard_view")
    else:
        return redirect("main:fund_dashboard_view")



def investment_fund_detail(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)
    return render(request, 'investment_fund/detail.html', {'fund': fund})

def investment_fund_list(request):
    funds = InvestmentFund.objects.all()
    return render(request, 'investment_fund/list.html', {'funds': funds})

@login_required
def update_investment_fund(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)  

    if request.method == "POST":
        form = InvestmentFundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الصندوق "{fund.name}" بنجاح.')
            return redirect('main:fund_dashboard_view')  
        else:
            print("Form errors:", form.errors)
            messages.error(request, "يوجد خطأ في البيانات، يرجى تصحيحها.")
    else:
        form = InvestmentFundForm(instance=fund)  # Pre-fill the form with existing data

    return render(request, 'investment_fund/update.html', {
        'form': form,
        'fund': fund  
    })



def delete_investment_fund(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)
    if request.method == "POST":
        fund.delete()
        messages.success(request, "تم حذف الصندوق بنجاح.")
        return redirect('main:fund_dashboard_view')
    return redirect('main:fund_dashboard_view')

#------------------------------------------ Wallet login 
@login_required
def wallet_view(request):
    try:
        # Fetch the wallet for the logged-in user
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        # If the wallet doesn't exist, create one automatically
        wallet = Wallet.objects.create(user=request.user)
        messages.info(request, "تم إنشاء محفظة جديدة لك.")

    # Fetch all transactions related to the user's wallet
    transactions = wallet.transactions.all().order_by('-created_at')  # Sort by date (most recent first)

    context = {
        'wallet': wallet,
        'transactions': transactions,  
    }

    return render(request, 'investment_fund/wallet_detail.html', context)
#----------------------------------------------------- Transaction logic 

@login_required
def deposit_to_wallet(request):
    if request.method == 'POST':
        try:
            # 1. Retrieve and validate amount from the form
            amount = Decimal(request.POST.get('amount', '0'))  # Convert to Decimal
            description = request.POST.get('description', '')

            if amount <= 0:
                messages.error(request, "المبلغ يجب أن يكون أكبر من 0.")
                return redirect('investment_fund:wallet_view')

            # 2. Get or create the user's wallet
            wallet, _ = Wallet.objects.get_or_create(user=request.user)

            # 3. Update wallet balance
            wallet.balance += amount
            wallet.save()

            # 4. Log the transaction (pass None for the fund)
            Transactions.objects.create(
                wallet=wallet,
                fund=None,  # Explicitly pass None for the fund
                transaction_type="Deposit",
                amount=amount,
                description=description,
                created_at=timezone.now()
            )

            # 5. Success message and redirect
            messages.success(request, f"تم إيداع {amount} ريال إلى محفظتك.")
            return redirect('investment_fund:wallet_view')

        except ValueError:
            # Handle invalid input
            messages.error(request, "الرجاء إدخال مبلغ صالح.")
            return redirect('investment_fund:wallet_view')

    else:
        # If it's a GET request, just show the user's current wallet information
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        context = {
            'wallet': wallet, 
        }

        return render(request, 'main/investor_dashboard.html', context)

from decimal import Decimal 

@login_required
def transfer_to_fund(request, pk=None):
    """Transfer money from the user's wallet to a selected investment fund."""
    # Fetch the list of funds the user has joined
    joined_funds = InvestorFund.objects.filter(investor__user=request.user)

    # Handle the transfer for a specific fund if 'pk' is provided
    if pk:
        fund = get_object_or_404(InvestmentFund, id=pk)
    else:
        fund = None

    wallet = Wallet.objects.get(user=request.user)

    if request.method == 'POST':
        try:
            # Validate input
            amount = Decimal(request.POST.get('amount', '0'))  # Convert to Decimal
            description = request.POST.get('description', '')
            fund_id = request.POST.get('fund_id')  # Get the selected fund ID

            # Get the selected fund
            selected_fund = get_object_or_404(InvestmentFund, id=fund_id)

            if amount <= 0:
                messages.error(request, "المبلغ يجب أن يكون أكبر من 0.")
            elif wallet.balance < amount:  # Decimal comparison
                messages.error(request, "ليس لديك رصيد كافي في المحفظة.")
            else:
                # Deduct from wallet
                wallet.balance -= amount
                wallet.save()

                # Ensure total_balance is Decimal (convert if it's a float)
                selected_fund.total_balance = Decimal(selected_fund.total_balance) + amount
                selected_fund.save()

                # Update or create an InvestorFund instance
                investor_fund, created = InvestorFund.objects.get_or_create(
                    investor=request.user.investor,
                    fund=selected_fund,
                    defaults={"amount_invested": Decimal('0.0')}  # Set default value
                )
                investor_fund.amount_invested += amount  # Add the amount
                investor_fund.save()

                # Log the transaction
                Transactions.objects.create(
                    wallet=wallet,
                    fund=selected_fund,
                    transaction_type="Transfer",
                    amount=amount,
                    description=description or f"Transfer to {selected_fund.name}",
                    created_at=timezone.now()
                )

                # Success message
                messages.success(request, f"تم تحويل {amount} ريال إلى الصندوق: {selected_fund.name}.")
                return redirect('main:investor_dashboard_view')
        
        except ValueError:
            messages.error(request, "الرجاء إدخال مبلغ صالح.")
    
    return render(request, 'main/investor_dashboard.html', {"joined_funds": joined_funds, "fund": fund})


from decimal import Decimal
@login_required
def withdraw_profit(request):
    # Fetch the wallet for the logged-in user
    wallet = Wallet.objects.get(user=request.user)

    # Fetch the joined investment funds
    joined_funds = InvestorFund.objects.filter(investor__user=request.user)

    # Calculate the total profit for each fund
    profit_data = []
    for investor_fund in joined_funds:
        # Fetch the related investment opportunity for each fund
        opportunity = InvestmentOpportunity.objects.filter(fund=investor_fund.fund).first()
        
        if opportunity:
            expected_return = Decimal(opportunity.expected_return)

            # Calculate the profit based on the invested amount and expected return
            investment_period_days = (opportunity.end_date - opportunity.start_date).days
            profit = (investor_fund.amount_invested * expected_return * investment_period_days) / Decimal(365) / Decimal(100)

            # Check if the opportunity status is 'Closed'
            if opportunity.status == 'Closed':
                transfer_enabled = True  # Allow the withdrawal if the status is Closed
            else:
                transfer_enabled = False  # Otherwise, disable it

            profit_data.append({
                "fund_name": investor_fund.fund.name,
                "amount_invested": investor_fund.amount_invested,
                "profit": round(profit, 2),
                "status": opportunity.status,  # Only access status if opportunity exists
                "fund_id": investor_fund.fund.id,
                "transfer_enabled": transfer_enabled  # Pass the flag for button activation
            })
        else:
            # If no opportunity is found, set status to None or other default value
            profit_data.append({
                "fund_name": investor_fund.fund.name,
                "amount_invested": investor_fund.amount_invested,
                "profit": 0.0,
                "status": 'No Opportunity',  # Default status when no opportunity exists
                "fund_id": investor_fund.fund.id,
                "transfer_enabled": False  # Disable the button if no opportunity exists
            })

    # Handle withdrawal request (POST)
    if request.method == 'POST':
        fund_id = request.POST.get('fund_id')  # Get the selected fund ID for profit withdrawal
        if not fund_id:  # Check if fund_id is missing
            messages.error(request, "مفقود معرف الصندوق.")
            return redirect('main:investor_dashboard_view')

        try:
            profit_to_withdraw = Decimal(request.POST.get('profit', '0'))  # Amount of profit to withdraw
        except ValueError:
            messages.error(request, "الرجاء إدخال مبلغ صالح.")
            return redirect('main:investor_dashboard_view')

        # Get the selected fund for the withdrawal
        selected_fund = get_object_or_404(InvestmentFund, id=fund_id)

        # Ensure the profit is valid
        if profit_to_withdraw <= 0:
            messages.error(request, "المبلغ يجب أن يكون أكبر من 0.")
        elif profit_to_withdraw > wallet.profit_balance:
            messages.error(request, "ليس لديك رصيد كافي من الأرباح للسحب.")
        else:
            # Determine the action (withdraw to wallet or reinvest in fund)
            action = request.POST.get('action', 'withdraw_to_wallet')  # Default is 'withdraw_to_wallet'

            # Perform the action
            if action == 'withdraw_to_wallet':
                # Add the profit to the wallet balance
                wallet.balance += profit_to_withdraw
                wallet.profit_balance -= profit_to_withdraw  # Deduct from profit_balance
                wallet.save()

                # Log the transaction
                Transactions.objects.create(
                    wallet=wallet,
                    transaction_type="Profit Withdrawal",
                    amount=profit_to_withdraw,
                    description=f"Profit Withdrawal from {selected_fund.name}",
                    created_at=timezone.now(),
                    fund=selected_fund
                )
                messages.success(request, f"تم سحب {profit_to_withdraw} ريال من الأرباح إلى محفظتك.")
            elif action == 'reinvest_in_fund':
                # Reinvest the profit into the selected fund
                selected_fund.total_balance += profit_to_withdraw
                selected_fund.save()

                # Update the InvestorFund record
                investor_fund = InvestorFund.objects.get(investor__user=request.user, fund=selected_fund)
                investor_fund.amount_invested += profit_to_withdraw
                investor_fund.save()

                # Log the transaction
                Transactions.objects.create(
                    wallet=wallet,
                    fund=selected_fund,
                    transaction_type="Reinvestment",
                    amount=profit_to_withdraw,
                    description=f"Reinvestment into {selected_fund.name}",
                    created_at=timezone.now()
                )
                messages.success(request, f"تم إعادة استثمار {profit_to_withdraw} ريال في صندوق {selected_fund.name}.")

        return redirect('main:investor_dashboard_view')

    return render(request, 'dashboard/investor_dashboard.html', {
        "wallet": wallet,
        "joined_funds": joined_funds,
        "profit_data": profit_data  # Pass the calculated profit data
    })

#-------------------------------------------------- Profit Calculate

@login_required
def investor_profit_view(request):
    # Fetch all funds the investor has invested in
    investor_funds = InvestorFund.objects.filter(investor__user=request.user)

    # Prepare data with calculated profits
    profit_data = []
    for investor_fund in investor_funds:
        profit = investor_fund.calculate_profit()
        profit_data.append({
            "fund_name": investor_fund.fund.name,
            "amount_invested": investor_fund.amount_invested,
            "profit": profit,
            "status": investor_fund.status,
        })

    context = {
        "profit_data": profit_data,
    }
    return render(request, "dashboard/investor_dashboard.html", context)
