from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models
from django.utils.timezone import now
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_productionorder_client_add_custom_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="gross_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0"))],
                verbose_name="Importe neto",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="iva_rate",
            field=models.DecimalField(
                choices=[(Decimal("0.21"), "21%"), (Decimal("0.105"), "10,5%")],
                decimal_places=3,
                default=Decimal("0.21"),
                max_digits=4,
                verbose_name="Alícuota de IVA",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="invoice",
            name="iva_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0"))],
                verbose_name="IVA",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="additional_tax_type",
            field=models.CharField(
                choices=[
                    ("none", "Sin percepciones"),
                    ("ib_bsas", "Ing. Brutos Bs. As."),
                    ("ib_caba", "Ing. Brutos CABA"),
                    ("percep_iva", "Percepción de IVA (3%)"),
                ],
                default="none",
                max_length=20,
                verbose_name="Percepción",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="additional_tax_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[MinValueValidator(Decimal("0"))],
                verbose_name="Importe percepciones",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                validators=[MinValueValidator(Decimal("0"))],
                verbose_name="Total factura",
            ),
        ),
        migrations.CreateModel(
            name="AccountingRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "record_type",
                    models.CharField(
                        choices=[
                            ("subdiary_iva", "Subdiario de IVA"),
                            ("ledger", "Mayor"),
                            ("trial_balance", "Sumas y saldos"),
                            ("chart_of_accounts", "Plan de cuentas"),
                        ],
                        max_length=30,
                    ),
                ),
                ("date", models.DateField(default=now)),
                ("description", models.CharField(max_length=255)),
                ("document_number", models.CharField(blank=True, max_length=100)),
                (
                    "debit",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "credit",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounting_records",
                        to="core.client",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accounting_records",
                        to="core.supplier",
                    ),
                ),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
        migrations.CreateModel(
            name="CurrentAccountMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("charge", "Cobro en cuenta corriente"),
                            ("payment", "Pago en cuenta corriente"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date", models.DateField(default=now)),
                ("concept", models.CharField(max_length=255)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="current_account_movements",
                        to="core.client",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="current_account_movements",
                        to="core.supplier",
                    ),
                ),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
        migrations.CreateModel(
            name="Remittance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.CharField(max_length=100)),
                ("date", models.DateField(default=now)),
                ("description", models.TextField(blank=True)),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="remittances",
                        to="core.client",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="remittances",
                        to="core.productionorder",
                    ),
                ),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
    ]
