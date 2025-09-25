from __future__ import annotations

from django.contrib import admin

from .models import (
    Budget,
    AccountingRecord,
    Client,
    CurrentAccountMovement,
    Expense,
    Invoice,
    Material,
    OrderPhoto,
    ProductionOrder,
    ProductionOrderItem,
    Remittance,
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
    list_display = (
        "number",
        "invoice_type",
        "date",
        "gross_amount",
        "iva_amount",
        "additional_tax_amount",
        "amount",
    )
    list_filter = ("invoice_type", "date", "iva_rate", "additional_tax_type")
    search_fields = ("number", "client__name", "supplier__name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("category", "date", "amount")
    list_filter = ("category", "date")


@admin.register(Remittance)
class RemittanceAdmin(admin.ModelAdmin):
    list_display = ("number", "date", "client", "order")
    search_fields = ("number", "client__name", "order__order_number")
    list_filter = ("date",)


@admin.register(CurrentAccountMovement)
class CurrentAccountMovementAdmin(admin.ModelAdmin):
    list_display = ("movement_type", "date", "client", "supplier", "amount")
    list_filter = ("movement_type", "date")
    search_fields = ("client__name", "supplier__name", "concept")


@admin.register(AccountingRecord)
class AccountingRecordAdmin(admin.ModelAdmin):
    list_display = ("record_type", "date", "description", "debit", "credit")
    list_filter = ("record_type", "date")
    search_fields = ("description", "client__name", "supplier__name", "document_number")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
