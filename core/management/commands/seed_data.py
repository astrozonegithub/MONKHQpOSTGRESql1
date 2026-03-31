from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from core.models import Service, Project, Testimonial, Contact, Software


class Command(BaseCommand):
    help = 'Seed the database with initial data for MonkHQ website'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Clear existing data
        Service.objects.all().delete()
        Project.objects.all().delete()
        Testimonial.objects.all().delete()
        Software.objects.all().delete()
        
        # Create Services
        services = [
            {
                'title': 'Brand Strategy',
                'description': 'Comprehensive brand development and positioning strategies that resonate with your target audience and drive market growth.',
                'icon': 'fa-lightbulb',
                'order': 1
            },
            {
                'title': 'Digital Design',
                'description': 'Stunning visual experiences crafted with precision and creativity to captivate your audience across all digital platforms.',
                'icon': 'fa-palette',
                'order': 2
            },
            {
                'title': 'Web Development',
                'description': 'Custom web applications built with cutting-edge technology and best practices for optimal performance and user experience.',
                'icon': 'fa-code',
                'order': 3
            },
            {
                'title': 'Marketing Campaigns',
                'description': 'Data-driven marketing campaigns that deliver measurable results and maximize your return on investment.',
                'icon': 'fa-bullhorn',
                'order': 4
            },
            {
                'title': 'Content Strategy',
                'description': 'Strategic content creation and distribution that builds brand authority and engages your target audience.',
                'icon': 'fa-pen-nib',
                'order': 5
            },
            {
                'title': 'Analytics & SEO',
                'description': 'Comprehensive analytics and SEO optimization to improve visibility and drive organic traffic to your digital assets.',
                'icon': 'fa-chart-line',
                'order': 6
            }
        ]
        
        for service_data in services:
            Service.objects.create(**service_data)
        
        # Create Projects
        projects = [
            {
                'title': 'TechStart Rebranding',
                'description': 'Complete brand transformation for a leading fintech startup, including visual identity, messaging, and digital presence.',
                'client': 'TechStart Inc.',
                'completed_date': date.today() - timedelta(days=45),
                'image_url': 'https://picsum.photos/seed/techstart/600/400.jpg',
                'featured': True,
                'order': 1
            },
            {
                'title': 'ECommerce Platform',
                'description': 'Full-stack development of a scalable e-commerce platform with advanced features and seamless user experience.',
                'client': 'Luxury Goods Co.',
                'completed_date': date.today() - timedelta(days=90),
                'image_url': 'https://picsum.photos/seed/ecommerce/600/400.jpg',
                'featured': True,
                'order': 2
            },
            {
                'title': 'SaaS Dashboard',
                'description': 'Analytics dashboard for a B2B SaaS platform with real-time data visualization and reporting capabilities.',
                'client': 'DataFlow Analytics',
                'completed_date': date.today() - timedelta(days=210),
                'image_url': 'https://picsum.photos/seed/saas/600/400.jpg',
                'featured': False,
                'order': 3
            },
            {
                'title': 'Restaurant Chain Website',
                'description': 'Multi-location restaurant website with online ordering, reservation system, and location finder.',
                'client': 'Gourmet Group',
                'completed_date': date.today() - timedelta(days=270),
                'image_url': 'https://picsum.photos/seed/restaurant/600/400.jpg',
                'featured': False,
                'order': 4
            }
        ]
        
        for project_data in projects:
            Project.objects.create(**project_data)
        
        # Create Testimonials
        testimonials = [
            {
                'client_name': 'Sarah Johnson',
                'company': 'TechStart Inc.',
                'content': 'MonkHQ transformed our brand identity completely. Their strategic approach and creative execution exceeded all our expectations. We\'ve seen a 300% increase in brand recognition since launch.',
                'rating': 5,
                'featured': True,
                'order': 1
            },
            {
                'client_name': 'Michael Chen',
                'company': 'Luxury Goods Co.',
                'content': 'The e-commerce platform MonkHQ built for us is exceptional. Sales increased by 150% in the first quarter, and customer satisfaction scores are at an all-time high.',
                'rating': 5,
                'featured': True,
                'order': 2
            }
        ]
        
        for testimonial_data in testimonials:
            Testimonial.objects.create(**testimonial_data)
        
        # Create Software
        software_list = [
            {
                'title': 'AI Content Generator',
                'description': 'Advanced AI-powered content generation tool that creates high-quality blog posts, social media content, and marketing copy in seconds.',
                'category': 'Content Marketing',
                'version': '2.1.0',
                'developer': 'MonkHQ Labs',
                'price': 49.99,
                'image_url': 'https://picsum.photos/seed/aicontent/400/300.jpg',
                'download_url': 'https://example.com/download/aicontent',
                'features': 'AI-powered writing\nMultiple content types\nSEO optimization\nBrand voice customization\nBulk generation',
                'system_requirements': 'Windows 10+ / macOS 10.14+\n4GB RAM\n500MB storage\nInternet connection',
                'featured': True,
                'is_free': False,
                'order': 1
            },
            {
                'title': 'Smart Analytics Pro',
                'description': 'Comprehensive analytics platform powered by AI that provides deep insights into your business performance and customer behavior.',
                'category': 'Analytics',
                'version': '1.5.2',
                'developer': 'MonkHQ Analytics',
                'price': 99.99,
                'image_url': 'https://picsum.photos/seed/analytics/400/300.jpg',
                'download_url': 'https://example.com/download/analytics',
                'features': 'Real-time dashboards\nPredictive analytics\nCustom reports\nData visualization\nAI insights',
                'system_requirements': 'Windows 10+ / macOS 10.14+ / Linux\n8GB RAM\n2GB storage\nInternet connection',
                'featured': True,
                'is_free': False,
                'order': 2
            },
            {
                'title': 'Social Media Scheduler',
                'description': 'AI-driven social media management tool that optimizes posting schedules and content for maximum engagement.',
                'category': 'Social Media',
                'version': '3.0.1',
                'developer': 'MonkHQ Social',
                'price': 0.00,
                'image_url': 'https://picsum.photos/seed/social/400/300.jpg',
                'download_url': 'https://example.com/download/social',
                'features': 'Multi-platform support\nAI scheduling\nContent suggestions\nAnalytics dashboard\nTeam collaboration',
                'system_requirements': 'Windows 8+ / macOS 10.12+\n2GB RAM\n200MB storage\nInternet connection',
                'featured': True,
                'is_free': True,
                'order': 3
            },
            {
                'title': 'SEO Optimizer',
                'description': 'Intelligent SEO optimization tool that analyzes your website and provides actionable recommendations to improve search rankings.',
                'category': 'SEO Tools',
                'version': '1.2.0',
                'developer': 'MonkHQ SEO',
                'price': 29.99,
                'image_url': 'https://picsum.photos/seed/seo/400/300.jpg',
                'download_url': 'https://example.com/download/seo',
                'features': 'Site analysis\nKeyword research\nCompetitor analysis\nRank tracking\nAI recommendations',
                'system_requirements': 'Windows 10+ / macOS 10.14+\n4GB RAM\n1GB storage\nInternet connection',
                'featured': False,
                'is_free': False,
                'order': 4
            },
            {
                'title': 'Email Marketing Automation',
                'description': 'Advanced email marketing platform with AI-powered personalization and automation features.',
                'category': 'Email Marketing',
                'version': '2.3.1',
                'developer': 'MonkHQ Email',
                'price': 79.99,
                'image_url': 'https://picsum.photos/seed/email/400/300.jpg',
                'download_url': 'https://example.com/download/email',
                'features': 'AI personalization\nAutomation workflows\nA/B testing\nAdvanced analytics\nTemplate library',
                'system_requirements': 'Windows 10+ / macOS 10.14+\n4GB RAM\n500MB storage\nInternet connection',
                'featured': False,
                'is_free': False,
                'order': 5
            },
            {
                'title': 'Customer Support Chatbot',
                'description': 'AI-powered customer support chatbot that handles inquiries 24/7 and integrates with your existing systems.',
                'category': 'Customer Support',
                'version': '1.8.0',
                'developer': 'MonkHQ Support',
                'price': 0.00,
                'image_url': 'https://picsum.photos/seed/chatbot/400/300.jpg',
                'download_url': 'https://example.com/download/chatbot',
                'features': '24/7 availability\nNatural language processing\nMulti-language support\nCRM integration\nAnalytics dashboard',
                'system_requirements': 'Windows 8+ / macOS 10.12+ / Linux\n2GB RAM\n300MB storage\nInternet connection',
                'featured': False,
                'is_free': True,
                'order': 6
            }
        ]
        
        for software_data in software_list:
            Software.objects.create(**software_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded data!'))
