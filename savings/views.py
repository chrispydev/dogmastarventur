from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from savings.models import Customer, Worker, Collection, CompanyAccount, Deduction
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from django.utils.timezone import now
from django.contrib import messages
from savings.forms import CollectionForm
from django.db.models import Sum, Q
from django.views.generic import FormView
from django.urls import reverse_lazy
from savings.forms import DeductionForm


class WorkerDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'customers': [],
            'total_customers': 0,
            'total_collections_today': 0,
            'total_weekly_collections': 0,
            'pending_customers': [],
            'recent_transactions': [],
            # 'search_query': '',
        }

        try:
            # Fetch the logged-in worker
            worker = Worker.objects.get(user=request.user)

            # Fetch customers the worker has collected from
            customers = Customer.objects.filter(
                collection__worker=worker
            ).distinct()

            total_customers = customers.count()

            # Calculate total collections for today
            total_collections_today = Collection.objects.filter(
                worker=worker, date__date=now().date()
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            # Calculate total weekly collections
            start_of_week = now().date() - timedelta(days=now().weekday())
            total_weekly_collections = Collection.objects.filter(
                worker=worker, date__gte=start_of_week
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

            # Identify pending customers (no collection in the past 7 days)
            one_week_ago = now().date() - timedelta(days=7)
            pending_customers = customers.exclude(
                id__in=Collection.objects.filter(
                    worker=worker, date__gte=one_week_ago
                ).values_list('customer_id', flat=True)
            )

            recent_transactions = Collection.objects.filter(
                worker=worker
            ).order_by('-date')[:2]  # Fetch the last 5 collections

            # # Search functionality for customer collections
            # search_query = request.GET.get('search', '')
            # if search_query:
            #     collections = Collection.objects.filter(
            #         Q(customer__name__icontains=search_query) |
            #         Q(customer__next_of_kin__icontains=search_query) |
            #         Q(amount__icontains=search_query)
            #     )
            # else:
            #     collections = Collection.objects.filter(worker=worker)

            # # Pagination
            # # Show 5 collections per page
            # paginator = Paginator(collections, 2)
            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)

            # Update context with dashboard data
            context.update({
                'customers': customers[:10],
                'total_customers': total_customers,
                'total_collections_today': total_collections_today,
                'total_weekly_collections': total_weekly_collections,
                'pending_customers': pending_customers,
                'recent_transactions': recent_transactions,
                # 'search_query': search_query,
                # 'page_obj': page_obj,  # For pagination
            })

        except Worker.DoesNotExist:
            context['error_message'] = "You are not assigned as a worker in the system."

        return render(request, 'savings/worker_dashboard.html', context)


class AddCollectionView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Ensure the logged-in user is a worker
            worker = Worker.objects.get(user=request.user)
            form = CollectionForm()
            return render(request, 'savings/add_collection.html', {'form': form})
        except Worker.DoesNotExist:
            messages.error(
                request, "You are not authorized to take collections.")
            # Adjust redirect URL as needed
            return redirect('worker_dashboard')

    def post(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            form = CollectionForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.worker = worker  # Assign the logged-in worker
                collection.save()
                messages.success(request, "Collection recorded successfully!")
                # Adjust redirect URL as needed
                return redirect('worker_dashboard')
            return render(request, 'savings/add_collection.html', {'form': form})
        except Worker.DoesNotExist:
            messages.error(
                request, "You are not authorized to take collections.")
            # Adjust redirect URL as needed
            return redirect('worker_dashboard')


class WeeklyCollectionsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'week_collections': [],
            'search_query': '',
            'page_obj': None
        }

        try:
            # Fetch the logged-in worker
            worker = Worker.objects.get(user=request.user)

            # Search for a specific week or customer
            search_query = request.GET.get('search', '')
            if search_query:
                collections = Collection.objects.filter(
                    Q(customer__name__icontains=search_query) |
                    Q(customer__next_of_kin__icontains=search_query) |
                    Q(amount__icontains=search_query),
                    worker=worker
                )
            else:
                collections = Collection.objects.filter(worker=worker)

            # Group collections by week and year
            collections_by_week = {}
            for collection in collections:
                start_of_week = collection.date - \
                    timedelta(days=collection.date.weekday())
                # Year-Week format (e.g. 2024-50)
                week_key = start_of_week.strftime('%Y-%U')

                if week_key not in collections_by_week:
                    collections_by_week[week_key] = {
                        'collections': [],
                        'total': 0
                    }
                collections_by_week[week_key]['collections'].append(collection)
                collections_by_week[week_key]['total'] += collection.amount

            # Convert to a list for pagination
            paginator = Paginator(list(collections_by_week.items()), 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # Update context with data
            context.update({
                'search_query': search_query,
                'week_collections': page_obj,
                'page_obj': page_obj
            })

        except Worker.DoesNotExist:
            context['error_message'] = "You are not assigned as a worker in the system."

        return render(request, 'savings/weekly_collections.html', context)


class WeeklyCollectionDetailView(LoginRequiredMixin, View):
    def get(self, request, week, *args, **kwargs):
        context = {
            'collections': [],
            'week': week,
            'page_obj': None,
        }

        try:
            # Fetch the logged-in worker
            worker = Worker.objects.get(user=request.user)

            # Fetch collections for the specific week
            # Get start of the week (Monday)
            start_of_week = datetime.strptime(week + "-1", "%Y-%U-%w")
            end_of_week = start_of_week + \
                timedelta(days=6)  # End of the week (Sunday)

            collections = Collection.objects.filter(
                worker=worker,
                date__gte=start_of_week,
                date__lte=end_of_week
            )

            # Paginate the collections for that week
            paginator = Paginator(collections, 5)  # 5 collections per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # Update context with data
            context.update({
                'collections': collections,
                'week': week,
                'page_obj': page_obj
            })

        except Worker.DoesNotExist:
            context['error_message'] = "You are not assigned as a worker in the system."

        return render(request, 'savings/weekly_collection_detail.html', context)


class RecordCollectionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            worker = Worker.objects.get(user=request.user)
            customers = worker.assigned_customers.all()
        except Worker.DoesNotExist:
            worker = None
            customers = []
        return render(request, 'savings/record_collection.html', {'customers': customers})

    def post(self, request, *args, **kwargs):
        customer_id = request.POST.get('customer_id')
        amount = request.POST.get('amount')
        customer = Customer.objects.get(id=customer_id)
        worker = Worker.objects.get(user=request.user)
        Collection.objects.create(
            worker=worker, customer=customer, amount=amount)
        return redirect('dashboard')


class DeductBalanceView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "savings/deduct_balance.html"
    form_class = DeductionForm
    success_url = reverse_lazy('deduct_balance')

    def test_func(self):
        return self.request.user.is_superuser  # Ensure only admin can access this

    def form_valid(self, form):
        deduction_type = form.cleaned_data['deduction_type']
        amount = form.cleaned_data['amount']
        admin = self.request.user

        if deduction_type == 'customer':
            customer = form.cleaned_data['customer']
            if customer and customer.balance >= amount:
                customer.balance -= amount
                customer.save()

                Deduction.objects.create(
                    admin=admin,
                    deduction_type='customer',
                    customer=customer,
                    amount=amount
                )

                messages.success(
                    self.request, f"${amount} deducted from {customer.name}.")
            else:
                messages.error(
                    self.request, "Insufficient balance in customer's account.")

        elif deduction_type == 'company':
            company_account, _ = CompanyAccount.objects.get_or_create()
            if company_account.balance >= amount:
                company_account.balance -= amount
                company_account.save()

                Deduction.objects.create(
                    admin=admin,
                    deduction_type='company',
                    amount=amount
                )

                messages.success(
                    self.request, f"${amount} deducted from the company account.")
            else:
                messages.error(
                    self.request, "Insufficient balance in the company account.")

        return super().form_valid(form)
