from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Migrate existing challenges to use the simplified database schema system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes'
        )
        parser.add_argument(
            '--challenge-id',
            type=int,
            help='Migrate specific challenge by ID'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        challenge_id = options.get('challenge_id')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Migrating challenges to simplified database schema system...')
        
        # Filter challenges
        if challenge_id:
            challenges = Challenge.objects.filter(id=challenge_id)
            if not challenges.exists():
                self.stdout.write(
                    self.style.ERROR(f'Challenge with ID {challenge_id} not found.')
                )
                return
        else:
            challenges = Challenge.objects.all()
        
        migrated_count = 0
        
        for challenge in challenges:
            old_schema_type = getattr(challenge, 'database_schema_type', None)
            
            # Set default supported engines if empty
            if not challenge.supported_engines:
                if not dry_run:
                    challenge.supported_engines = ['sqlite', 'postgresql', 'mysql']
                self.stdout.write(f'  Setting default supported engines for: {challenge.title}')
            
            # Determine schema type based on existing data
            schema_type_changed = False
            
            # Check if challenge already has the new schema type field
            if not old_schema_type:
                # Determine schema type from content
                if hasattr(challenge, 'initialization_sql') and challenge.initialization_sql:
                    init_sql_lower = challenge.initialization_sql.lower()
                    
                    if 'employees' in init_sql_lower and 'department' in init_sql_lower:
                        new_schema_type = 'employees'
                    elif 'orders' in init_sql_lower or 'returns' in init_sql_lower:
                        new_schema_type = 'ecommerce'
                    else:
                        new_schema_type = 'custom'
                        # Preserve existing custom data
                        if not dry_run:
                            challenge.custom_initialization_sql = challenge.initialization_sql
                            if hasattr(challenge, 'database_schema') and challenge.database_schema:
                                challenge.custom_database_schema = challenge.database_schema
                else:
                    new_schema_type = 'employees'  # Default
                
                if not dry_run:
                    challenge.database_schema_type = new_schema_type
                
                schema_type_changed = True
                self.stdout.write(f'  Setting schema type to "{new_schema_type}" for: {challenge.title}')
            
            if schema_type_changed or not challenge.supported_engines:
                if not dry_run:
                    challenge.save()
                migrated_count += 1
                
                self.stdout.write(f'✅ Migrated challenge: {challenge.title}')
                if old_schema_type != getattr(challenge, 'database_schema_type', None):
                    self.stdout.write(f'   Schema type: {old_schema_type or "None"} → {getattr(challenge, "database_schema_type", "employees")}')
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would migrate {migrated_count} challenge(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully migrated {migrated_count} challenge(s)')
            )
            
            # Show summary of schema types
            self.stdout.write('\nSchema type distribution:')
            for schema_type, name in Challenge.DATABASE_SCHEMA_CHOICES:
                count = Challenge.objects.filter(database_schema_type=schema_type).count()
                self.stdout.write(f'  {name}: {count} challenges')
