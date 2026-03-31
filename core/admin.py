from django.contrib import admin
from .models import Service, Project, Testimonial, Contact, Software


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    search_fields = ['title']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'completed_date', 'featured', 'order']
    list_editable = ['featured', 'order']
    list_filter = ['featured', 'completed_date']
    search_fields = ['title', 'client']
    date_hierarchy = 'completed_date'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'company', 'rating', 'featured', 'order']
    list_editable = ['featured', 'order']
    list_filter = ['rating', 'featured']
    search_fields = ['client_name', 'company']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'service_interest', 'software_interest', 'created_at']
    list_filter = ['service_interest', 'software_interest', 'created_at']
    search_fields = ['name', 'email', 'company']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'developer', 'get_price_display', 'featured', 'is_free', 'order', 'created_at']
    list_editable = ['featured', 'is_free', 'order']
    list_filter = ['category', 'featured', 'is_free', 'created_at']
    search_fields = ['title', 'developer', 'category']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'version', 'developer')
        }),
        ('Pricing', {
            'fields': ('price', 'is_free')
        }),
        ('Media', {
            'fields': ('image_url', 'download_url')
        }),
        ('Details', {
            'fields': ('features', 'system_requirements')
        }),
        ('Settings', {
            'fields': ('featured', 'order', 'created_at', 'updated_at')
        }),
    )
