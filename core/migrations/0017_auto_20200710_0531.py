# Generated by Django 2.2.13 on 2020-07-10 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20200709_0607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='party',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidates', to='core.CandidateParty'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='position',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidates', to='core.CandidatePosition'),
        ),
        migrations.AlterField(
            model_name='voterprofile',
            name='batch',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='voter_profiles', to='core.Batch'),
        ),
        migrations.AlterField(
            model_name='voterprofile',
            name='section',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='voter_profiles', to='core.Section'),
        ),
    ]
