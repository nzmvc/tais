# Generated by Django 4.2.17 on 2025-03-31 16:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notification", "0001_initial"),
        ("saas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="readflag",
            name="company",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="saas.company",
            ),
        ),
        migrations.AddField(
            model_name="readflag",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="notification.notification",
                verbose_name="Mesaj",
            ),
        ),
        migrations.AddField(
            model_name="readflag",
            name="recipient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipient_notification",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="company",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="saas.company",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="sender",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sender_notification",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
