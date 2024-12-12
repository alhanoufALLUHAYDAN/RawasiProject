from django.apps import AppConfig

class InvestmentFundConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investment_fund'

    # def ready(self):
    #     import investment_fund.signals  # Import the signals to connect them
