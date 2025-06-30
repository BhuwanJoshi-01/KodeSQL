from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from courses.models import Course, CourseModule, CourseLesson, UserCourseEnrollment
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample courses for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample courses...')
        
        # Get or create an instructor user
        instructor, created = User.objects.get_or_create(
            email='instructor@example.com',
            defaults={
                'username': 'instructor',
                'first_name': 'Vijay',
                'last_name': 'Pratap',
                'is_staff': True,
            }
        )
        
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write(f'Created instructor user: {instructor.email}')
        
        # Sample courses data
        courses_data = [
            {
                'title': 'SQL Fundamentals',
                'short_description': 'Learn the basics of SQL including queries, joins, and database management. Perfect for beginners.',
                'description': '''
                <h3>Course Overview</h3>
                <p>This comprehensive course covers all the fundamental concepts of SQL (Structured Query Language). You'll learn how to write queries, manipulate data, and understand database relationships.</p>
                
                <h3>What You'll Learn</h3>
                <ul>
                    <li>Basic SQL syntax and commands</li>
                    <li>Data retrieval with SELECT statements</li>
                    <li>Filtering and sorting data</li>
                    <li>Working with multiple tables using JOINs</li>
                    <li>Data manipulation (INSERT, UPDATE, DELETE)</li>
                    <li>Database design principles</li>
                </ul>
                ''',
                'difficulty': 'beginner',
                'course_type': 'free',
                'price': Decimal('0.00'),
                'duration_hours': 10,
                'category': 'Database',
                'tags': 'sql, database, beginner, fundamentals',
                'modules': [
                    {
                        'title': 'Introduction to Databases',
                        'description': 'Understanding what databases are and why we need them.',
                        'lessons': [
                            {
                                'title': 'What is a Database?',
                                'content': '<p>Learn about databases, tables, and basic concepts.</p>',
                                'lesson_type': 'text',
                                'duration_minutes': 15,
                            },
                            {
                                'title': 'SQL Overview',
                                'content': '<p>Introduction to SQL and its importance.</p>',
                                'lesson_type': 'video',
                                'duration_minutes': 20,
                            }
                        ]
                    },
                    {
                        'title': 'Basic Queries',
                        'description': 'Learn to write your first SQL queries.',
                        'lessons': [
                            {
                                'title': 'SELECT Statement',
                                'content': '<p>Learn the SELECT statement to retrieve data.</p>',
                                'lesson_type': 'interactive',
                                'duration_minutes': 30,
                                'example_query': 'SELECT * FROM customers;',
                            },
                            {
                                'title': 'WHERE Clause',
                                'content': '<p>Filter data using WHERE conditions.</p>',
                                'lesson_type': 'interactive',
                                'duration_minutes': 25,
                                'example_query': 'SELECT * FROM customers WHERE country = "USA";',
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Advanced SQL Techniques',
                'short_description': 'Master advanced SQL concepts including window functions, CTEs, and performance optimization.',
                'description': '''
                <h3>Course Overview</h3>
                <p>Take your SQL skills to the next level with advanced techniques used by professional data analysts and database developers.</p>
                
                <h3>Prerequisites</h3>
                <p>Basic knowledge of SQL fundamentals is required.</p>
                ''',
                'difficulty': 'advanced',
                'course_type': 'paid',
                'price': Decimal('49.99'),
                'duration_hours': 15,
                'category': 'Database',
                'tags': 'sql, advanced, window functions, cte, optimization',
                'modules': [
                    {
                        'title': 'Window Functions',
                        'description': 'Learn powerful window functions for advanced analytics.',
                        'lessons': [
                            {
                                'title': 'Introduction to Window Functions',
                                'content': '<p>Understanding window functions and their use cases.</p>',
                                'lesson_type': 'video',
                                'duration_minutes': 25,
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'SQL for Data Science',
                'short_description': 'Learn how to use SQL for data analysis, data cleaning, and preparing data for machine learning.',
                'description': '''
                <h3>Course Overview</h3>
                <p>This course focuses on using SQL specifically for data science tasks, including data exploration, cleaning, and analysis.</p>
                ''',
                'difficulty': 'intermediate',
                'course_type': 'paid',
                'price': Decimal('39.99'),
                'discount_price': Decimal('29.99'),
                'duration_hours': 12,
                'category': 'Data Science',
                'tags': 'sql, data science, analytics, machine learning',
                'modules': [
                    {
                        'title': 'Data Exploration with SQL',
                        'description': 'Explore and understand your data using SQL.',
                        'lessons': [
                            {
                                'title': 'Exploratory Data Analysis',
                                'content': '<p>Learn techniques for exploring data with SQL.</p>',
                                'lesson_type': 'interactive',
                                'duration_minutes': 35,
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Create courses
        for course_data in courses_data:
            modules_data = course_data.pop('modules', [])
            
            course, created = Course.objects.get_or_create(
                slug=slugify(course_data['title']),
                defaults={
                    **course_data,
                    'instructor': instructor,
                    'status': 'published',
                    'is_featured': True,
                }
            )
            
            if created:
                self.stdout.write(f'Created course: {course.title}')
                
                # Create modules and lessons
                for module_order, module_data in enumerate(modules_data):
                    lessons_data = module_data.pop('lessons', [])
                    
                    module = CourseModule.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data.get('description', ''),
                        order=module_order,
                    )
                    
                    for lesson_order, lesson_data in enumerate(lessons_data):
                        CourseLesson.objects.create(
                            module=module,
                            title=lesson_data['title'],
                            content=lesson_data['content'],
                            lesson_type=lesson_data.get('lesson_type', 'text'),
                            duration_minutes=lesson_data.get('duration_minutes', 0),
                            example_query=lesson_data.get('example_query', ''),
                            order=lesson_order,
                        )
                    
                    self.stdout.write(f'  Created module: {module.title} with {len(lessons_data)} lessons')
            else:
                self.stdout.write(f'Course already exists: {course.title}')
        
        self.stdout.write(self.style.SUCCESS('Sample courses created successfully!'))
        self.stdout.write('You can now visit /courses/ to see the courses.')
