from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('website-development/', views.website_development_view, name='website_development'),
    path('influencer-marketing/', views.influencer_marketing_view, name='influencer_marketing'),
    path('ai-agent/', views.ai_agent_view, name='ai_agent'),
    path('software-store/', views.software_store_view, name='software_store'),
    path('contact/', views.contact_view, name='contact'),
]
