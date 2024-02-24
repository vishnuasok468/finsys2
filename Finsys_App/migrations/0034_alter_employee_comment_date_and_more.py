# Generated by Django 4.2.3 on 2024-02-24 06:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Finsys_App', '0033_rename_fin_attendance_fin_attendances'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee_comment',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 24)),
        ),
        migrations.AlterField(
            model_name='holiday_comment',
            name='date',
            field=models.DateField(default=datetime.date(2024, 2, 24)),
        ),
        migrations.CreateModel(
            name='Fin_Attendance_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('action', models.CharField(max_length=100)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_attendances')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_company_details')),
                ('login_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Finsys_App.fin_login_details')),
            ],
        ),
    ]