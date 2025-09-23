from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productionorderitem",
            name="custom_description",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Descripción personalizada",
            ),
        ),
        migrations.AlterField(
            model_name="productionorder",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="core.client",
            ),
        ),
    ]
