# Generated by Django 4.2.5 on 2023-09-12 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_review_updated_alter_product_updated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
