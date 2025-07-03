# Generated manually to migrate existing challenges to simplified schema system

from django.db import migrations


def migrate_challenges_to_simplified_schema(apps, schema_editor):
    """
    Migrate existing challenges to use the new simplified schema system.
    """
    Challenge = apps.get_model('challenges', 'Challenge')
    
    for challenge in Challenge.objects.all():
        # Set default supported engines if empty
        if not challenge.supported_engines:
            challenge.supported_engines = ['sqlite', 'postgresql', 'mysql']
        
        # Determine schema type based on existing data
        if hasattr(challenge, 'initialization_sql') and challenge.initialization_sql:
            # Check if it's an employee schema
            if 'employees' in challenge.initialization_sql.lower():
                challenge.database_schema_type = 'employees'
            # Check if it's an ecommerce schema
            elif 'orders' in challenge.initialization_sql.lower() or 'returns' in challenge.initialization_sql.lower():
                challenge.database_schema_type = 'ecommerce'
            else:
                # Custom schema - preserve existing data
                challenge.database_schema_type = 'custom'
                challenge.custom_initialization_sql = challenge.initialization_sql
                if hasattr(challenge, 'database_schema') and challenge.database_schema:
                    challenge.custom_database_schema = challenge.database_schema
        else:
            # Default to employee schema
            challenge.database_schema_type = 'employees'
        
        challenge.save()


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - restore old fields from new ones.
    """
    Challenge = apps.get_model('challenges', 'Challenge')
    
    for challenge in Challenge.objects.all():
        if challenge.database_schema_type == 'custom':
            # Restore custom data to old fields
            if hasattr(challenge, 'custom_initialization_sql'):
                challenge.initialization_sql = challenge.custom_initialization_sql
            if hasattr(challenge, 'custom_database_schema'):
                challenge.database_schema = challenge.custom_database_schema
        
        challenge.save()


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0009_simplify_database_schema'),
    ]

    operations = [
        migrations.RunPython(
            migrate_challenges_to_simplified_schema,
            reverse_migration,
        ),
    ]
