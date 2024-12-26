from django.contrib.auth import views
from django.urls import path
from auth.views import RegisterForm, CustomPasswordResetDoneView, AdminDashboardView, CustomLogoutView, AddCustomerView, CustomerListView, CustomerDetailView

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('add-customer/', AddCustomerView.as_view(), name='add_customer'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('register/', RegisterForm.as_view(), name='register'),
    path("login/", views.LoginView.as_view(
        template_name="auth/login.html"), name="login",),
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
