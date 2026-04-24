from django.contrib import admin
from .models import PrescriptionOrder, Medicine, Cart, CartItem, Order, OrderItem, Article


# This tells Django to add this table to the admin panel
@admin.register(PrescriptionOrder)
class PrescriptionOrderAdmin(admin.ModelAdmin):
    # This controls what columns you see when you look at the list of orders
    list_display = ('patient_name', 'phone_number', 'status', 'uploaded_at')

    # Adds a handy filter box on the right side to sort by Pending or Paid
    list_filter = ('status', 'uploaded_at')

    # Adds a search bar so you can look up a customer by name or phone
    search_fields = ('patient_name', 'phone_number')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_trending')
    list_filter = ('category', 'is_trending')
    search_fields = ('name',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'cart', 'quantity', 'is_active')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Don't show extra blank rows

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    inlines = [OrderItemInline] # This shows the purchased items directly inside the Order page!

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date')
    search_fields = ('title', 'content')