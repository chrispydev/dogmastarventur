from django.contrib.auth import views
from django.urls import path
from auth.views import RegisterForm, CustomPasswordResetDoneView, AdminDashboardView, CustomLogoutView, AddCustomerView, CustomerListView, CustomerDetailView, CustomerAdminDetailView, CustomerAdminListView, AdminRegisterView, CustomAdminLoginView, AllCollectionsView, CollectionDetailView, CustomerLoginView, CustomerDashboardView, SuperAdminRegisterView

urlpatterns = [
    path('customer/login/', CustomerLoginView.as_view(), name='customer_login'),
    path('customer/dashboard/', CustomerDashboardView.as_view(),
         name='customer_dashboard'),
    path('login/', CustomAdminLoginView.as_view(), name='login'),
    path('admin-register/', AdminRegisterView.as_view(), name='admin_register'),
    path('super-admin-register/',
         SuperAdminRegisterView.as_view(), name='super_admin_register'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-customers/', CustomerAdminListView.as_view(),
         name='admin_customer_list'),
    path('collections/', AllCollectionsView.as_view(), name='all_collections'),
    path('collections/<int:pk>/', CollectionDetailView.as_view(),
         name='collection_detail'),
    path('admin-customers/<int:pk>/', CustomerAdminDetailView.as_view(),
         name='admin_customer_detail'),
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('add-customer/', AddCustomerView.as_view(), name='add_customer'),
    path('register/', RegisterForm.as_view(), name='register'),
    # path("login/", views.LoginView.as_view(
    #     template_name="auth/login.html"), name="login"),
    # path('logout/', views.LogoutView.as_view(
    #     template_name='auth/logout.html', next_page='/'), name='logout'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-reset/', CustomPasswordResetDoneView.as_view(
         template_name='auth/password_reset.html'), name='password_reset'),
    # path('password-reset/', views.PasswordResetView.as_view(
    #      template_name='auth/password_reset.html'), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>', views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-complete/', views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'), name='password_reset_complete'),

]
