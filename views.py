from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *


def index(request):
    return render(request, 'index.html')

def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            if not user.is_active:
                messages.error(request,"Account blocked by admin")
                return redirect('login')

            login(request,user)

            if user.is_staff:
                return redirect('admin_dashboard')

            elif user.user_type == "Student":
                return redirect('student_home')

            elif user.user_type == "Alumni":
                return redirect('alumni_home')

        else:
            messages.error(request,"Invalid username or password")

    return render(request,'login.html')


def register_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user_type = request.POST.get('user_type')

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        department = request.POST.get('department')
        course = request.POST.get('course')

        year_from = request.POST.get('year_from')
        year_to = request.POST.get('year_to')

        if password != confirm_password:
            messages.error(request,"Passwords do not match")
            return render(request,'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already exists")
            return render(request,'register.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            department=department,
            course=course,
            year_of_study_from=year_from,
            year_of_study_to=year_to
        )

        messages.success(request,"Registration successful. Please login.")

        return redirect('login')

    return render(request,'register.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def student_home(request):
    user = request.user
    return render(request, 'student_home.html', {'user': user})

def alumni_home(request):
    return render(request, 'alumni_home.html')

def student_profile(request):
    return render(request, 'student_profile.html')

@login_required
def student_update_profile(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.year_of_study_from = request.POST.get('study_from')
        user.year_of_study_to = request.POST.get('study_to')
        user.course = request.POST.get('course')
        user.department = request.POST.get('department')
        user.save()

        return redirect('student_profile')

    return render(request, 'update_profile.html')


@login_required
def alumni_profile_view(request):
    return render(request, 'alumni_profile.html')


@login_required
def alumni_update_profile_view(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.year_of_study_from = request.POST.get('study_from')
        user.year_of_study_to = request.POST.get('study_to')
        user.course = request.POST.get('course')
        user.department = request.POST.get('department')
        user.save()

        return redirect('alumni_profile')

    return render(request, 'alumni_update_profile.html')


@login_required
def alumni_products(request):
    products = Product.objects.filter(seller=request.user, status__in=['Sell', 'Sell/Lease', 'Lease'])
    return render(request, 'alumni_products.html', {'products': products})


@login_required
def add_product_view(request):

    if request.method == "POST":

        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        price = request.POST.get('price')

        # IMPORTANT FIX
        if status == "Lease":
            price = 0   # no selling price for lease
        else:
            price = int(price) if price else 0

        Product.objects.create(
            seller=request.user,
            name=name,
            description=description,
            price=price,
            category=category,
            status=status,
            image=image
        )

        return redirect('alumni_products')

    return render(request, 'add_product.html')


def search_products_view(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query),
            status__in=['Sell', 'Sell/Lease', 'Lease']
        )

    return render(request, 'search_products.html', {
        'query': query,
        'results': results
    })

@csrf_exempt
def request_lease(request, product_id):
    if request.method == "POST":
        product = Product.objects.get(id=product_id)
        return JsonResponse({"status": "requested"})
    

@login_required
def wallet_view(request):

    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = Payment.objects.filter(
        Q(buyer=request.user) | Q(receiver=request.user)
    ).order_by('-paid_at')

    return render(request, 'wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })


@login_required
def wallet_topup(request):

    if request.method == "POST":

        amount = float(request.POST.get('amount'))

        wallet, created = Wallet.objects.get_or_create(user=request.user)

        # Update balance
        wallet.balance += amount

        # Store last top-up info
        wallet.topup_amount = amount
        wallet.created_at = datetime.now()

        wallet.save()

        return redirect('wallet')

    return redirect('wallet')

@login_required
def bargain_request(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # Only students allowed
    if request.user.user_type != "Student":
        messages.error(request, "Only students can bargain.")
        return redirect('student_home')

    min_price = int(product.price * 0.7)

    if request.method == "POST":

        student_price = int(request.POST.get('price'))

        # Validation
        if student_price < min_price:
            messages.error(request, f"Minimum bargain price is ₹{min_price}")
            return redirect('bargain_request', product_id=product.id)

        # Create bargain request
        Bargain.objects.create(
            student=request.user,
            alumni=product.seller,
            product=product,
            student_price=student_price,
            status='pending'
        )

        messages.success(request, "Bargain request sent to alumni!")
        return redirect('student_home')

    return render(request, 'bargain_request.html', {
        'product': product,
        'min_price': min_price
    })

@login_required
def product_requests(request, product_id):

    product = get_object_or_404(Product, id=product_id, seller=request.user)

    buy_requests = None
    lease_requests = None
    bargain_requests = None

    if product.status == "Sell":
        buy_requests = Payment.objects.filter(product=product)
        bargain_requests = Bargain.objects.filter(product=product)

    elif product.status == "Lease":
        lease_requests = LeaseRequest.objects.filter(product=product, status="pending")

    elif product.status == "Sell/Lease":
        buy_requests = Payment.objects.filter(product=product)
        lease_requests = LeaseRequest.objects.filter(product=product, status="pending")
        bargain_requests = Bargain.objects.filter(product=product)

    return render(request, 'product_requests.html', {
        'product': product,
        'buy_requests': buy_requests,
        'lease_requests': lease_requests,
        'bargain_requests': bargain_requests
    })


@login_required
def buy_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    BuyOrder.objects.create(
        student=request.user,
        alumni=product.seller,
        product=product,
        price=product.price,
        status='pending'
    )

    messages.success(request, "Buy request sent to alumni")
    return redirect('student_home')



@login_required
def approve_buy(request, id):

    order = get_object_or_404(BuyOrder, id=id, alumni=request.user)

    if order.status != "pending":
        messages.warning(request, "Already processed")
        return redirect('product_requests', order.product.id)

    student_wallet = get_object_or_404(Wallet, user=order.student)
    alumni_wallet = get_object_or_404(Wallet, user=order.alumni)

    # check balance
    if student_wallet.balance < order.price:
        messages.error(request, "Student has insufficient balance")
        order.status = "rejected"
        order.save()
        return redirect('product_requests', order.product.id)

    # transfer money
    student_wallet.balance -= order.price
    alumni_wallet.balance += order.price

    student_wallet.save()
    alumni_wallet.save()

    # record payment
    Payment.objects.create(
        user=order.student,
        product=order.product,
        amount=order.price,
        status="paid"
    )

    # update order
    order.status = "approved"
    order.approved_at = timezone.now()
    order.save()

    # mark product sold
    product = order.product
    product.status = "sold"
    product.save()

    messages.success(request, "Purchase completed successfully")
    return redirect('product_requests', product.id)


@login_required
def reject_buy(request, id):

    order = get_object_or_404(BuyOrder, id=id, alumni=request.user)

    order.status = "rejected"
    order.save()

    messages.info(request, "Buy request rejected")
    return redirect('product_requests', order.product.id)


@login_required
def approve_lease(request, id):

    lease = get_object_or_404(LeaseRequest, id=id, alumni=request.user)

    lease.status = "approved"
    lease.rent = 10
    lease.save()
    Product.objects.filter(id=lease.product.id).update(status="leased")

    messages.success(request, "Lease approved")
    return redirect('product_requests', lease.product.id)


@login_required
def reject_lease(request, id):

    lease = get_object_or_404(LeaseRequest, id=id, alumni=request.user)

    lease.status = "rejected"
    lease.save()

    messages.info(request, "Lease rejected")
    return redirect('product_requests', lease.product.id)


@login_required
def accept_bargain(request, id):

    bargain = get_object_or_404(Bargain, id=id, alumni=request.user)

    final_price = bargain.student_price

    student_wallet = Wallet.objects.get(user=bargain.student)
    alumni_wallet = Wallet.objects.get(user=bargain.alumni)

    # Check student balance
    if student_wallet.balance < final_price:
        bargain.status = "rejected"
        bargain.save()

        messages.error(request, "Student has insufficient balance")
        return redirect('product_requests', bargain.product.id)

    # Deduct from student wallet
    student_wallet.balance -= final_price
    student_wallet.spent_amount += final_price
    student_wallet.save()

    # Add to alumni wallet
    alumni_wallet.balance += final_price
    alumni_wallet.save()

    # Create payment record
    Payment.objects.create(
        buyer=bargain.student,
        receiver=bargain.alumni,
        product=bargain.product,
        amount=final_price,
        status="Paid",
        type="Buy"
    )

    # Create BuyOrder
    BuyOrder.objects.create(
        student=bargain.student,
        alumni=bargain.alumni,
        product=bargain.product,
        price=final_price,
        status="approved",
        approved_at=timezone.now()
    )

    # Update bargain
    bargain.final_price = final_price
    bargain.status = "accepted"
    bargain.save()

    # Mark product sold
    product = bargain.product
    product.status = "sold"
    product.save()

    messages.success(request, "Bargain accepted and purchase completed")

    return redirect('product_requests', product.id)


@login_required
def reject_bargain(request, id):

    bargain = get_object_or_404(Bargain, id=id, alumni=request.user)

    bargain.status = "rejected"
    bargain.save()

    messages.info(request, "Bargain rejected")
    return redirect('product_requests', bargain.product.id)


@login_required
def counter_bargain(request, id):

    bargain = get_object_or_404(Bargain, id=id, alumni=request.user)

    if request.method == "POST":
        new_price = int(request.POST.get('price'))

        bargain.alumni_price = new_price
        bargain.status = "countered"
        bargain.save()

        messages.success(request, "Counter offer sent")
        return redirect('product_requests', bargain.product.id)

    return render(request, 'counter_bargain.html', {'bargain': bargain})


@login_required
def counter_bargain(request, id):
    bargain = get_object_or_404(Bargain, id=id, alumni=request.user)

    if request.method == "POST":
        price = int(request.POST['counter_price'])

        bargain.alumni_price = price
        bargain.status = "counter"
        bargain.save()

        return redirect('product_requests', product_id=bargain.product.id)

    return render(request, 'counter_bargain.html', {'bargain': bargain})

@login_required
def bargain_history(request, id):

    bargain = get_object_or_404(Bargain, id=id, student=request.user)

    if request.method == "POST":
        price = int(request.POST['student_counter'])
        bargain.student_price = price
        bargain.status = "pending"
        bargain.save()
        return redirect('bargain_history', id=id)

    return render(request, 'bargain_history.html', {'bargain': bargain})


@login_required
def my_bargains(request):

    bargains = Bargain.objects.filter(student=request.user).order_by('-updated_at')

    return render(request, 'my_bargains.html', {'bargains': bargains})


@login_required
def alumni_wallet(request):

    wallet, created = Wallet.objects.get_or_create(user=request.user)

    # payments received by this alumni
    payments = Payment.objects.filter(
        receiver=request.user
    ).order_by('-paid_at')

    total_received = payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(request, 'alumni_wallet.html', {
        'wallet': wallet,
        'payments': payments,
        'total_received': total_received
    })

@login_required
def alumni_wallet_topup(request):

    if request.method == "POST":
        amount = float(request.POST.get('amount'))

        wallet, created = Wallet.objects.get_or_create(user=request.user)

        wallet.balance += amount
        wallet.opup_amount = amount
        wallet.created_at = datetime.now()
        wallet.save()

        return redirect('alumni_wallet')

    return redirect('alumni_wallet')


@login_required
def my_purchases(request):

    orders = BuyOrder.objects.filter(student=request.user).order_by('-approved_at')

    return render(request, 'my_purchases.html', {'orders': orders})


@login_required
def request_lease(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # prevent leasing own product
    if product.seller == request.user:
        messages.error(request, "You cannot lease your own product")
        return redirect('search_products')

    # prevent duplicate request
    exists = LeaseRequest.objects.filter(
        student=request.user,
        product=product,
        status="pending"
    ).exists()

    if exists:
        messages.warning(request, "You already requested this product")
        return redirect('search_products')

    # create lease request
    LeaseRequest.objects.create(
        student=request.user,
        alumni=product.seller,
        product=product
    )

    messages.success(request, "Lease request sent to alumni")

    return redirect('student_home')

@login_required
def alumni_lease_requests(request):

    # all lease requests for this alumni
    requests = LeaseRequest.objects.filter(alumni=request.user).select_related('product','student').order_by('-requested_at')

    # group by product
    product_requests = {}
    for r in requests:
        product_requests.setdefault(r.product, []).append(r)

    return render(request, 'alumni_lease_requests.html', {
        'product_requests': product_requests
    })

@login_required
def approve_lease(request, id):

    lease = get_object_or_404(LeaseRequest, id=id, alumni=request.user)

    # update lease
    lease.approved_at = timezone.now()
    lease.rent = 10
    lease.status = "approved"
    lease.save()

    # update product status
    product = lease.product

    product.previous_status = product.status
    product.status = "leased"

    product.save()

    return redirect('alumni_lease_requests')


@login_required
def reject_lease(request, id):

    lease = get_object_or_404(LeaseRequest, id=id, alumni=request.user)

    lease.status = "rejected"
    lease.save()

    return redirect('alumni_lease_requests')


@login_required
def my_leases(request):

    leases = LeaseRequest.objects.filter(student=request.user).order_by('-requested_at')

    lease_data = []

    for lease in leases:

        rent_days = 0
        rent_amount = lease.rent   # default stored rent

        if lease.status == "approved" and lease.approved_at:

            approved_time = lease.approved_at

            if timezone.is_naive(approved_time):
                approved_time = timezone.make_aware(approved_time, timezone.get_current_timezone())

            difference = timezone.now() - approved_time
            rent_days = int(difference.total_seconds() // (24 * 60 * 60))
            rent_amount = rent_days * 10

            # update live rent
            lease.rent = rent_amount
            lease.save(update_fields=['rent'])

        lease_data.append({
            'lease': lease,
            'days': rent_days,
            'rent': rent_amount
        })

    return render(request, 'my_leases.html', {'lease_data': lease_data})


@login_required
def return_product(request, lease_id):

    lease = get_object_or_404(LeaseRequest, id=lease_id, student=request.user)

    if lease.status != "approved":
        messages.error(request, "Invalid return request")
        return redirect('my_leases')

    # calculate rent
    approved_time = lease.approved_at

    if timezone.is_naive(approved_time):
        approved_time = timezone.make_aware(approved_time)

    time_difference = timezone.now() - approved_time
    rent_days = time_difference.total_seconds() // (24 * 60 * 60)

    rent_amount = int(rent_days) * 10

    # wallets
    student_wallet = Wallet.objects.get(user=request.user)
    alumni_wallet = Wallet.objects.get(user=lease.alumni)

    # check balance
    if student_wallet.balance < rent_amount:
        messages.error(request, "Insufficient balance to return product")
        return redirect('my_leases')

    # deduct from student
    student_wallet.balance -= rent_amount
    student_wallet.spent_amount += rent_amount
    student_wallet.save()

    # add to alumni
    alumni_wallet.balance += rent_amount
    alumni_wallet.save()

    # create payment record
    Payment.objects.create(
        buyer=request.user,
        receiver=lease.alumni,
        product=lease.product,
        amount=rent_amount,
        status="Paid",
        type="Lease"
    )

    # update lease
    lease.rent = rent_amount
    lease.status = "returned"
    lease.save()

    # restore product status
    product = lease.product

    product.status = product.previous_status
    product.previous_status = None
    product.save()

    messages.success(request, f"Product returned successfully. Rent paid ₹{rent_amount}")

    return redirect('my_leases')

@login_required
def alumni_sales(request):

    sales = BuyOrder.objects.filter(alumni=request.user, status="approved").order_by('-approved_at')

    return render(request, 'alumni_sales.html', {'sales': sales})

@login_required
def admin_dashboard(request):

    context = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_sales': BuyOrder.objects.filter(status='approved').count(),
        'total_leases': LeaseRequest.objects.filter(status='approved').count(),
    }

    return render(request, 'admin_dashboard.html', context)


def manage_users(request):

    users = User.objects.filter(
        user_type__in=['Student', 'Alumni']
    ).order_by('-date_joined')

    return render(request, 'admin_manage_users.html', {'users': users})


def admin_products(request):

    products = Product.objects.all().order_by('-created_at')

    return render(request, 'admin_products.html', {'products': products})

@login_required
def admin_transactions(request):

    transactions = Payment.objects.select_related(
        'buyer', 'receiver', 'product'
    ).order_by('-paid_at')

    return render(request, 'admin_transactions.html', {
        'transactions': transactions
    })


@login_required
def block_user(request, user_id):

    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()

    return redirect('manage_users')


@login_required
def unblock_user(request, user_id):

    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()

    return redirect('manage_users')

@login_required
def delete_user(request, user_id):

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")

    return redirect('manage_users')

def buy_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # Check if product already sold
    if product.status == "sold":
        messages.error(request, "This product is already sold.")
        return redirect('search_products')

    student = request.user
    alumni = product.seller
    price = product.price

    # Prevent buying own product
    if student == alumni:
        messages.error(request, "You cannot buy your own product.")
        return redirect('search_products')

    # Get wallets
    student_wallet = Wallet.objects.get(user=student)
    alumni_wallet = Wallet.objects.get(user=alumni)

    # Check wallet balance
    if student_wallet.balance < price:
        messages.error(request, "Insufficient wallet balance.")
        return redirect('wallet')

    # Deduct from student wallet
    student_wallet.balance -= price
    student_wallet.spent_amount += price
    student_wallet.save()

    # Add to alumni wallet
    alumni_wallet.balance += price
    alumni_wallet.save()

    Payment.objects.create(
        buyer=student,
        receiver=alumni,
        product=product,
        amount=price,
        status="Paid",
        type="Buy"
    )

    BuyOrder.objects.create(
        student=student,
        alumni=alumni,
        product=product,
        price=price,
        status="approved",
        approved_at=timezone.now()
    )

    product.status = "sold"
    product.save()

    messages.success(request, "Product purchased successfully!")

    return redirect('student_home')