# Generated by Django 4.2.17 on 2025-03-31 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("saas", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="orderFormTemplate",
        ),
    ]
