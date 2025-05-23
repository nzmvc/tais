# Generated by Django 4.2.17 on 2025-03-31 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("message", models.TextField()),
                ("created_date", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ReadFlag",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "read_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Okunma Tarihi"
                    ),
                ),
            ],
        ),
    ]
