# Generated migration for ChallengeTable model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(help_text='Original table name (will be auto-prefixed with challenge ID for isolation)', max_length=100)),
                ('schema_sql', models.TextField(help_text='CREATE TABLE statement for this table')),
                ('run_dataset_sql', models.TextField(help_text='INSERT statements for test/trial data (users see this during testing)')),
                ('submit_dataset_sql', models.TextField(help_text='INSERT statements for validation data (hidden test cases for final submission)')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order in admin')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='challenges.challenge')),
            ],
            options={
                'ordering': ['order', 'table_name'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='challengetable',
            unique_together={('challenge', 'table_name')},
        ),
    ]
