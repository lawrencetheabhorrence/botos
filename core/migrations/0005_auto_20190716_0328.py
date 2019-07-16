# Generated by Django 2.2.3 on 2019-07-16 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190715_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, null=True, verbose_name='date_updated')),
                ('key', models.CharField(default=None, max_length=30, unique=True, verbose_name='key')),
                ('value', models.TextField(blank=True, default=None, null=True, verbose_name='value')),
            ],
            options={
                'verbose_name_plural': 'election settings',
                'ordering': ['key'],
                'verbose_name': 'election setting',
            },
        ),
        migrations.DeleteModel(
            name='ElectionSetting',
        ),
        migrations.AddIndex(
            model_name='setting',
            index=models.Index(fields=['key'], name='core_settin_key_53fa74_idx'),
        ),
    ]