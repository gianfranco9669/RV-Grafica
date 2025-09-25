from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("ordenes/", views.ProductionOrderListView.as_view(), name="order_list"),
    path("ordenes/nueva/", views.ProductionOrderCreateView.as_view(), name="order_create"),
    path("ordenes/<int:pk>/", views.ProductionOrderDetailView.as_view(), name="order_detail"),
    path("ordenes/<int:pk>/editar/", views.ProductionOrderUpdateView.as_view(), name="order_update"),
    path("presupuestos/", views.BudgetListView.as_view(), name="budget_list"),
    path("presupuestos/nuevo/", views.BudgetCreateView.as_view(), name="budget_create"),
    path("presupuestos/<int:pk>/editar/", views.BudgetUpdateView.as_view(), name="budget_update"),
    path("facturacion/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("facturacion/nueva/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("facturacion/remitos/", views.RemittanceListView.as_view(), name="remittance_list"),
    path("facturacion/remitos/nuevo/", views.RemittanceCreateView.as_view(), name="remittance_create"),
    path("gastos/", views.ExpenseListView.as_view(), name="expense_list"),
    path("gastos/nuevo/", views.ExpenseCreateView.as_view(), name="expense_create"),
    path("clientes/", views.ClientListView.as_view(), name="client_list"),
    path("clientes/nuevo/", views.ClientCreateView.as_view(), name="client_create"),
    path("clientes/<int:pk>/editar/", views.ClientUpdateView.as_view(), name="client_update"),
    path("proveedores/", views.SupplierListView.as_view(), name="supplier_list"),
    path("proveedores/nuevo/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("proveedores/<int:pk>/editar/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("reportes/", views.ReportsView.as_view(), name="reports"),
    path("finanzas/", views.FinanceMovementListView.as_view(), name="finance_movement_list"),
    path("finanzas/nuevo/", views.FinanceMovementCreateView.as_view(), name="finance_movement_create"),
    path("contabilidad/", views.AccountingRecordListView.as_view(), name="accounting_record_list"),
    path("contabilidad/nuevo/", views.AccountingRecordCreateView.as_view(), name="accounting_record_create"),
]
