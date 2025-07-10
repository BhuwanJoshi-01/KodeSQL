"""
Management command to fix column ordering in expected results for all challenges.
"""

from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Fix column ordering in expected results for challenges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--challenge-id',
            type=int,
            help='Fix specific challenge by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        challenge_id = options.get('challenge_id')
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        if challenge_id:
            try:
                challenge = Challenge.objects.get(id=challenge_id)
                self.fix_challenge_column_order(challenge, dry_run)
            except Challenge.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Challenge with ID {challenge_id} does not exist')
                )
                return
        else:
            # Fix all challenges that have reference queries
            challenges = Challenge.objects.filter(reference_query__isnull=False).exclude(reference_query='')
            self.stdout.write(f'Found {challenges.count()} challenges with reference queries')
            
            for challenge in challenges:
                self.fix_challenge_column_order(challenge, dry_run)

        self.stdout.write(self.style.SUCCESS('Column order fix completed!'))
        self.stdout.write('')
        self.stdout.write('💡 Note: All new challenges will automatically have consistent column ordering applied during creation.')

    def fix_challenge_column_order(self, challenge, dry_run=False):
        """Fix column ordering for a specific challenge."""
        self.stdout.write(f'\n🔍 Checking Challenge: {challenge.title} (ID: {challenge.id})')
        
        if not challenge.reference_query:
            self.stdout.write(f'   ⚠️  No reference query, skipping')
            return
        
        if not challenge.expected_result:
            self.stdout.write(f'   ⚠️  No expected results, skipping')
            return
        
        try:
            # Execute the reference query to get current results
            from challenges.utils import execute_dual_dataset_query, normalize_json_result
            
            result = execute_dual_dataset_query(
                challenge=challenge,
                query=challenge.reference_query,
                flag_id=2,  # Submit dataset
                engine='mysql'
            )
            
            if not result['success']:
                self.stdout.write(f'   ❌ Reference query execution failed: {result.get("error")}')
                return
            
            # Get current column order from fresh execution
            current_results = result['results']
            if not current_results:
                self.stdout.write(f'   ⚠️  No results from reference query')
                return
            
            current_columns = list(current_results[0].keys()) if isinstance(current_results[0], dict) else []
            
            # Get stored expected results column order
            stored_expected = challenge.expected_result
            if not stored_expected:
                self.stdout.write(f'   ⚠️  No stored expected results')
                return
            
            stored_columns = list(stored_expected[0].keys()) if isinstance(stored_expected[0], dict) else []
            
            # Compare column orders
            if current_columns == stored_columns:
                self.stdout.write(f'   ✅ Column order is correct: {current_columns}')
                return
            
            self.stdout.write(f'   ❌ Column order mismatch:')
            self.stdout.write(f'      Current:  {current_columns}')
            self.stdout.write(f'      Stored:   {stored_columns}')
            
            if not dry_run:
                # Regenerate expected results with correct column order
                success, message = challenge.execute_reference_query()
                if success:
                    # Verify the fix
                    challenge.refresh_from_db()
                    new_stored = challenge.expected_result
                    new_columns = list(new_stored[0].keys()) if new_stored and isinstance(new_stored[0], dict) else []
                    
                    if new_columns == current_columns:
                        self.stdout.write(f'   ✅ Fixed! New column order: {new_columns}')
                    else:
                        self.stdout.write(f'   ⚠️  Fix incomplete. New order: {new_columns}')
                else:
                    self.stdout.write(f'   ❌ Failed to regenerate: {message}')
            else:
                self.stdout.write(f'   🔧 Would regenerate expected results')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Error: {str(e)}')
