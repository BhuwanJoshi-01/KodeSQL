from django.core.management.base import BaseCommand
from challenges.models import Challenge
import random


class Command(BaseCommand):
    help = 'Expand challenge content with more premium challenges and companies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of new challenges to create (default: 20)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(f'Creating {count} new premium challenges...')
        
        # Create new challenges
        created_count = self.create_premium_challenges(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new challenges!')
        )

    def create_premium_challenges(self, count):
        """Create premium challenges with realistic content"""
        
        companies = [
            'Meta', 'Apple', 'Netflix', 'Google', 'Amazon', 'Microsoft',
            'Tesla', 'Uber', 'Airbnb', 'Spotify', 'LinkedIn', 'Twitter',
            'Salesforce', 'Oracle', 'IBM', 'Adobe', 'Nvidia', 'Intel',
            'Cisco', 'VMware', 'Snowflake', 'Databricks', 'Palantir',
            'Stripe', 'Square', 'PayPal', 'Zoom', 'Slack', 'Dropbox',
            'Reddit', 'Pinterest', 'Snapchat', 'TikTok', 'Discord'
        ]
        
        challenge_templates = [
            {
                'title': 'User Engagement Analytics',
                'description': 'Analyze user engagement metrics to identify patterns in user behavior and calculate retention rates.',
                'question': 'Write a query to find the top 10 users with the highest engagement score in the last 30 days.',
                'difficulty': 'medium',
                'tags': ['analytics', 'aggregation', 'window-functions'],
                'expected_query': 'SELECT user_id, SUM(engagement_score) as total_score FROM user_activities WHERE activity_date >= CURRENT_DATE - INTERVAL 30 DAY GROUP BY user_id ORDER BY total_score DESC LIMIT 10;'
            },
            {
                'title': 'Revenue Growth Analysis',
                'description': 'Calculate month-over-month revenue growth and identify trends in business performance.',
                'question': 'Find the month-over-month revenue growth percentage for each product category.',
                'difficulty': 'hard',
                'tags': ['analytics', 'window-functions', 'aggregation'],
                'expected_query': 'SELECT category, month, revenue, LAG(revenue) OVER (PARTITION BY category ORDER BY month) as prev_revenue, ((revenue - LAG(revenue) OVER (PARTITION BY category ORDER BY month)) / LAG(revenue) OVER (PARTITION BY category ORDER BY month)) * 100 as growth_rate FROM monthly_revenue ORDER BY category, month;'
            },
            {
                'title': 'Customer Churn Prediction',
                'description': 'Identify customers at risk of churning based on their activity patterns and subscription history.',
                'question': 'Find customers who haven\'t made any purchases in the last 60 days but were active in the previous 90 days.',
                'difficulty': 'hard',
                'tags': ['analytics', 'subqueries', 'date-functions'],
                'expected_query': 'SELECT DISTINCT c.customer_id, c.email FROM customers c WHERE c.customer_id NOT IN (SELECT customer_id FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL 60 DAY) AND c.customer_id IN (SELECT customer_id FROM orders WHERE order_date BETWEEN CURRENT_DATE - INTERVAL 150 DAY AND CURRENT_DATE - INTERVAL 60 DAY);'
            },
            {
                'title': 'Inventory Optimization',
                'description': 'Optimize inventory levels by analyzing sales patterns and identifying slow-moving products.',
                'question': 'Find products that have less than 10 units sold in the last quarter but have more than 100 units in stock.',
                'difficulty': 'medium',
                'tags': ['inventory', 'aggregation', 'joins'],
                'expected_query': 'SELECT p.product_id, p.product_name, p.stock_quantity, COALESCE(SUM(oi.quantity), 0) as units_sold FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_date >= CURRENT_DATE - INTERVAL 3 MONTH GROUP BY p.product_id, p.product_name, p.stock_quantity HAVING units_sold < 10 AND p.stock_quantity > 100;'
            },
            {
                'title': 'Social Media Metrics',
                'description': 'Calculate engagement rates and viral coefficients for social media posts.',
                'question': 'Find posts with engagement rate above 5% and calculate their viral coefficient.',
                'difficulty': 'hard',
                'tags': ['social-media', 'analytics', 'aggregation'],
                'expected_query': 'SELECT post_id, (likes + comments + shares) / CAST(impressions AS FLOAT) * 100 as engagement_rate, shares / CAST(impressions AS FLOAT) as viral_coefficient FROM posts WHERE (likes + comments + shares) / CAST(impressions AS FLOAT) * 100 > 5 ORDER BY engagement_rate DESC;'
            },
            {
                'title': 'A/B Test Analysis',
                'description': 'Analyze A/B test results to determine statistical significance and conversion rates.',
                'question': 'Compare conversion rates between control and test groups for the latest experiment.',
                'difficulty': 'medium',
                'tags': ['ab-testing', 'analytics', 'aggregation'],
                'expected_query': 'SELECT experiment_group, COUNT(*) as total_users, SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions, SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) / CAST(COUNT(*) AS FLOAT) * 100 as conversion_rate FROM ab_test_results WHERE experiment_id = (SELECT MAX(experiment_id) FROM ab_test_results) GROUP BY experiment_group;'
            },
            {
                'title': 'Supply Chain Optimization',
                'description': 'Optimize supply chain by analyzing supplier performance and delivery times.',
                'question': 'Find suppliers with average delivery time less than 5 days and 95%+ on-time delivery rate.',
                'difficulty': 'medium',
                'tags': ['supply-chain', 'aggregation', 'analytics'],
                'expected_query': 'SELECT supplier_id, AVG(delivery_days) as avg_delivery, SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) / CAST(COUNT(*) AS FLOAT) * 100 as on_time_rate FROM deliveries GROUP BY supplier_id HAVING avg_delivery < 5 AND on_time_rate >= 95 ORDER BY on_time_rate DESC, avg_delivery ASC;'
            },
            {
                'title': 'Fraud Detection System',
                'description': 'Identify potentially fraudulent transactions based on unusual patterns.',
                'question': 'Find transactions that are 3x higher than the user\'s average transaction amount in the last 30 days.',
                'difficulty': 'hard',
                'tags': ['fraud-detection', 'window-functions', 'subqueries'],
                'expected_query': 'WITH user_avg AS (SELECT user_id, AVG(amount) as avg_amount FROM transactions WHERE transaction_date >= CURRENT_DATE - INTERVAL 30 DAY GROUP BY user_id) SELECT t.transaction_id, t.user_id, t.amount, ua.avg_amount FROM transactions t JOIN user_avg ua ON t.user_id = ua.user_id WHERE t.amount > ua.avg_amount * 3 AND t.transaction_date >= CURRENT_DATE - INTERVAL 30 DAY;'
            },
            {
                'title': 'Recommendation Engine Data',
                'description': 'Prepare data for recommendation algorithms by analyzing user preferences and item similarities.',
                'question': 'Find users who have similar purchase patterns to a given user based on product categories.',
                'difficulty': 'hard',
                'tags': ['recommendations', 'joins', 'aggregation'],
                'expected_query': 'WITH user_categories AS (SELECT user_id, category_id, COUNT(*) as purchase_count FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id GROUP BY user_id, category_id) SELECT uc1.user_id as similar_user FROM user_categories uc1 JOIN user_categories uc2 ON uc1.category_id = uc2.category_id WHERE uc2.user_id = ? AND uc1.user_id != ? GROUP BY uc1.user_id HAVING COUNT(DISTINCT uc1.category_id) >= 3;'
            },
            {
                'title': 'Performance Monitoring',
                'description': 'Monitor application performance by analyzing response times and error rates.',
                'question': 'Find API endpoints with 95th percentile response time above 2 seconds in the last hour.',
                'difficulty': 'hard',
                'tags': ['performance', 'analytics', 'percentiles'],
                'expected_query': 'SELECT endpoint, PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time FROM api_logs WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR GROUP BY endpoint HAVING p95_response_time > 2000 ORDER BY p95_response_time DESC;'
            }
        ]
        
        created_count = 0
        
        for i in range(count):
            # Select random template and company
            template = random.choice(challenge_templates)
            company = random.choice(companies)
            
            # Create unique title
            title = f"{template['title']} - {company} Interview"
            
            # Check if challenge already exists
            if Challenge.objects.filter(title=title).exists():
                continue
            
            # Create challenge
            challenge = Challenge.objects.create(
                title=title,
                description=template['description'],
                difficulty=template['difficulty'],
                question=template['question'],
                hint=f"Consider using {', '.join(template['tags'][:2])} to solve this problem efficiently.",
                expected_query=template['expected_query'],
                expected_result=[],  # Would be populated with actual test data
                subscription_type='paid',  # All new challenges are premium
                company=company,
                tags=template['tags'],
                is_active=True,
                order=1000 + i  # Place at end
            )
            
            created_count += 1
            self.stdout.write(f'Created: {challenge.title}')
        
        return created_count
