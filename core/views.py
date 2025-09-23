from __future__ import annotations

from typing import Iterable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.db import models
from django.db.models import Max  # <- añadido para next_order_number
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from .forms import (
    BudgetForm,
    ClientForm,
    ExpenseForm,
    InvoiceForm,
    OrderItemForm,
    OrderItemFormSet,
    OrderPhotoForm,
    ProductionOrderForm,
    SupplierForm,
    update_order_item_formset_labels,
)
from .models import (
    Budget,
    Client,
    Expense,
    Invoice,
    ORDER_ITEM_PRESETS,
    OrderPhoto,
    ProductionOrder,
    ProductionOrderItem,
    Supplier,
    UserProfile,
)


# ---------------------------
# Mixins de rol/permisos
# ---------------------------

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles: set[str] = set()

    def test_func(self) -> bool:
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        profile = getattr(user, "profile", None)
        return bool(profile and profile.role in self.allowed_roles)

    def handle_no_permission(self) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseForbidden("No tenés permisos para acceder a esta sección.")


class AdministrativeRequiredMixin(LoginRequiredMixin, RoleRequiredMixin):
    allowed_roles = {UserProfile.ROLE_ADMINISTRATIVE, UserProfile.ROLE_ADMIN}


class AdminOnlyMixin(LoginRequiredMixin, RoleRequiredMixin):
    allowed_roles = {UserProfile.ROLE_ADMIN}


# ---------------------------
# Dashboard
# ---------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_orders"] = ProductionOrder.objects.filter(status=ProductionOrder.STATUS_PENDING).count()
        context["in_progress_orders"] = ProductionOrder.objects.filter(status=ProductionOrder.STATUS_IN_PROGRESS).count()
        context["completed_orders"] = ProductionOrder.objects.filter(status=ProductionOrder.STATUS_COMPLETED).count()
        context["budgets_count"] = Budget.objects.count()
        context["sales_invoices"] = Invoice.objects.filter(invoice_type=Invoice.TYPE_SALE).count()
        context["purchase_invoices"] = Invoice.objects.filter(invoice_type=Invoice.TYPE_PURCHASE).count()
        expenses = Expense.objects.aggregate(total=models.Sum("amount"))
        context["expense_total"] = expenses.get("total") or 0
        profile = getattr(self.request.user, "profile", None)
        context["can_manage_orders"] = self.request.user.is_superuser or (profile and profile.is_administrative)
        return context


# ---------------------------
# Utilidades de órdenes
# ---------------------------

def _get_next_order_number() -> int:
    """
    Devuelve el próximo número de orden para mostrar en 'Nueva orden'.
    (El modelo igual autoasigna al guardar si está vacío.)
    """
    max_number = ProductionOrder.objects.aggregate(Max("order_number"))["order_number__max"] or 0
    return max_number + 1


def _iter_items_from_source(source) -> list:
    """
    Dado un 'source' que puede ser un Budget o una ProductionOrder (o None),
    intenta devolver una lista de items relacionados (source.items.all()).
    Retorna [] si no hay relación o si algo falla.
    """
    if not source:
        return []
    rel = getattr(source, "items", None)
    if not rel:
        return []
    try:
        return list(rel.all())
    except Exception:
        return []


def build_order_item_initial(source=None) -> list[dict]:
    """
    Devuelve filas iniciales para el formset de ítems de orden.
    - Si 'source' (Budget/ProductionOrder) tiene items, copia sus campos.
    - Si no hay nada, devuelve 1 fila en blanco.
    Se alinea con OrderItemForm: preset_key, preset_name, detail, colors, measure, quantity, unit_price, total_amount.
    """
    rows: list[dict] = []

    for it in _iter_items_from_source(source):
        if not it:
            continue
        rows.append({
            "preset_key": getattr(it, "preset_label", getattr(it, "preset_key", "")) or "",
            # preset_name = texto visible/EDITABLE de “Descripción del trabajo”
            "preset_name": getattr(it, "description", getattr(it, "detail", "")) or "",
            "detail": getattr(it, "detail", getattr(it, "description", "")) or "",
            "colors": getattr(it, "colors", "") or "",
            "measure": getattr(it, "measure", "") or "",
            "quantity": getattr(it, "quantity", 1) or 1,
            "unit_price": getattr(it, "unit_price", 0) or 0,
            "total_amount": getattr(it, "total_amount", 0) or 0,
        })

    if not rows:
        rows = [{
            "preset_key": "",
            "preset_name": "",
            "detail": "",
            "colors": "",
            "measure": "",
            "quantity": 1,
            "unit_price": "",
            "total_amount": "",
        }]

    return rows


def save_order_items(order: ProductionOrder, formset: Iterable[OrderItemForm]) -> None:
    """
    Guarda/actualiza los ítems de la orden a partir del formset.
    Usa preset_key como llave lógica (compatible con ORDER_ITEM_PRESETS).
    """
    for form in formset:
        if not getattr(form, "cleaned_data", None):
            continue
        if form.cleaned_data.get("DELETE"):
            continue

        preset_key = form.cleaned_data.get("preset_key")
        if not preset_key:
            # Si querés permitir líneas sin preset, cambiá a create() y guarda preset_label vacío.
            continue

        ProductionOrderItem.objects.update_or_create(
            order=order,
            preset_label=preset_key,
            defaults={
                # Si no hay 'detail', usa lo que el usuario escribió en 'preset_name'
                "detail": form.cleaned_data.get("detail", "") or form.cleaned_data.get("preset_name", ""),
                "colors": form.cleaned_data.get("colors", ""),
                "measure": form.cleaned_data.get("measure", ""),
                "quantity": form.cleaned_data.get("quantity") or 1,
                "unit_price": form.cleaned_data.get("unit_price") or 0,
                "total_amount": form.cleaned_data.get("total_amount") or 0,
            },
        )


# ---------------------------
# Órdenes
# ---------------------------

class ProductionOrderListView(LoginRequiredMixin, ListView):
    template_name = "core/order_list.html"
    model = ProductionOrder
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("client")
        status = self.request.GET.get("estado")
        if status in {choice[0] for choice in ProductionOrder.STATUS_CHOICES}:
            queryset = queryset.filter(status=status)
        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(
                models.Q(client__name__icontains=search) |
                models.Q(order_number__icontains=search)
            )
        return queryset.order_by("-order_date", "-order_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("estado", "")
        context["search"] = self.request.GET.get("q", "")
        profile = getattr(self.request.user, "profile", None)
        context["can_manage_orders"] = self.request.user.is_superuser or (profile and profile.is_administrative)
        return context


class ProductionOrderCreateView(AdministrativeRequiredMixin, TemplateView):
    """
    Create con form principal y formset de ítems.
    Soporta prellenado opcional desde presupuesto: /ordenes/nueva/?preset_budget=ID
    """
    template_name = "core/order_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Intento de preset por presupuesto
        preset = None
        preset_id = request.GET.get("preset_budget")
        if preset_id:
            preset = Budget.objects.filter(pk=preset_id).first()

        form = ProductionOrderForm(initial={"status": ProductionOrder.STATUS_PENDING})
        formset = OrderItemFormSet(initial=build_order_item_initial(preset))
        update_order_item_formset_labels(formset)
        context = {
            "form": form,
            "formset": formset,
            "is_edit": False,
            "default_status": ProductionOrder.STATUS_PENDING,
            "next_order_number": _get_next_order_number(),  # <- mostrar N° próximo en la UI
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        update_order_item_formset_labels(formset)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            # El modelo autoasigna order_number si está vacío
            order.created_by = request.user
            order.save()
            save_order_items(order, formset)
            messages.success(request, "Orden de producción creada correctamente.")
            return redirect("order_detail", pk=order.pk)
        messages.error(request, "Revisá los datos cargados. Hay errores en el formulario.")
        context = {
            "form": form,
            "formset": formset,
            "is_edit": False,
            "default_status": ProductionOrder.STATUS_PENDING,
            "next_order_number": _get_next_order_number(),  # volver a mostrarlo en caso de error
        }
        return self.render_to_response(context)


class ProductionOrderUpdateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/order_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.order = ProductionOrder.objects.select_related("client").get(pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(instance=self.order)
        # Prellenar desde los ítems existentes de la orden
        initial_rows = build_order_item_initial(self.order)
        formset = OrderItemFormSet(initial=initial_rows)
        update_order_item_formset_labels(formset)
        context = {
            "form": form,
            "formset": formset,
            "is_edit": True,
            "order": self.order,
            "default_status": self.order.status,
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(request.POST, instance=self.order)
        formset = OrderItemFormSet(request.POST)
        update_order_item_formset_labels(formset)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            save_order_items(order, formset)
            messages.success(request, "Orden de producción actualizada.")
            return redirect("order_detail", pk=order.pk)
        messages.error(request, "No se pudo actualizar la orden. Verificá la información ingresada.")
        context = {
            "form": form,
            "formset": formset,
            "is_edit": True,
            "order": self.order,
            "default_status": self.order.status,
        }
        return self.render_to_response(context)


class ProductionOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "core/order_detail.html"
    model = ProductionOrder

    def get_ordered_items(self) -> list[ProductionOrderItem]:
        order = self.get_object()
        items_map = {item.preset_label: item for item in order.items.all()}
        ordered_items: list[ProductionOrderItem] = []
        for key, _ in ORDER_ITEM_PRESETS:
            if key in items_map:
                ordered_items.append(items_map[key])
            else:
                ordered_items.append(ProductionOrderItem(order=order, preset_label=key))
        return ordered_items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context["items"] = self.get_ordered_items()
        photo_form = kwargs.get("photo_form") or OrderPhotoForm()
        context["photo_form"] = photo_form
        profile = getattr(self.request.user, "profile", None)
        context["can_edit"] = self.request.user.is_superuser or (profile and profile.is_administrative)
        context["can_upload"] = can_upload_photos(self.request.user)
        context["photos"] = order.photos.select_related("uploaded_by").prefetch_related("materials")
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        if not can_upload_photos(request.user):
            return HttpResponseForbidden("No tenés permisos para subir fotos.")
        form = OrderPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = OrderPhoto.objects.create(
                order=self.object,
                image=form.cleaned_data["image"],
                description=form.cleaned_data.get("description", ""),
                uploaded_by=request.user,
            )
            if form.cleaned_data.get("materials"):
                photo.materials.set(form.cleaned_data["materials"])
            messages.success(request, "Foto subida correctamente.")
            return redirect("order_detail", pk=self.object.pk)
        context = self.get_context_data(photo_form=form)
        return self.render_to_response(context)


def can_upload_photos(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.role in {UserProfile.ROLE_OPERATOR, UserProfile.ROLE_ADMINISTRATIVE, UserProfile.ROLE_ADMIN})


# ---------------------------
# Presupuestos
# ---------------------------

class BudgetListView(AdministrativeRequiredMixin, ListView):
    template_name = "core/budget_list.html"
    model = Budget
    paginate_by = 20


class BudgetCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/budget_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = BudgetForm()
        return self.render_to_response({"form": form, "is_edit": False})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.created_by = request.user
            budget.save()
            messages.success(request, "Presupuesto guardado correctamente.")
            return redirect("budget_list")
        messages.error(request, "Hay errores en el formulario de presupuesto.")
        return self.render_to_response({"form": form, "is_edit": False})


class BudgetUpdateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/budget_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.budget = Budget.objects.get(pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = BudgetForm(instance=self.budget)
        return self.render_to_response({"form": form, "is_edit": True, "budget": self.budget})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = BudgetForm(request.POST, instance=self.budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Presupuesto actualizado.")
            return redirect("budget_list")
        messages.error(request, "No se pudo actualizar el presupuesto.")
        return self.render_to_response({"form": form, "is_edit": True, "budget": self.budget})


# ---------------------------
# Facturación / Gastos
# ---------------------------

class InvoiceListView(AdministrativeRequiredMixin, ListView):
    template_name = "core/invoice_list.html"
    model = Invoice
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("client", "supplier", "order")
        invoice_type = self.request.GET.get("tipo")
        if invoice_type in {choice[0] for choice in Invoice.TYPE_CHOICES}:
            queryset = queryset.filter(invoice_type=invoice_type)
        return queryset.order_by("-date", "-id")


class InvoiceCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/invoice_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = InvoiceForm()
        return self.render_to_response({"form": form})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, "Factura guardada correctamente.")
            return redirect("invoice_list")
        messages.error(request, "Hay errores en la carga de la factura.")
        return self.render_to_response({"form": form})


class ExpenseListView(AdministrativeRequiredMixin, ListView):
    template_name = "core/expense_list.html"
    model = Expense
    paginate_by = 20
    ordering = ["-date", "-id"]


class ExpenseCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/expense_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ExpenseForm()
        return self.render_to_response({"form": form})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            messages.success(request, "Gasto registrado.")
            return redirect("expense_list")
        messages.error(request, "No se pudo guardar el gasto.")
        return self.render_to_response({"form": form})


# ---------------------------
# Clientes / Proveedores
# ---------------------------

class ClientListView(AdministrativeRequiredMixin, ListView):
    template_name = "core/client_list.html"
    model = Client
    paginate_by = 50
    ordering = ["name"]


class ClientCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/client_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ClientForm()
        return self.render_to_response({"form": form, "is_edit": False})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente agregado.")
            return redirect("client_list")
        return self.render_to_response({"form": form, "is_edit": False})


class ClientUpdateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/client_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.client = Client.objects.get(pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ClientForm(instance=self.client)
        return self.render_to_response({"form": form, "is_edit": True, "client": self.client})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ClientForm(request.POST, instance=self.client)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado.")
            return redirect("client_list")
        return self.render_to_response({"form": form, "is_edit": True, "client": self.client})


class SupplierListView(AdministrativeRequiredMixin, ListView):
    template_name = "core/supplier_list.html"
    model = Supplier
    paginate_by = 50
    ordering = ["name"]


class SupplierCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/supplier_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = SupplierForm()
        return self.render_to_response({"form": form, "is_edit": False})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor agregado.")
            return redirect("supplier_list")
        return self.render_to_response({"form": form, "is_edit": False})


class SupplierUpdateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/supplier_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.supplier = Supplier.objects.get(pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = SupplierForm(instance=self.supplier)
        return self.render_to_response({"form": form, "is_edit": True, "supplier": self.supplier})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = SupplierForm(request.POST, instance=self.supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado.")
            return redirect("supplier_list")
        return self.render_to_response({"form": form, "is_edit": True, "supplier": self.supplier})
