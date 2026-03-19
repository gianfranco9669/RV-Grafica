from __future__ import annotations

from typing import Iterable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import (
    BudgetForm,
    ClientForm,
    CommercialContactForm,
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


class LandingPageView(FormView):
    template_name = "core/landing.html"
    form_class = CommercialContactForm
    success_url = reverse_lazy("landing")

    def form_valid(self, form):
        company_name = form.cleaned_data["company_name"]
        messages.success(
            self.request,
            f"Gracias por contactarte con AVESOL, {company_name}. Tu consulta comercial quedó registrada para una futura integración operativa.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse_lazy('landing')}#contacto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_categories"] = [
            {
                "name": "Pollos enteros",
                "description": "Soluciones para abastecimiento de volumen con foco en presentación uniforme, conservación y continuidad comercial.",
                "icon": "bi-basket2-fill",
                "tag": "Rotación de góndola y freezer",
            },
            {
                "name": "Trozados",
                "description": "Pechuga, pata muslo, alitas y cortes preparados para distintos canales de venta y necesidades de reposición.",
                "icon": "bi-grid-1x2-fill",
                "tag": "Versatilidad por corte",
            },
            {
                "name": "Papas fritas",
                "description": "Líneas pensadas para gastronomía y comercios que buscan rendimiento, practicidad y regularidad en producto congelado.",
                "icon": "bi-stars",
                "tag": "Alto consumo",
            },
            {
                "name": "Congelados",
                "description": "Mix de productos congelados para ampliar surtido y atender distintas oportunidades comerciales del canal moderno.",
                "icon": "bi-snow2",
                "tag": "Surtido escalable",
            },
            {
                "name": "Rebozados",
                "description": "Opciones listas para venta rápida o cocina profesional, con foco en practicidad, rendimiento y salida sostenida.",
                "icon": "bi-shield-fill-check",
                "tag": "Conveniencia y valor agregado",
            },
            {
                "name": "Línea gastronómica",
                "description": "Productos especiales y presentaciones orientadas a restaurantes, hoteles, rotiserías y cocinas de alta demanda.",
                "icon": "bi-briefcase-fill",
                "tag": "Canal Horeca",
            },
        ]
        context["features"] = [
            {
                "title": "Calidad comercial",
                "description": "Selección de líneas aptas para sostener imagen, rotación y confianza en cada canal de venta.",
                "icon": "bi-award",
            },
            {
                "title": "Cadena de frío",
                "description": "Conservación y manipulación orientadas a resguardar temperatura, producto y condición de entrega.",
                "icon": "bi-thermometer-snow",
            },
            {
                "title": "Distribución coordinada",
                "description": "Organización logística según recorridos, frecuencia de compra, prioridades y ventanas de recepción.",
                "icon": "bi-truck",
            },
            {
                "title": "Stock programado",
                "description": "Visión de abastecimiento para reducir quiebres, ordenar reposición y acompañar el crecimiento del cliente.",
                "icon": "bi-boxes",
            },
            {
                "title": "Atención comercial",
                "description": "Seguimiento cercano de cuentas, consultas, cotizaciones y oportunidades de ampliación de surtido.",
                "icon": "bi-headset",
            },
            {
                "title": "Cobertura flexible",
                "description": "Modelo preparado para adaptarse a zonas, escalas operativas y requerimientos de entrega.",
                "icon": "bi-geo-alt",
            },
            {
                "title": "Cumplimiento",
                "description": "Compromiso con tiempos, coordinación y una relación profesional basada en previsibilidad.",
                "icon": "bi-check2-circle",
            },
            {
                "title": "Escala comercial",
                "description": "Preparación para operar con cuentas recurrentes, lanzamientos y desarrollos por volumen.",
                "icon": "bi-bar-chart-line",
            },
        ]
        context["segments"] = [
            {
                "title": "Mayoristas y distribuidores",
                "description": "Propuestas para operadores que necesitan surtido competitivo, volumen y entregas coordinadas.",
            },
            {
                "title": "Supermercados y autoservicios",
                "description": "Líneas de abastecimiento para freezers, góndolas y rotación constante en puntos de venta.",
            },
            {
                "title": "Restaurantes y gastronomía",
                "description": "Opciones congeladas orientadas a practicidad, rendimiento y continuidad en cocina profesional.",
            },
            {
                "title": "Comercios y granjas",
                "description": "Mix de productos para ampliar oferta, sostener calidad y fortalecer la propuesta comercial del local.",
            },
        ]
        context["featured_products"] = [
            {
                "category": "Trozados y avícolas",
                "name": "Línea de cortes seleccionados",
                "description": "Bloque modelo para destacar presentaciones con información comercial clara y futura ficha técnica.",
                "details": ["Presentaciones adaptables", "Canal mayorista o retail", "Base para integrar gramajes y marcas"],
                "image": "images/avesol-storage.svg",
                "alt": "Cámaras y pallets como soporte del catálogo comercial de trozados y productos avícolas",
            },
            {
                "category": "Papas y congelados",
                "name": "Soluciones para alto giro",
                "description": "Ideal para comunicar productos de salida constante en gastronomía, autoservicios y comercios especializados.",
                "details": ["Practicidad operativa", "Reposición sostenida", "Formato escalable para nuevas líneas"],
                "image": "images/avesol-hero-grid.svg",
                "alt": "Composición visual de distintas familias de productos congelados para catálogo AVESOL",
            },
            {
                "category": "Rebozados y especiales",
                "name": "Línea lista para potenciar surtido",
                "description": "Espacio preparado para sumar artículos de conveniencia, gastronómicos o de valor agregado comercial.",
                "details": ["Mayor ticket por categoría", "Venta rápida", "Preparado para filtros y fichas"],
                "image": "images/avesol-distribution.svg",
                "alt": "Despacho y logística de productos congelados listos para entrega a clientes comerciales",
            },
        ]
        context["process_steps"] = [
            {
                "title": "Selección comercial",
                "description": "Definimos el surtido y las líneas más convenientes según canal, demanda y perfil de rotación.",
            },
            {
                "title": "Almacenamiento y conservación",
                "description": "Organizamos stock bajo criterios de orden, temperatura y cuidado del producto congelado.",
            },
            {
                "title": "Armado de pedidos",
                "description": "Consolidamos cada solicitud priorizando exactitud, presentación y preparación para despacho eficiente.",
            },
            {
                "title": "Distribución coordinada",
                "description": "Programamos entregas según zona, frecuencia y requerimientos operativos de cada cliente.",
            },
            {
                "title": "Recepción y seguimiento",
                "description": "Sostenemos comunicación comercial para resolver consultas, reposiciones y oportunidades de crecimiento.",
            },
            {
                "title": "Desarrollo de cuenta",
                "description": "Acompañamos la evolución del negocio con nuevas categorías, mix comercial y planificación de abastecimiento.",
            },
        ]
        context["trust_quotes"] = [
            {
                "quote": "Necesitábamos una propuesta ordenada para reposición frecuente y AVESOL nos transmitió estructura, respuesta y seriedad.",
                "author": "Cliente placeholder",
                "role": "Cadena de cercanía",
            },
            {
                "quote": "La lógica comercial está pensada para abastecer con previsibilidad, algo clave cuando el congelado tiene alta rotación.",
                "author": "Testimonio placeholder",
                "role": "Distribuidor regional",
            },
            {
                "quote": "La web deja claro el perfil corporativo de una empresa preparada para trabajar con cuentas reales del mercado.",
                "author": "Referencia placeholder",
                "role": "Compras gastronómicas",
            },
        ]
        return context


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
        context["can_manage_orders"] = self.request.user.is_superuser or (
            profile and profile.is_administrative
        )
        return context


# ---------------------------
# Utilidades de órdenes
# ---------------------------

def build_order_item_initial(order: ProductionOrder | None = None) -> list[dict[str, object]]:
    """
    Devuelve filas iniciales para el formset:
    - Si hay order con items, copia por preset_label.
    - Si no hay, genera una fila por cada preset con valores seguros.
    """
    items_map: dict[str, ProductionOrderItem] = {}
    if order is not None:
        items_map = {item.preset_label: item for item in order.items.all()}

    initial: list[dict[str, object]] = []
    for key, label in ORDER_ITEM_PRESETS:
        item = items_map.get(key)
        initial.append(
            {
                "preset_key": key,
                # editable y con valor por defecto si no hay item
                "preset_name": (getattr(item, "custom_description", None) or label),
                "detail": getattr(item, "detail", "") or "",
                "colors": getattr(item, "colors", "") or "",
                "measure": getattr(item, "measure", "") or "",
                # usar None para que el form muestre vacío (no crashea)
                "quantity": getattr(item, "quantity", None),
                "unit_price": getattr(item, "unit_price", None),
                "total_amount": getattr(item, "total_amount", None),
            }
        )
    return initial


def save_order_items(order: ProductionOrder, formset: Iterable[OrderItemForm]) -> None:
    """
    Guarda/actualiza ítems usando preset_key como llave lógica.
    """
    for form in formset:
        if not getattr(form, "cleaned_data", None):
            continue
        preset_key = form.cleaned_data.get("preset_key")
        if not preset_key:
            # evitamos crear líneas huérfanas
            continue

        ProductionOrderItem.objects.update_or_create(
            order=order,
            preset_label=preset_key,
            defaults={
                "custom_description": form.cleaned_data.get("preset_name", "") or "",
                "detail": form.cleaned_data.get("detail", "") or "",
                "colors": form.cleaned_data.get("colors", "") or "",
                "measure": form.cleaned_data.get("measure", "") or "",
                # Si vienen None, guardamos 0 para campos numéricos
                "quantity": form.cleaned_data.get("quantity") or 0,
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
                models.Q(client__name__icontains=search) | models.Q(order_number__icontains=search)
            )
        return queryset.order_by("-order_date", "-order_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("estado", "")
        context["search"] = self.request.GET.get("q", "")
        profile = getattr(self.request.user, "profile", None)
        context["can_manage_orders"] = self.request.user.is_superuser or (
            profile and profile.is_administrative
        )
        return context


class ProductionOrderCreateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/order_form.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(initial={"status": ProductionOrder.STATUS_PENDING})
        formset = OrderItemFormSet(initial=build_order_item_initial())
        update_order_item_formset_labels(formset)
        context = {
            "form": form,
            "formset": formset,
            "is_edit": False,
            "default_status": ProductionOrder.STATUS_PENDING,
        }
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        update_order_item_formset_labels(formset)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
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
        }
        return self.render_to_response(context)


class ProductionOrderUpdateView(AdministrativeRequiredMixin, TemplateView):
    template_name = "core/order_form.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.order = ProductionOrder.objects.select_related("client").get(pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ProductionOrderForm(instance=self.order)
        formset = OrderItemFormSet(initial=build_order_item_initial(self.order))
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
        context["can_edit"] = self.request.user.is_superuser or (
            profile and profile.is_administrative
        )
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
    return bool(
        profile and profile.role in {UserProfile.ROLE_OPERATOR, UserProfile.ROLE_ADMINISTRATIVE, UserProfile.ROLE_ADMIN}
    )


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
