from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Max
from django.utils import timezone

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(TimeStampedModel):
    name = models.CharField(max_length=255)
    service_line = models.CharField("Empresa / Línea", max_length=255, blank=True)
    contact_name = models.CharField("Nombre y apellido", max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.name


class Material(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.name

    @staticmethod
    def default_materials() -> list[str]:
        return [
            "Reflectivo",
            "Polarizado",
            "Ploteo",
            "Vinilo impreso",
            "Microperforado",
        ]


ORDER_ITEM_PRESETS: list[tuple[str, str]] = [
    ("trompa", "Trompa"),
    ("estrellas_trompa", "Estrellas trompa"),
    ("interno_trompa", "Interno trompa"),
    ("luminosos", "Luminosos"),
    ("culata_logo", "Culata / logo"),
    ("estrellas_culata", "Estrellas culata"),
    ("internos", "Internos"),
    ("lateral", "Lateral"),
    ("lateral_exterior", "Lateral exterior"),
    ("estrellas_lateral", "Estrellas lateral"),
    ("parabrisas", "Parabrisas / aire"),
    ("obo_exterior", "Oblea exterior"),
    ("obo_interior", "Oblea interior"),
    ("silletas", "Silla / pechera"),
    ("estribos", "Estribos"),
    ("banda_reflectiva", "Banda reflectiva"),
    ("circulo_reflectivo", "Círculo reflectivo"),
    ("polarizado", "Polarizado"),
]


class ProductionOrder(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_IN_PROGRESS, "En curso"),
        (STATUS_COMPLETED, "Finalizada"),
    ]

    order_number = models.PositiveIntegerField(unique=True, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
    )
    order_date = models.DateField(default=date.today)
    service_line = models.CharField("Empresa / línea", max_length=255, blank=True)
    internal_code = models.CharField("Interno", max_length=100, blank=True)
    bodywork = models.CharField("Carrocería", max_length=255, blank=True)
    contact_name = models.CharField("Nombre y apellido", max_length=255, blank=True)
    email = models.EmailField("Mail", blank=True)
    phone = models.CharField("Tel", max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_orders",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-order_date", "-order_number"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        client_name = self.client.name if self.client else "Sin cliente"
        return f"Orden #{self.order_number} - {client_name}"

    def save(self, *args, **kwargs) -> None:
        if not self.order_number:
            max_number = ProductionOrder.objects.aggregate(Max("order_number"))["order_number__max"] or 0
            self.order_number = max_number + 1
        super().save(*args, **kwargs)

    @property
    def subtotal(self) -> Decimal:
        total = Decimal("0")
        for item in self.items.all():
            if item.total_amount is not None:
                total += item.total_amount
        return total


class ProductionOrderItem(TimeStampedModel):
    order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    preset_label = models.CharField(max_length=50, choices=ORDER_ITEM_PRESETS)
    custom_description = models.CharField(
        "Descripción personalizada",
        max_length=255,
        blank=True,
        default="",
    )
    detail = models.CharField(max_length=255, blank=True)
    colors = models.CharField(max_length=255, blank=True)
    measure = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("order", "preset_label")
        ordering = ["order", "id"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        label = self.custom_description or self.get_preset_label_display()
        return f"{label} ({self.order.order_number})"

    def save(self, *args, **kwargs) -> None:
        if self.total_amount is None and self.quantity is not None and self.unit_price is not None:
            self.total_amount = (self.quantity * self.unit_price).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)


class OrderPhoto(TimeStampedModel):
    order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = models.ImageField(upload_to="orders/photos/")
    description = models.CharField(max_length=255, blank=True)
    materials = models.ManyToManyField(Material, blank=True, related_name="order_photos")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_order_photos",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return f"Foto orden {self.order.order_number}"


class Budget(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name="budgets", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    square_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    price_per_square_meter = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    additional_costs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_budgets",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return f"Presupuesto {self.title}"

    def calculate_total(self) -> Decimal:
        return (self.square_meters * self.price_per_square_meter) + self.additional_costs

    def save(self, *args, **kwargs) -> None:
        self.total_amount = self.calculate_total().quantize(Decimal("0.01"))
        super().save(*args, **kwargs)


class Invoice(TimeStampedModel):
    TYPE_SALE = "sale"
    TYPE_PURCHASE = "purchase"
    TYPE_CHOICES = [
        (TYPE_SALE, "Factura de venta"),
        (TYPE_PURCHASE, "Factura de compra"),
    ]

    invoice_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    number = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_invoices",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]
        unique_together = ("invoice_type", "number")

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return f"Factura {self.number} ({self.get_invoice_type_display()})"

    def clean(self) -> None:
        if self.invoice_type == self.TYPE_SALE and not self.client:
            raise ValidationError("Las facturas de venta requieren un cliente asociado.")
        if self.invoice_type == self.TYPE_PURCHASE and not self.supplier:
            raise ValidationError("Las facturas de compra requieren un proveedor asociado.")


class Expense(TimeStampedModel):
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return f"Gasto {self.category} - {self.amount}"


class UserProfile(TimeStampedModel):
    ROLE_OPERATOR = "operator"
    ROLE_ADMINISTRATIVE = "administrative"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_OPERATOR, "Operativo"),
        (ROLE_ADMINISTRATIVE, "Administrativo"),
        (ROLE_ADMIN, "Administrador"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OPERATOR)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_operator(self) -> bool:
        return self.role == self.ROLE_OPERATOR

    @property
    def is_administrative(self) -> bool:
        return self.role in {self.ROLE_ADMINISTRATIVE, self.ROLE_ADMIN}

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN
