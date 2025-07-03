from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, CourseModule, CourseLesson, LessonResource
from django.utils.text import slugify
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample course data for testing the course watch system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample course data...')
        
        # Get or create instructor
        instructor, created = User.objects.get_or_create(
            email='instructor@example.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Instructor',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write(f'Created instructor: {instructor.email}')
        
        # Create sample course
        course, created = Course.objects.get_or_create(
            slug='sql-fundamentals-course',
            defaults={
                'title': 'SQL Fundamentals: From Beginner to Advanced',
                'short_description': 'Master SQL with hands-on exercises and real-world projects',
                'description': '''
                <h2>Learn SQL from the ground up</h2>
                <p>This comprehensive course will take you from SQL beginner to advanced practitioner. 
                You'll learn through hands-on exercises, real-world examples, and practical projects.</p>
                
                <h3>What you'll learn:</h3>
                <ul>
                    <li>SQL fundamentals and syntax</li>
                    <li>Database design principles</li>
                    <li>Advanced querying techniques</li>
                    <li>Performance optimization</li>
                    <li>Real-world project implementation</li>
                </ul>
                ''',
                'difficulty': 'beginner',
                'course_type': 'free',
                'status': 'published',
                'duration_hours': 12,
                'instructor': instructor,
                'category': 'Database',
                'language': 'English',
                'tags': 'SQL, Database, MySQL, PostgreSQL, Data Analysis',
                'is_featured': True,
                'allow_preview': True,
                'certificate_enabled': True
            }
        )
        
        if created:
            self.stdout.write(f'Created course: {course.title}')
        
        # Create modules
        modules_data = [
            {
                'title': 'Getting Started with SQL',
                'description': 'Introduction to databases and SQL basics',
                'order': 1,
                'lessons': [
                    {
                        'title': 'What is SQL?',
                        'content': '<h3>Introduction to SQL</h3><p>SQL (Structured Query Language) is a programming language designed for managing data in relational databases.</p>',
                        'lesson_type': 'text',
                        'duration_minutes': 15,
                        'order': 1
                    },
                    {
                        'title': 'Setting Up Your Environment',
                        'content': '<h3>Database Setup</h3><p>Learn how to set up your SQL development environment.</p>',
                        'lesson_type': 'video',
                        'duration_minutes': 30,
                        'order': 2,
                        'video_url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY'
                    },
                    {
                        'title': 'Your First SQL Query',
                        'content': '<h3>Writing Your First Query</h3><p>Let\'s write our first SELECT statement.</p>',
                        'lesson_type': 'interactive',
                        'duration_minutes': 20,
                        'order': 3,
                        'example_query': 'SELECT * FROM users;',
                        'expected_output': 'id | name | email\n1  | John | john@example.com\n2  | Jane | jane@example.com'
                    }
                ]
            },
            {
                'title': 'Basic SQL Operations',
                'description': 'Learn fundamental SQL operations',
                'order': 2,
                'lessons': [
                    {
                        'title': 'SELECT Statements',
                        'content': '<h3>The SELECT Statement</h3><p>Master the most important SQL command.</p>',
                        'lesson_type': 'text',
                        'duration_minutes': 25,
                        'order': 1,
                        'example_query': 'SELECT name, email FROM users WHERE age > 18;'
                    },
                    {
                        'title': 'Filtering with WHERE',
                        'content': '<h3>Filtering Data</h3><p>Learn to filter your query results.</p>',
                        'lesson_type': 'video',
                        'duration_minutes': 35,
                        'order': 2
                    },
                    {
                        'title': 'Sorting with ORDER BY',
                        'content': '<h3>Sorting Results</h3><p>Order your query results effectively.</p>',
                        'lesson_type': 'interactive',
                        'duration_minutes': 20,
                        'order': 3,
                        'practice_query': 'SELECT * FROM products ORDER BY price DESC;'
                    }
                ]
            },
            {
                'title': 'Advanced SQL Concepts',
                'description': 'Dive into advanced SQL techniques',
                'order': 3,
                'lessons': [
                    {
                        'title': 'JOINs and Relationships',
                        'content': '<h3>Understanding JOINs</h3><p>Learn to combine data from multiple tables.</p>',
                        'lesson_type': 'text',
                        'duration_minutes': 45,
                        'order': 1
                    },
                    {
                        'title': 'Aggregate Functions',
                        'content': '<h3>Working with Aggregates</h3><p>COUNT, SUM, AVG, and more.</p>',
                        'lesson_type': 'video',
                        'duration_minutes': 40,
                        'order': 2
                    }
                ]
            }
        ]
        
        for module_data in modules_data:
            lessons_data = module_data.pop('lessons')
            
            module, created = CourseModule.objects.get_or_create(
                course=course,
                title=module_data['title'],
                defaults=module_data
            )
            
            if created:
                self.stdout.write(f'  Created module: {module.title}')
            
            # Create lessons
            for lesson_data in lessons_data:
                lesson, created = CourseLesson.objects.get_or_create(
                    module=module,
                    title=lesson_data['title'],
                    defaults=lesson_data
                )
                
                if created:
                    self.stdout.write(f'    Created lesson: {lesson.title}')
                    
                    # Create sample resources for some lessons
                    if lesson.order == 1:  # First lesson in each module
                        resource, created = LessonResource.objects.get_or_create(
                            lesson=lesson,
                            title=f'{lesson.title} - Study Notes',
                            defaults={
                                'description': f'Comprehensive study notes for {lesson.title}',
                                'resource_type': 'pdf',
                                'file_size': 1024 * 500,  # 500KB
                                'is_downloadable': True,
                                'order': 1
                            }
                        )
                        
                        if created:
                            self.stdout.write(f'      Created resource: {resource.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample course: {course.title}\n'
                f'Course URL: /courses/{course.slug}/\n'
                f'Watch URL: /courses/{course.slug}/watch/\n'
                f'Admin URL: /courses/admin/{course.slug}/'
            )
        )
