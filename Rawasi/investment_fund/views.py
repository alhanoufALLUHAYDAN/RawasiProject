from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import InvestmentFund
from .forms import InvestmentFundForm  
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def create_investment_fund(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        total_balance = request.POST.get("total_balance")
        is_active = request.POST.get("is_active") == "True"  # Convert string to boolean
        category = request.POST.get("category")

        # Check if the leader already has an investment fund
        if hasattr(request.user, 'leader') and hasattr(request.user.leader, 'managed_fund'):
            messages.error(request, "لا يمكنك إنشاء أكثر من صندوق استثماري.")
            return redirect("main:fund_dashboard_view")

        # Validate the inputs
        if not all([name, description, total_balance, category]):
            messages.error(request, "الرجاء ملء جميع الحقول المطلوبة.")
            return redirect("main:fund_dashboard_view")

        # Create the investment fund
        try:
            InvestmentFund.objects.create(
                name=name,
                description=description,
                total_balance=total_balance,
                is_active=is_active,
                category=category,
                leader=request.user.leader  # Link the fund to the current leader
            )
            messages.success(request, "تم إنشاء الصندوق الاستثماري بنجاح!")
        except Exception as e:
            messages.error(request, f"حدث خطأ: {e}")
        
        return redirect("main:fund_dashboard_view")
    else:
        return redirect("main:fund_dashboard_view")



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
            messages.success(request, f'Investment fund "{fund.name}" has been updated successfully.')
            return redirect('main:fund_dashboard_view')  # Redirect to the dashboard
        else:
            print("Form errors:", form.errors)  # Debug form errors
            messages.error(request, "There was an error updating the investment fund. Please correct the errors below.")
    else:
        form = InvestmentFundForm(instance=fund)  # Handle GET request and populate the form
    return render(request, 'investment_fund/update.html', {'form': form, 'fund': fund})


def delete_investment_fund(request, pk):
    fund = get_object_or_404(InvestmentFund, pk=pk)
    if request.method == "POST":
        fund.delete()
        messages.success(request, "تم حذف الصندوق بنجاح.")
        return redirect('main:fund_dashboard_view')
    return redirect('main:fund_dashboard_view')