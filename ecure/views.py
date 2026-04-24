from django.shortcuts import render, redirect, get_object_or_404
from .forms import PrescriptionForm, OrderForm
from .models import Medicine, Cart, CartItem, Order, OrderItem, Article, PrescriptionOrder
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.cache import never_cache

@never_cache
def home(request):
    return render(request, 'index.html')

@never_cache
def home(request):
    """Renders the eCure homepage with dynamic database products and articles."""
    # 1. Grab the medicines
    trending_medicines = Medicine.objects.filter(is_trending=True)[:4]

    # 2. Grab the articles
    latest_articles = Article.objects.all().order_by('-published_date')[:3]

    # 3. Send them both to the HTML page
    return render(request, 'index.html', {
        'trending_medicines': trending_medicines,
        'latest_articles': latest_articles
    })


def upload_prescription(request):
    """Handles the prescription upload form."""
    success = False

    if request.method == 'POST':
        # request.FILES is mandatory for images/PDFs!
        form = PrescriptionForm(request.POST, request.FILES)

        if form.is_valid():
            # 1. Create the object, but DON'T save it to the database yet
            prescription = form.save(commit=False)

            # 2. If the person is logged into an account, attach their User ID
            if request.user.is_authenticated:
                prescription.user = request.user

            # 3. Now permanently save it to the database and media folder!
            prescription.save()
            success = True
    else:
        form = PrescriptionForm()

    return render(request, 'upload.html', {'form': form, 'success': success})

def _cart_id(request):
    """Helper function to give guests a unique session ID."""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, medicine_id):
    """Finds the medicine and adds a specific quantity to the user's cart."""
    medicine = get_object_or_404(Medicine, id=medicine_id)

    # 1. Get the user's cart (or create one if they are new)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    # --- NEW: Check if the user asked for a specific quantity! ---
    quantity = 1 # Default to 1 (keeps your homepage links working safely)
    if request.method == 'POST':
        # Grab the number they typed in the box, or default to 1 just in case
        quantity = int(request.POST.get('quantity', 1))

    # 2. Add the medicine to the cart (or increase quantity if it's already there)
    try:
        cart_item = CartItem.objects.get(medicine=medicine, cart=cart)
        cart_item.quantity += quantity # Add their specific amount
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(medicine=medicine, cart=cart, quantity=quantity)

    # 3. Send them right back to where they clicked the button
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def cart(request):
    """Displays the user's shopping cart and calculates the total."""
    try:
        # Find the user's specific cart
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # Get all the items inside that cart
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Calculate the grand total
        total = 0
        for item in cart_items:
            total += (item.medicine.price * item.quantity)

    except Cart.DoesNotExist:
        # If they haven't added anything yet, pass empty variables
        cart_items = []
        total = 0

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


def checkout(request):
    """Handles the checkout form and converts the cart into a permanent order."""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        if not cart_items:
            return redirect('home')  # Don't let them checkout an empty cart!

        total = sum([item.medicine.price * item.quantity for item in cart_items])
    except Cart.DoesNotExist:
        return redirect('home')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 1. Save the customer details, but pause to add the total amount
            order = form.save(commit=False)
            order.total_amount = total
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            # 2. Move items from CartItem table to OrderItem table
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    medicine=item.medicine,
                    price=item.medicine.price,
                    quantity=item.quantity
                )

            # 3. Destroy the temporary cart now that the order is secured
            cart.delete()

            # 4. Send them to a success page!
            return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items, 'total': total})


def order_success(request):
    """A simple thank you page after purchase."""
    return render(request, 'success.html')


@never_cache
def register_user(request):
    """Handles new user sign-ups."""
    # THE BOUNCER: If already logged in, kick them to the home page!
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log them in after signing up
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@never_cache
def login_user(request):
    """Handles returning user logins."""
    # THE BOUNCER: If already logged in, kick them to the home page!
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Authenticate checks if the username and password match the database
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')
        else:
            error = "Invalid username or password. Please try again."
    else:
        form = AuthenticationForm()
        # Add our CSS class to the login form boxes
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-input'

    return render(request, 'login.html', {'form': form, 'error': error})

@never_cache
def logout_user(request):
    """Logs the user out and sends them to the homepage."""
    logout(request)
    return redirect('home')

@never_cache
@login_required(login_url='login')
def my_orders(request):
    """Displays a history of the user's past orders."""
    # Go to the database, find orders matching this user, and sort by newest first
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


def search(request):
    """Handles the search bar queries and checks if items are in the cart."""
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search the database for the medicines
        results = Medicine.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query) | Q(brand__icontains=query)
        )

        # --- NEW LOGIC: Check if these items are already in the cart! ---
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)

            # Create a cheat-sheet matching medicine IDs to their CartItems
            cart_dict = {item.medicine.id: item for item in cart_items}

            # Loop through the search results and attach the cart data if it exists
            for medicine in results:
                if medicine.id in cart_dict:
                    medicine.in_cart = True
                    medicine.cart_item_id = cart_dict[medicine.id].id
                    medicine.cart_quantity = cart_dict[medicine.id].quantity
                else:
                    medicine.in_cart = False
        except Cart.DoesNotExist:
            # If they don't have a cart at all, mark everything as not in cart
            for medicine in results:
                medicine.in_cart = False

    return render(request, 'search_results.html', {'results': results, 'query': query})

def medicine_detail(request, id):
    """Displays the full details of a single medicine."""
    # This safely grabs the medicine, or shows a 404 page if it doesn't exist
    medicine = get_object_or_404(Medicine, id=id)
    return render(request, 'medicine_detail.html', {'medicine': medicine})


def category(request, category_name):
    """Displays all medicines within a specific category."""
    # We use __iexact so that 'vitamins' and 'Vitamins' both work!
    results = Medicine.objects.filter(category__iexact=category_name)

    return render(request, 'category.html', {
        'results': results,
        'category_name': category_name
    })

def article_detail(request, id):
    """Displays the full text of a single article."""
    article = get_object_or_404(Article, id=id)
    return render(request, 'article_detail.html', {'article': article})

def all_articles(request):
    """Displays every article in the database."""
    # Notice there is no [:3] here! It grabs everything.
    articles = Article.objects.all().order_by('-published_date')
    return render(request, 'articles.html', {'articles': articles})


def brand_products(request, brand_name):
    """Displays all medicines from a specific brand."""
    # We use __iexact so that 'bayer' and 'Bayer' both work
    results = Medicine.objects.filter(brand__iexact=brand_name)

    return render(request, 'brand.html', {
        'results': results,
        'brand_name': brand_name
    })

@never_cache
@login_required(login_url='login')
def dashboard(request):
    """Displays the user's order history and prescription statuses."""
    # Grab all regular shop orders for this specific user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Grab all prescription uploads for this specific user
    # (Assuming your PrescriptionOrder model has a 'user' field and a 'created_at' or 'date' field)
    prescriptions = PrescriptionOrder.objects.filter(user=request.user).order_by('-uploaded_at')

    return render(request, 'dashboard.html', {
        'orders': orders,
        'prescriptions': prescriptions
    })


def update_quantity(request, item_id, action):
    """Increases, decreases, or manually sets the quantity of an item in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id)

    # NEW: Handle manual text input (if they type a number and submit the form)
    if request.method == 'POST':
        try:
            # Grab the number they typed in
            new_quantity = int(request.POST.get('quantity', cart_item.quantity))

            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
            else:
                cart_item.delete()  # If they type 0, remove it from the cart
        except ValueError:
            pass  # If they typed letters/gibberish, safely ignore it

    # OLD: Handle the + / - button clicks
    else:
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

    # Refresh the page seamlessly
    return redirect(request.META.get('HTTP_REFERER', 'cart'))

def about(request):
    """Renders the About Us page."""
    return render(request, 'about.html')