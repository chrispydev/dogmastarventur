import json  # ✅ Import json for safe conversion
from auth.forms import UserRegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from savings.models import Customer, Worker, Collection, Deduction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from auth.forms import CustomerForm, AdminRegisterForm, CustomerLoginForm
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.utils.timezone import now
from datetime import timedelta


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


# class AdminDashboardView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_superuser:
#             return render(request, '403.html')  # Redirect non-admin users

#         # Aggregate data for dashboard
#         total_customers = Customer.objects.count()
#         total_workers = Worker.objects.count()
#         total_savings = sum(
#             customer.balance for customer in Customer.objects.all())
#         recent_collections = Collection.objects.order_by('-date')[:10]

#         context = {
#             'total_customers': total_customers,
#             'total_workers': total_workers,
#             'total_savings': total_savings,
#             'recent_collections': recent_collections,
#         }
#         return render(request, 'admin_panel/dashboard.html', context)


class AddCustomerView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerForm()
        return render(request, 'auth/add_customer.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            worker = Worker.objects.get(user=user)
            form.save()
            customer = Customer.objects.get(name=form.data['name'])
            customer.created_by = worker
            customer.save()
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


class AllCollectionsView(View):
    """View to display all collections."""

    def get(self, request, *args, **kwargs):
        collections = Collection.objects.select_related(
            'worker', 'customer').order_by('-date')
        # Display 10 collections per page
        paginator = Paginator(collections, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'collections': collections,
            'page_obj': page_obj
        }
        return render(request, 'savings/all_collections.html', context)


class CollectionDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=pk)
        context = {
            'collection': collection
        }
        return render(request, 'savings/collection_detail.html', context)


class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Existing context
        context = {
            'total_customers': 0,
            'total_workers': 0,
            'total_collections': 0,
            'total_weekly_collections': 0,
            'total_deductions': 0,
            'total_balance': 0,
            'total_pending_customers': 0,
            'daily_collections': [],
        }

        # Fetch total collections
        total_collections = Collection.objects.aggregate(Sum('amount'))[
            'amount__sum'] or 0

        # Fetch total weekly collections
        start_of_week = now().date() - timedelta(days=now().weekday())
        total_weekly_collections = Collection.objects.filter(
            date__gte=start_of_week).aggregate(Sum('amount'))['amount__sum'] or 0

        # Fetch total deductions
        total_deductions = Deduction.objects.aggregate(Sum('amount'))[
            'amount__sum'] or 0

        # Calculate total balance
        total_balance = float(total_collections) - \
            float(total_deductions)  # ✅ Convert to float

        # Get daily collections for the last 7 days
        today = now().date()
        daily_collections = []
        for i in range(7):
            day = today - timedelta(days=6 - i)
            total_for_day = Collection.objects.filter(
                date__date=day).aggregate(Sum('amount'))['amount__sum'] or 0
            daily_collections.append(
                float(total_for_day))  # ✅ Convert to float

        # Convert to JSON-safe format
        context.update({
            'total_collections': total_collections,
            'total_weekly_collections': total_weekly_collections,
            'total_deductions': total_deductions,
            'total_balance': total_balance,
            'total_pending_customers': Customer.objects.exclude(
                id__in=Collection.objects.filter(
                    date__gte=today - timedelta(days=7)).values_list('customer_id', flat=True)
            ).count(),
            # ✅ Convert list to JSON string
            'daily_collections': json.dumps(daily_collections),
        })

        return render(request, 'auth/admin_dashboard.html', context)


class CustomerAdminListView(ListView):
    model = Customer
    template_name = 'auth/customer_admin_list.html'
    context_object_name = 'customers'
    paginate_by = 10  # Number of customers per page


class CustomerAdminDetailView(DetailView):
    model = Customer
    template_name = 'auth/customer_admin_detail.html'
    context_object_name = 'customer'


class AdminRegisterView(View):
    def get(self, request):
        admin_form = AdminRegisterForm()
        template_name = 'auth/admin_register.html'
        return render(request, template_name, {'admin_form': admin_form})

    def post(self, request):
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            admin_user = form.save(commit=False)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(form.cleaned_data['password1'])
            admin_user.save()
            messages.success(
                request, f'Admin account created for {admin_user.username}!')
            return redirect('admin_dashboard')
        else:
            admin_form = AdminRegisterForm()
            template_name = 'auth/admin_register.html'
        return render(request, template_name, {'form': form, 'admin_form': admin_form})


class CustomAdminLoginView(View):
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('worker_dashboard')
        # else:
        #     form = AuthenticationForm()
        return render(request, 'auth/login.html', {'form': form})

    def get(self, request):
        form = AuthenticationForm()
        template_name = 'auth/login.html'
        return render(request, template_name, {'form': form})


class CustomerDashboardView(View):
    template_name = 'auth/customer_dashboard.html'

    def get(self, request):
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('customer_login')

        customer = Customer.objects.get(id=customer_id)
        collections = customer.collection_set.all().order_by(
            '-date')  # Assuming the relationship exists
        return render(request, self.template_name, {
            'customer': customer,
            'collections': collections,
        })


class CustomerLoginView(View):
    template_name = 'auth/customer_login.html'

    def get(self, request):
        form = CustomerLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            # Save customer info in the session for simplicity
            request.session['customer_id'] = customer.id
            # Redirect to a customer dashboard
            return redirect('customer_dashboard')
        return render(request, self.template_name, {'form': form})
