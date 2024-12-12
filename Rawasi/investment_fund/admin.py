from django.contrib import admin
from .models import InvestmentFund, Wallet, Transactions


@admin.register(InvestmentFund)
class InvestmentFundAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'total_balance','category' ,'status', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'leader__username', 'status')
    list_filter = ('status', 'is_active','category','created_at')
    ordering = ('-created_at',)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('last_updated', 'created_at')
    ordering = ('-last_updated',)


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'fund', 'wallet', 'amount', 'created_at', 'updated_at')
    search_fields = ('transaction_type', 'fund__name', 'wallet__user__username')
    list_filter = ('transaction_type', 'created_at')
    ordering = ('-created_at',)
