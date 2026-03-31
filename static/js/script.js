// DOM Elements
const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');
const navLinks = document.querySelectorAll('.nav-link');
const animateOnScroll = document.querySelectorAll('.animate-on-scroll');
const statNumbers = document.querySelectorAll('.stat-number');

// Mobile Navigation Toggle
navToggle.addEventListener('click', () => {
    navToggle.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Software Modal Functions
function openSoftwareModal(softwareTitle) {
    const modal = document.getElementById('software-contact-modal');
    const titleInput = document.getElementById('modal_software');
    const messageInput = document.getElementById('modal_message');
    
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Pre-fill software title
        if (titleInput) {
            titleInput.value = softwareTitle;
        }
        
        // Clear message and focus
        if (messageInput) {
            messageInput.value = '';
            messageInput.focus();
        }
    }
}

function closeSoftwareModal() {
    const modal = document.getElementById('software-contact-modal');
    
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('software-contact-modal');
    if (modal && event.target === modal) {
        closeSoftwareModal();
    }
});

// Close mobile menu when clicking on a link
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navToggle.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Navbar scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Active navigation link highlighting
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 100;
        const sectionId = section.getAttribute('id');
        const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            navLinks.forEach(link => link.classList.remove('active'));
            if (navLink) {
                navLink.classList.add('active');
            }
        }
    });
}

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            
            // Start count-up animation for stats
            if (entry.target.classList.contains('stat-item')) {
                const statNumber = entry.target.querySelector('.stat-number');
                if (statNumber && !statNumber.classList.contains('counted')) {
                    animateCounter(statNumber);
                    statNumber.classList.add('counted');
                }
            }
        }
    });
}, observerOptions);

// Observe all elements with animation classes
animateOnScroll.forEach(element => {
    observer.observe(element);
});

// Count-up animation for statistics
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000; // 2 seconds
    const step = target / (duration / 16); // 60fps
    let current = 0;

    const updateCounter = () => {
        current += step;
        if (current < target) {
            element.textContent = Math.ceil(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };

    updateCounter();
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        if (targetSection) {
            const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Parallax effect for hero graphic elements
const graphicElements = document.querySelectorAll('.graphic-element');

window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;

    graphicElements.forEach((element, index) => {
        const speed = 0.5 + (index * 0.1);
        element.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// Update active nav link on scroll
window.addEventListener('scroll', updateActiveNavLink);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateActiveNavLink();
    
    // Add loading animation to hero elements
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroActions = document.querySelector('.hero-actions');
    const heroVisual = document.querySelector('.hero-visual');
    
    if (heroTitle) heroTitle.classList.add('animate-fade-in');
    if (heroSubtitle) heroSubtitle.classList.add('animate-fade-in-delay');
    if (heroActions) heroActions.classList.add('animate-fade-in-delay-2');
    if (heroVisual) heroVisual.classList.add('animate-fade-in-delay');
    
    // Observe stat items for count-up animation
    statNumbers.forEach(stat => {
        const statItem = stat.closest('.stat-item');
        if (statItem) {
            observer.observe(statItem);
        }
    });
});

// Form validation (if contact form is added later)
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            showError(input, 'This field is required');
            isValid = false;
        } else {
            clearError(input);
        }
    });
    
    return isValid;
}

function showError(input, message) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.classList.add('error');
        let errorElement = formGroup.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            formGroup.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }
}

function clearError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.classList.remove('error');
        const errorElement = formGroup.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Performance optimization for scroll events
const optimizedScroll = debounce(() => {
    updateActiveNavLink();
    
    // Parallax effect
    const scrolled = window.pageYOffset;
    graphicElements.forEach((element, index) => {
        const speed = 0.5 + (index * 0.1);
        element.style.transform = `translateY(${scrolled * speed}px)`;
    });
}, 10);

window.addEventListener('scroll', optimizedScroll);

// Add loading states for buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.classList.contains('btn-primary')) {
            // Add ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });
});

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .form-group.error input,
    .form-group.error textarea {
        border-color: #ef4444;
    }
    
    .error-message {
        color: #ef4444;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
`;
document.head.appendChild(style);
