from django.core.management.base import BaseCommand
from django.conf import settings
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Show available database schemas and their usage'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Database Schema Configuration ===\n'))
        
        # Show available schemas from settings
        schemas = getattr(settings, 'CHALLENGE_DATABASE_SCHEMAS', {})
        
        self.stdout.write('Available Predefined Schemas:')
        for schema_key, schema_config in schemas.items():
            self.stdout.write(f'  • {schema_key}: {schema_config.get("name", "Unknown")}')
            self.stdout.write(f'    Description: {schema_config.get("description", "No description")}')
            
            # Show tables in this schema
            schema_data = schema_config.get('schema', {})
            tables = schema_data.get('tables', {})
            if tables:
                self.stdout.write(f'    Tables: {", ".join(tables.keys())}')
            self.stdout.write('')
        
        # Show usage statistics
        self.stdout.write('Schema Usage by Challenges:')
        for choice_key, choice_label in Challenge.DATABASE_SCHEMA_CHOICES:
            count = Challenge.objects.filter(database_schema_type=choice_key).count()
            self.stdout.write(f'  • {choice_label}: {count} challenge(s)')
        
        self.stdout.write(f'\nTotal Challenges: {Challenge.objects.count()}')
        
        # Show supported engines
        self.stdout.write('\nSupported Database Engines:')
        for engine_key, engine_label in Challenge.DATABASE_ENGINE_CHOICES:
            self.stdout.write(f'  • {engine_label} ({engine_key})')
        
        self.stdout.write(self.style.SUCCESS('\n=== Configuration Location ==='))
        self.stdout.write('Database schemas are configured in: sqlplayground/settings.py')
        self.stdout.write('Look for: CHALLENGE_DATABASE_SCHEMAS')
