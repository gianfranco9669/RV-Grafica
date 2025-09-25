# Generated manually to bootstrap RV Gráfica models
from __future__ import annotations

import datetime
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("service_line", models.CharField(blank=True, max_length=255, verbose_name="Empresa / Línea")),
                ("contact_name", models.CharField(blank=True, max_length=255, verbose_name="Nombre y apellido")),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=100)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("contact_name", models.CharField(blank=True, max_length=255)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=100)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ProductionOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_number", models.PositiveIntegerField(editable=False, unique=True)),
                ("order_date", models.DateField(default=datetime.date.today)),
                ("service_line", models.CharField(blank=True, max_length=255, verbose_name="Empresa / línea")),
                ("internal_code", models.CharField(blank=True, max_length=100, verbose_name="Interno")),
                ("bodywork", models.CharField(blank=True, max_length=255, verbose_name="Carrocería")),
                ("contact_name", models.CharField(blank=True, max_length=255, verbose_name="Nombre y apellido")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Mail")),
                ("phone", models.CharField(blank=True, max_length=100, verbose_name="Tel")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente"),
                            ("in_progress", "En curso"),
                            ("completed", "Finalizada"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="core.client",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-order_date", "-order_number"],
            },
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField(default=datetime.date.today)),
                (
                    "square_meters",
                    models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0"))]),
                ),
                (
                    "price_per_square_meter",
                    models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0"))]),
                ),
                (
                    "additional_costs",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        max_digits=10,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(decimal_places=2, editable=False, max_digits=12),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="budgets",
                        to="core.client",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_budgets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.CharField(max_length=100)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("date", models.DateField(default=datetime.date.today)),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))]),
                ),
                (
                    "recorded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "invoice_type",
                    models.CharField(
                        choices=[("sale", "Factura de venta"), ("purchase", "Factura de compra")],
                        max_length=20,
                    ),
                ),
                ("number", models.CharField(max_length=100)),
                ("date", models.DateField(default=datetime.date.today)),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))]),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoices",
                        to="core.client",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_invoices",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoices",
                        to="core.productionorder",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoices",
                        to="core.supplier",
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-id"],
                "unique_together": {("invoice_type", "number")},
            },
        ),
        migrations.CreateModel(
            name="ProductionOrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "preset_label",
                    models.CharField(
                        choices=[
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
                        ],
                        max_length=50,
                    ),
                ),
                ("detail", models.CharField(blank=True, max_length=255)),
                ("colors", models.CharField(blank=True, max_length=255)),
                ("measure", models.CharField(blank=True, max_length=100)),
                (
                    "quantity",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="core.productionorder",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "id"],
                "unique_together": {("order", "preset_label")},
            },
        ),
        migrations.CreateModel(
            name="OrderPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("image", models.ImageField(upload_to="orders/photos/")),
                ("description", models.CharField(blank=True, max_length=255)),
                (
                    "materials",
                    models.ManyToManyField(blank=True, related_name="order_photos", to="core.material"),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="core.productionorder",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_order_photos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("operator", "Operativo"),
                            ("administrative", "Administrativo"),
                            ("admin", "Administrador"),
                        ],
                        default="operator",
                        max_length=20,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de usuario",
                "verbose_name_plural": "Perfiles de usuario",
            },
        ),
    ]
