from django.urls import path
from .api_views.ListTransactions import list_transactions
from .api_views.PostTransaction import post_transaction
# from .api_views.ViewTransactions import view_transactions
from .api_views.UpdateTransactionStatus import update_transaction
from .api_views.SearchForTransaction import search_for_transaction
from .api_views.CallBack import callback_receiver
from .api_views.Report import report


urlpatterns = [
    path('list/', list_transactions, name="list-transactions"),
    path('submit/', post_transaction, name="submit-transaction"),
    path('report/', report, name="report"),
    # path('view/', view_transactions, name="view-transactions"),
    path('update/<str:reference_type>/<str:transaction_id>/', update_transaction, name="update-transaction"),
    path('search/<str:reference_type>/<str:transaction_id>/', search_for_transaction, name="search-for-transaction"),
    path('callback/', callback_receiver, name="callback")
]
