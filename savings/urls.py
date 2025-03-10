from django.urls import path
from savings.views import WorkerDashboardView, AddCollectionView, WeeklyCollectionDetailView, WeeklyCollectionsView, DeductBalanceView

urlpatterns = [
    path('', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('add-collection/', AddCollectionView.as_view(), name='add_collection'),
    path('weekly-collections/', WeeklyCollectionsView.as_view(),
         name='weekly_collections'),
    path('weekly-collection/<str:week>/',
         WeeklyCollectionDetailView.as_view(), name='weekly_collection_detail'),
    path('dashboard/deduct/', DeductBalanceView.as_view(), name='deduct_balance'),
]
