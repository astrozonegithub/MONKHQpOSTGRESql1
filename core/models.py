from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Font Awesome icon class
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.CharField(max_length=100)
    completed_date = models.DateField()
    image_url = models.URLField(max_length=500, blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5)  # 1-5 stars
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.client_name} - {self.company}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    service_interest = models.CharField(max_length=100, blank=True)
    software_interest = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email}"


class Software(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    version = models.CharField(max_length=50, blank=True)
    developer = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image_url = models.URLField(max_length=500, blank=True)
    download_url = models.URLField(max_length=500, blank=True)
    features = models.TextField(blank=True, help_text="Enter features separated by new lines")
    system_requirements = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []
    
    def get_price_display(self):
        """Return formatted price or 'Free'"""
        if self.is_free or self.price == 0:
            return "Free"
        return f"₹{self.price:.2f}"
