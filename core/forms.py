from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django import forms
from django.forms import formset_factory

from .models import (
    Budget,
    Client,
    Expense,
    Invoice,
    Material,
    ORDER_ITEM_PRESETS,
    ProductionOrder,
    Supplier,
)


def _widget_with_class(widget: forms.Widget, css_class: str = "form-control") -> forms.Widget:
    if isinstance(widget, forms.Select):
        widget.attrs.setdefault("class", "form-select")
    elif isinstance(widget, forms.CheckboxSelectMultiple):
        widget.attrs.setdefault("class", "form-check-input")
    else:
        widget.attrs.setdefault("class", css_class)
    return widget


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "service_line", "contact_name", "email", "phone", "notes"]
        widgets = {
            "name": _widget_with_class(forms.TextInput()),
            "service_line": _widget_with_class(forms.TextInput()),
            "contact_name": _widget_with_class(forms.TextInput()),
            "email": _widget_with_class(forms.EmailInput()),
            "phone": _widget_with_class(forms.TextInput()),
            "notes": _widget_with_class(forms.Textarea(attrs={"rows": 3})),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_name", "email", "phone", "notes"]
        widgets = {
            "name": _widget_with_class(forms.TextInput()),
            "contact_name": _widget_with_class(forms.TextInput()),
            "email": _widget_with_class(forms.EmailInput()),
            "phone": _widget_with_class(forms.TextInput()),
            "notes": _widget_with_class(forms.Textarea(attrs={"rows": 3})),
        }


class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = [
            "client",
            "order_date",
            "service_line",
            "internal_code",
            "bodywork",
            "contact_name",
            "email",
            "phone",
            "status",
            "notes",
        ]
        widgets = {
            "client": _widget_with_class(forms.Select()),
            "order_date": _widget_with_class(forms.DateInput(attrs={"type": "date"})),
            "service_line": _widget_with_class(forms.TextInput()),
            "internal_code": _widget_with_class(forms.TextInput()),
            "bodywork": _widget_with_class(forms.TextInput()),
            "contact_name": _widget_with_class(forms.TextInput()),
            "email": _widget_with_class(forms.EmailInput()),
            "phone": _widget_with_class(forms.TextInput()),
            "status": _widget_with_class(forms.Select()),
            "notes": _widget_with_class(forms.Textarea(attrs={"rows": 3})),
        }


class OrderItemForm(forms.Form):
    preset_key = forms.CharField(widget=forms.HiddenInput())
    preset_name = forms.CharField(label="Descripción", required=False, disabled=True)
    detail = forms.CharField(label="Detalle", required=False)
    colors = forms.CharField(label="Colores", required=False)
    measure = forms.CharField(label="Medida", required=False)
    quantity = forms.DecimalField(
        label="Cant.",
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    unit_price = forms.DecimalField(
        label="Precio",
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
    )
    total_amount = forms.DecimalField(
        label="Total",
        required=False,
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0"),
    )

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        quantity = cleaned_data.get("quantity")
        unit_price = cleaned_data.get("unit_price")
        total_amount = cleaned_data.get("total_amount")
        if total_amount is None and quantity is not None and unit_price is not None:
            cleaned_data["total_amount"] = (quantity * unit_price).quantize(Decimal("0.01"))
        return cleaned_data


OrderItemFormSet = formset_factory(OrderItemForm, extra=0)


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            "client",
            "title",
            "description",
            "date",
            "square_meters",
            "price_per_square_meter",
            "additional_costs",
        ]
        widgets = {
            "client": _widget_with_class(forms.Select()),
            "title": _widget_with_class(forms.TextInput()),
            "description": _widget_with_class(forms.Textarea(attrs={"rows": 3})),
            "date": _widget_with_class(forms.DateInput(attrs={"type": "date"})),
            "square_meters": _widget_with_class(forms.NumberInput(attrs={"step": "0.01"})),
            "price_per_square_meter": _widget_with_class(forms.NumberInput(attrs={"step": "0.01"})),
            "additional_costs": _widget_with_class(forms.NumberInput(attrs={"step": "0.01"})),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_type",
            "number",
            "date",
            "client",
            "supplier",
            "order",
            "amount",
            "description",
        ]
        widgets = {
            "invoice_type": _widget_with_class(forms.Select()),
            "number": _widget_with_class(forms.TextInput()),
            "date": _widget_with_class(forms.DateInput(attrs={"type": "date"})),
            "client": _widget_with_class(forms.Select()),
            "supplier": _widget_with_class(forms.Select()),
            "order": _widget_with_class(forms.Select()),
            "amount": _widget_with_class(forms.NumberInput(attrs={"step": "0.01"})),
            "description": _widget_with_class(forms.Textarea(attrs={"rows": 3})),
        }

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        invoice_type = cleaned_data.get("invoice_type")
        client = cleaned_data.get("client")
        supplier = cleaned_data.get("supplier")
        if invoice_type == Invoice.TYPE_SALE and not client:
            self.add_error("client", "Seleccioná un cliente para la factura de venta.")
        if invoice_type == Invoice.TYPE_PURCHASE and not supplier:
            self.add_error("supplier", "Seleccioná un proveedor para la factura de compra.")
        return cleaned_data


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "description", "date", "amount"]
        widgets = {
            "category": _widget_with_class(forms.TextInput()),
            "description": _widget_with_class(forms.Textarea(attrs={"rows": 2})),
            "date": _widget_with_class(forms.DateInput(attrs={"type": "date"})),
            "amount": _widget_with_class(forms.NumberInput(attrs={"step": "0.01"})),
        }


class OrderPhotoForm(forms.Form):
    image = forms.ImageField(label="Foto")
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=_widget_with_class(forms.Textarea(attrs={"rows": 2})),
    )
    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Materiales utilizados",
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["materials"].queryset = Material.objects.all()
        self.fields["image"].widget = _widget_with_class(self.fields["image"].widget)
        self.fields["materials"].widget.attrs.setdefault("class", "form-check-input")


def update_order_item_formset_labels(formset: Iterable[OrderItemForm]) -> None:
    label_map = {key: label for key, label in ORDER_ITEM_PRESETS}
    for form in formset:
        preset_key = form.initial.get("preset_key") or form.data.get(form.add_prefix("preset_key"))
        if preset_key:
            form.fields["preset_name"].initial = label_map.get(preset_key, "")
        form.fields["detail"].widget = _widget_with_class(forms.TextInput())
        form.fields["colors"].widget = _widget_with_class(forms.TextInput())
        form.fields["measure"].widget = _widget_with_class(forms.TextInput())
        form.fields["quantity"].widget = _widget_with_class(forms.NumberInput(attrs={"step": "0.01"}))
        form.fields["unit_price"].widget = _widget_with_class(forms.NumberInput(attrs={"step": "0.01"}))
        form.fields["total_amount"].widget = _widget_with_class(forms.NumberInput(attrs={"step": "0.01"}))
