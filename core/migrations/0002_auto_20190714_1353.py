# Generated by Django 2.2.3 on 2019-07-14 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElectionSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, null=True, verbose_name='date_updated')),
                ('key', models.CharField(default=None, max_length=30, unique=True, verbose_name='key')),
                ('value', models.CharField(blank=True, default=None, max_length=128, null=True, verbose_name='value')),
            ],
            options={
                'verbose_name_plural': 'election settings',
                'verbose_name': 'election setting',
                'ordering': ['key'],
            },
        ),
        migrations.AddField(
            model_name='batch',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date_created'),
        ),
        migrations.AddField(
            model_name='batch',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='date_updated'),
        ),
        migrations.AddField(
            model_name='section',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date_created'),
        ),
        migrations.AddField(
            model_name='section',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='date_updated'),
        ),
        migrations.AddField(
            model_name='user',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='date_created'),
        ),
        migrations.AddField(
            model_name='user',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='date_updated'),
        ),
        migrations.AddIndex(
            model_name='electionsetting',
            index=models.Index(fields=['key'], name='core_electi_key_1a53c9_idx'),
        ),
    ]