# Generated by Django 4.2.3 on 2024-02-24 07:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Finsys_App', '0034_alter_employee_comment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fin_attendance_history',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 24)),
        ),
    ]
