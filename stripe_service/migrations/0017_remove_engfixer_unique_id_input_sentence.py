# Generated by Django 4.1.4 on 2023-08-17 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_service', '0016_alter_engfixer_input_sentence_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='engfixer',
            name='unique_id_input_sentence',
        ),
    ]