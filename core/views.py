from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Service, Project, Testimonial, Contact, Software


def home_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        software_interest = request.POST.get('software_interest', '')
        message = request.POST.get('message')
        
        if name and email and message:
            # Save contact submission
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
                service_interest=service_interest,
                software_interest=software_interest,
                message=message
            )
            
            # Send email notification (optional)
            try:
                email_body = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nCompany: {company}\nService Interest: {service_interest}'
                if software_interest:
                    email_body += f'\nSoftware Interest: {software_interest}'
                if request_trial:
                    email_body += f'\nTrial Requested: Yes'
                email_body += f'\n\nMessage:\n{message}'
                
                send_mail(
                    f'New Contact Form Submission from {name}',
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except:
                pass  # Continue even if email fails
            
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get all model data
    services = Service.objects.all()
    projects = Project.objects.all()
    testimonials = Testimonial.objects.all()
    
    # Get featured items for highlights
    featured_projects = projects.filter(featured=True)
    featured_testimonials = testimonials.filter(featured=True)
    
    context = {
        'services': services,
        'projects': projects,
        'testimonials': testimonials,
        'featured_projects': featured_projects,
        'featured_testimonials': featured_testimonials,
    }
    
    return render(request, 'core/index.html', context)


def website_development_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        software_interest = request.POST.get('software_interest', '')
        message = request.POST.get('message')
        
        if name and email and message:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
                service_interest=service_interest,
                software_interest=software_interest,
                message=message
            )
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:website_development')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    services = Service.objects.all()
    projects = Project.objects.filter(title__icontains='web') | Project.objects.filter(description__icontains='web')
    
    context = {
        'services': services,
        'projects': projects,
        'page_title': 'Website Development',
        'page_description': 'Custom web applications built with cutting-edge technology and best practices for optimal performance and user experience.',
    }
    
    return render(request, 'core/website_development.html', context)


def influencer_marketing_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        software_interest = request.POST.get('software_interest', '')
        message = request.POST.get('message')
        
        if name and email and message:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
                service_interest=service_interest,
                software_interest=software_interest,
                message=message
            )
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:influencer_marketing')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    services = Service.objects.all()
    testimonials = Testimonial.objects.filter(rating=5)
    
    context = {
        'services': services,
        'testimonials': testimonials,
        'page_title': 'Influencer Marketing',
        'page_description': 'Strategic influencer partnerships that amplify your brand message and drive authentic engagement with your target audience.',
    }
    
    return render(request, 'core/influencer_marketing.html', context)


def ai_agent_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        software_interest = request.POST.get('software_interest', '')
        message = request.POST.get('message')
        
        if name and email and message:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
                service_interest=service_interest,
                software_interest=software_interest,
                message=message
            )
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:ai_agent')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    services = Service.objects.all()
    projects = Project.objects.filter(description__icontains='ai') | Project.objects.filter(description__icontains='automation')
    
    context = {
        'services': services,
        'projects': projects,
        'page_title': 'AI Agent Development',
        'page_description': 'Intelligent AI agents and automation solutions that streamline operations and enhance customer experiences.',
    }
    
    return render(request, 'core/ai_agent.html', context)


def software_store_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        software_interest = request.POST.get('software_interest', '')
        message = request.POST.get('message')
        
        if name and email and message:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone,
                company=company,
                service_interest=service_interest,
                software_interest=software_interest,
                message=message
            )
            messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
            return redirect('core:software_store')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    price_filter = request.GET.get('price', '')
    
    # Filter software based on parameters
    software_list = Software.objects.all()
    
    if search_query:
        software_list = software_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    if category_filter:
        software_list = software_list.filter(category=category_filter)
    
    if price_filter:
        if price_filter == 'free':
            software_list = software_list.filter(is_free=True)
        elif price_filter == 'paid':
            software_list = software_list.filter(is_free=False)
    
    # Get featured software
    featured_software = software_list.filter(featured=True)
    
    # Get categories for filter dropdown and calculate counts
    categories_with_counts = []
    for category in Software.objects.values_list('category', flat=True).distinct():
        count = Software.objects.filter(category=category).count()
        categories_with_counts.append({'name': category, 'count': count})
    
    context = {
        'software_list': software_list,
        'featured_software': featured_software,
        'categories_with_counts': categories_with_counts,
        'search_query': search_query,
        'category_filter': category_filter,
        'price_filter': price_filter,
        'page_title': 'Software Store',
        'page_description': 'Discover and download premium software solutions powered by AI technology for your business and personal needs.',
    }
    
    return render(request, 'core/software_store.html', context)

def contact_view(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')
        service_interest = request.POST.get('service_interest', '')
        message = request.POST.get('message')
        
        # Create contact record
        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            company=company,
            service_interest=service_interest,
            message=message
        )
        
        # Send email notification (optional)
        try:
            email_body = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nCompany: {company}\nService Interest: {service_interest}\n\nMessage:\n{message}'
            
            send_mail(
                f'New Contact Form Submission from {name}',
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except:
            pass
        
        return redirect(reverse('core:contact') + '?success=true')
    
    # Get page data
    context = {
        'services': Service.objects.all(),
        'projects': Project.objects.all(),
        'testimonials': Testimonial.objects.all(),
    }
    
    return render(request, 'core/contact.html', context)
