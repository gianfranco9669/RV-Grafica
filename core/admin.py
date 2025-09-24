from __future__ import annotations

from django.contrib import admin

from .models import (
    Budget,
    Client,
    Expense,
    Invoice,
    Material,
    OrderPhoto,
    ProductionOrder,
    ProductionOrderItem,
    Supplier,
    UserProfile,
)


class ProductionOrderItemInline(admin.TabularInline):
    model = ProductionOrderItem
    extra = 0


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    inlines = [ProductionOrderItemInline]
    list_display = ("order_number", "client", "order_date", "status")
    list_filter = ("status", "order_date")
    search_fields = ("order_number", "client__name")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "service_line", "contact_name", "phone")
    search_fields = ("name", "service_line", "contact_name")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "phone")
    search_fields = ("name", "contact_name")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(OrderPhoto)
class OrderPhotoAdmin(admin.ModelAdmin):
    list_display = ("order", "uploaded_by", "created_at")
    list_filter = ("materials",)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "date", "total_amount")
    list_filter = ("date",)
    search_fields = ("title", "client__name")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "invoice_type", "date", "amount")
    list_filter = ("invoice_type", "date")
    search_fields = ("number", "client__name", "supplier__name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("category", "date", "amount")
    list_filter = ("category", "date")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
