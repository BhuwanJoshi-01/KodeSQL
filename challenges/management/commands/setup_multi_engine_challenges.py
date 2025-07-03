from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = 'Setup multi-database engine support for existing challenges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--engines',
            nargs='+',
            default=['sqlite', 'postgresql', 'mysql'],
            help='List of database engines to support (default: sqlite postgresql mysql)'
        )
        parser.add_argument(
            '--challenge-id',
            type=int,
            help='Update specific challenge by ID'
        )

    def handle(self, *args, **options):
        engines = options['engines']
        challenge_id = options.get('challenge_id')
        
        self.stdout.write('Setting up multi-database engine support...')
        
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
        
        updated_count = 0
        
        for challenge in challenges:
            # Set supported engines
            challenge.supported_engines = engines
            
            # Create engine-specific SQL if needed
            if challenge.initialization_sql and not challenge.engine_specific_sql:
                challenge.engine_specific_sql = self._create_engine_specific_sql(
                    challenge.initialization_sql, engines
                )
            
            challenge.save()
            updated_count += 1
            
            self.stdout.write(f'✅ Updated challenge: {challenge.title}')
            self.stdout.write(f'   Supported engines: {", ".join(engines)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} challenge(s)')
        )

    def _create_engine_specific_sql(self, base_sql, engines):
        """
        Create engine-specific SQL variations from base SQL.
        """
        engine_sql = {}
        
        for engine in engines:
            if engine == 'sqlite':
                engine_sql[engine] = base_sql
            elif engine == 'postgresql':
                engine_sql[engine] = self._adapt_sql_for_postgresql(base_sql)
            elif engine == 'mysql':
                engine_sql[engine] = self._adapt_sql_for_mysql(base_sql)
        
        return engine_sql

    def _adapt_sql_for_postgresql(self, sql):
        """
        Adapt SQLite SQL for PostgreSQL.
        """
        # Common SQLite to PostgreSQL conversions
        adaptations = [
            ('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY'),
            ('DATETIME DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT TRUE'),
            ('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT FALSE'),
            ('TEXT', 'VARCHAR(255)'),
        ]
        
        adapted_sql = sql
        for sqlite_syntax, postgres_syntax in adaptations:
            adapted_sql = adapted_sql.replace(sqlite_syntax, postgres_syntax)
        
        return adapted_sql

    def _adapt_sql_for_mysql(self, sql):
        """
        Adapt SQLite SQL for MySQL.
        """
        # Common SQLite to MySQL conversions
        adaptations = [
            ('INTEGER PRIMARY KEY AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY'),
            ('DATETIME DEFAULT CURRENT_TIMESTAMP', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT TRUE'),
            ('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT FALSE'),
        ]
        
        adapted_sql = sql
        for sqlite_syntax, mysql_syntax in adaptations:
            adapted_sql = adapted_sql.replace(sqlite_syntax, mysql_syntax)
        
        return adapted_sql
