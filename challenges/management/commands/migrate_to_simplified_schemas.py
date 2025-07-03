from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Migrate existing challenges to use simplified schema system'

    def handle(self, *args, **options):
        self.stdout.write('Migrating challenges to simplified schema system...')
        
        updated_count = 0
        
        for challenge in Challenge.objects.all():
            # Determine appropriate schema type based on existing data
            schema_type = self._determine_schema_type(challenge)
            
            if schema_type != challenge.database_schema_type:
                challenge.database_schema_type = schema_type
                challenge.save()
                updated_count += 1
                self.stdout.write(f'✅ Updated challenge "{challenge.title}" to use "{schema_type}" schema')
            else:
                self.stdout.write(f'⏭️  Challenge "{challenge.title}" already using correct schema type')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {updated_count} challenge(s)')
        )

    def _determine_schema_type(self, challenge):
        """
        Determine the appropriate schema type based on challenge content.
        """
        title_lower = challenge.title.lower()
        query_lower = challenge.expected_query.lower()
        
        # Check for e-commerce related keywords
        ecommerce_keywords = ['order', 'return', 'customer', 'sales', 'purchase']
        if any(keyword in title_lower or keyword in query_lower for keyword in ecommerce_keywords):
            return 'ecommerce'
        
        # Check for student/academic related keywords
        student_keywords = ['student', 'course', 'enrollment', 'grade', 'class', 'academic']
        if any(keyword in title_lower or keyword in query_lower for keyword in student_keywords):
            return 'students'
        
        # Check if it has custom schema data
        if hasattr(challenge, 'custom_database_schema') and challenge.custom_database_schema:
            return 'custom'
        
        # Default to employees schema
        return 'employees'
