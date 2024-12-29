from auth.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from savings.models import Customer, Worker, Collection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from auth.forms import CustomerForm
from django.db.models import Sum, Count


class RegisterForm(View):
    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            Worker.objects.create(user=user)
            login(request, user)
            return redirect('worker_dashboard')
        else:
            user_form = UserRegisterForm()  # Create a new form instance
            template_name = 'auth/register.html'
            return render(request, template_name, {'user_form': user_form, 'form': form})

    def get(self, request):
        user_form = UserRegisterForm()
        template_name = 'auth/register.html'
        return render(request, template_name, {'user_form': user_form})


class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')


class CustomPasswordResetDoneView(PasswordResetView):
    template_name = 'auth/password_reset.html'

    def form_valid(self, form):
        # Check if the email address is registered
        email = form.cleaned_data.get('email')
        # Replace User with your User model
        user = User.objects.filter(email=email).first()

        if user is None:
            # Display an alert or flash message
            messages.warning(
                self.request, 'The provided email address is not registered.')
            return redirect('password_reset')

        return super().form_valid(form)


class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, '403.html')  # Redirect non-admin users

        # Aggregate data for dashboard
        total_customers = Customer.objects.count()
        total_workers = Worker.objects.count()
        total_savings = sum(
            customer.balance for customer in Customer.objects.all())
        recent_collections = Collection.objects.order_by('-date')[:10]

        context = {
            'total_customers': total_customers,
            'total_workers': total_workers,
            'total_savings': total_savings,
            'recent_collections': recent_collections,
        }
        return render(request, 'admin_panel/dashboard.html', context)


class AddCustomerView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerForm()
        return render(request, 'auth/add_customer.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully!")
            # Update with your redirect URL
            return redirect('worker_dashboard')
        return render(request, 'auth/add_customer.html', {'form': form})


class CustomerListView(ListView):
    model = Customer
    template_name = 'auth/customer_list.html'
    context_object_name = 'customers'

    def get_queryset(self):
        # Get the logged-in worker
        worker = get_object_or_404(Worker, user=self.request.user)
        # Retrieve customers the worker has taken collections from
        customer_ids = Collection.objects.filter(
            worker=worker).values_list('customer_id', flat=True)
        return Customer.objects.filter(id__in=customer_ids).distinct()


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'auth/customer_detail.html'
    context_object_name = 'customer'

    def get_queryset(self):
        # Get the logged-in worker
        worker = get_object_or_404(Worker, user=self.request.user)
        # Retrieve customers the worker has taken collections from
        customer_ids = Collection.objects.filter(
            worker=worker).values_list('customer_id', flat=True)
        return Customer.objects.filter(id__in=customer_ids).distinct()


class AdminDashboardView(View):
    def get(self, request, *args, **kwargs):
        # Total statistics
        total_customers = Customer.objects.count()
        total_workers = Worker.objects.count()
        total_collections = Collection.objects.aggregate(
            total_amount=Sum('amount'))['total_amount'] or 0
        total_pending_customers = Customer.objects.filter(
            collection__isnull=True
        ).count()

        # Weekly collections
        from datetime import timedelta
        from django.utils.timezone import now

        one_week_ago = now() - timedelta(days=7)
        weekly_collections = Collection.objects.filter(date__gte=one_week_ago)
        total_weekly_collections = weekly_collections.aggregate(
            total_amount=Sum('amount'))['total_amount'] or 0

        # Recent collections
        recent_collections = Collection.objects.order_by('-date')[:5]

        # Pass data to the context
        context = {
            'total_customers': total_customers,
            'total_workers': total_workers,
            'total_collections': total_collections,
            'total_pending_customers': total_pending_customers,
            'total_weekly_collections': total_weekly_collections,
            'recent_collections': recent_collections,
        }
        return render(request, 'auth/admin_dashboard.html', context)


class CustomerAdminListView(ListView):
    model = Customer
    template_name = 'auth/customer_list.html'
    context_object_name = 'customers'


class CustomerAdminDetailView(DetailView):
    model = Customer
    template_name = 'auth/customer_detail.html'
    context_object_name = 'customer'
