from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import InvestmentFund
from .forms import InvestmentFundForm  
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

@login_required
def create_investment_fund(request):
    # Ensure the logged-in user is a Leader
    if not hasattr(request.user, 'leader'):
        return HttpResponseForbidden("You are not authorized to create an investment fund.")  # Return a 403 Forbidden response

    if request.method == "POST":
        form = InvestmentFundForm(request.POST)
        if form.is_valid():
            # Save the form without committing to assign the leader
            investment_fund = form.save(commit=False)
            investment_fund.leader = request.user.leader  # Assign the logged-in leader
            investment_fund.save()
            return redirect('investment_fund_list')  # Redirect to the list view
    else:
        form = InvestmentFundForm()

    return render(request, 'investment_fund/create.html', {'form': form})


def investment_fund_detail(request, pk):
    # Get the specific investment fund by primary key (pk)
    fund = get_object_or_404(InvestmentFund, pk=pk)
    
    # Pass the fund object to the template
    return render(request, 'investment_fund/detail.html', {'fund': fund})

def investment_fund_list(request):
    funds = InvestmentFund.objects.all()
    return render(request, 'investment_fund/list.html', {'funds': funds})


def update_investment_fund(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)
    if request.method == "POST":
        form = InvestmentFundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect('investment_fund_list')
    else:
        form = InvestmentFundForm(instance=fund)
    return render(request, 'investment_fund/update.html', {'form': form, 'fund': fund})


def delete_investment_fund(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)
    if request.method == "POST":
        fund.delete()
        return redirect('investment_fund_list')
    return render(request, 'investment_fund/delete.html', {'fund': fund})
