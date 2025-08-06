// ProFit Coach Landing Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-out-cubic',
        once: true,
        offset: 100,
        delay: 100
    });

    // Navigation functionality
    initNavigation();
    
    // Contact form functionality
    initContactForm();
    
    // Demo video functionality
    initDemoVideo();
    
    // Smooth scrolling
    initSmoothScrolling();
    
    // Scroll animations
    initScrollAnimations();
    
    // Performance optimizations
    initPerformanceOptimizations();
});

// Navigation Functions
function initNavigation() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Mobile menu toggle
    navToggle.addEventListener('click', function() {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        if (navMenu.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
    });

    // Close menu when clicking on links
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });

    // Active navigation highlight
    updateActiveNavigation();
    window.addEventListener('scroll', updateActiveNavigation);
}

function updateActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.scrollY >= (sectionTop - 200)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Contact Form Functions
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmission);
        
        // Real-time validation
        const inputs = contactForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    }
}

async function handleFormSubmission(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('.submit-btn');
    const btnText = submitBtn.querySelector('span');
    
    // Validate form
    if (!validateForm(form)) {
        showNotification('Por favor, completa todos los campos obligatorios correctamente.', 'error');
        return;
    }
    
    // Show loading state
    showLoadingState(submitBtn, btnText);
    
    try {
        // Prepare email data
        const emailData = {
            nombre: formData.get('nombre'),
            email: formData.get('email'),
            telefono: formData.get('telefono') || 'No proporcionado',
            profesion: formData.get('profesion'),
            atletas: formData.get('atletas') || 'No especificado',
            mensaje: formData.get('mensaje') || 'Sin mensaje adicional',
            fecha: new Date().toLocaleDateString('es-ES'),
            hora: new Date().toLocaleTimeString('es-ES')
        };
        
        // Simulate form submission (replace with actual endpoint)
        await submitForm(emailData);
        
        // Show success message
        showNotification('¡Mensaje enviado correctamente! Te contactaremos pronto.', 'success');
        
        // Reset form
        form.reset();
        
        // Track conversion
        trackConversion('contact_form_submitted', emailData);
        
    } catch (error) {
        console.error('Error submitting form:', error);
        showNotification('Error al enviar el mensaje. Por favor, intenta nuevamente.', 'error');
    } finally {
        // Reset button state
        resetLoadingState(submitBtn, btnText);
    }
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.getAttribute('name');
    
    // Remove existing error
    clearFieldError({ target: field });
    
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es obligatorio.';
    }
    
    // Email validation
    if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Por favor, ingresa un email válido.';
        }
    }
    
    // Phone validation
    if (fieldName === 'telefono' && value) {
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{8,}$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = 'Por favor, ingresa un teléfono válido.';
        }
    }
    
    // Name validation
    if (fieldName === 'nombre' && value) {
        if (value.length < 2) {
            isValid = false;
            errorMessage = 'El nombre debe tener al menos 2 caracteres.';
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#DC2626';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '4px';
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(e) {
    const field = e.target;
    field.classList.remove('error');
    
    const errorMessage = field.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

async function submitForm(data) {
    // Simulate API call - replace with your actual endpoint
    const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    
    return response.json();
}

function showLoadingState(button, textElement) {
    button.disabled = true;
    button.classList.add('loading');
    textElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
}

function resetLoadingState(button, textElement) {
    button.disabled = false;
    button.classList.remove('loading');
    textElement.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Mensaje';
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = type === 'success' ? 'fas fa-check-circle' : 
                 type === 'error' ? 'fas fa-exclamation-circle' : 
                 'fas fa-info-circle';
    
    notification.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '10000',
        padding: '16px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
        transform: 'translateX(400px)',
        transition: 'transform 0.3s ease',
        maxWidth: '400px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
    });
    
    // Set background color based on type
    notification.style.background = type === 'success' ? '#10B981' : 
                                   type === 'error' ? '#EF4444' : 
                                   '#3B82F6';
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notification);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
}

function removeNotification(notification) {
    if (notification && notification.parentNode) {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }
}

// Demo Video Functions
function initDemoVideo() {
    // Placeholder for demo video functionality
    window.playDemo = function() {
        const videoContainer = document.querySelector('.video-container');
        const placeholder = document.querySelector('.video-placeholder');
        
        // Create video element
        const video = document.createElement('div');
        video.innerHTML = `
            <div class="demo-playing">
                <div class="demo-loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Cargando demo...</p>
                </div>
                <p style="margin-top: 20px; text-align: center; color: #6B7280;">
                    <strong>Demo disponible por solicitud</strong><br>
                    <a href="#contacto" style="color: #2563EB;">Contáctanos para ver la demostración completa</a>
                </p>
            </div>
        `;
        
        video.style.cssText = `
            aspect-ratio: 16/9;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            padding: 40px;
        `;
        
        placeholder.replaceWith(video);
        
        // Track demo click
        trackConversion('demo_clicked', {
            section: 'demo',
            timestamp: new Date().toISOString()
        });
    };
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offsetTop = target.offsetTop - 70; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll Animations
function initScrollAnimations() {
    // Typing animation for hero mockup
    animateTyping();
    
    // Counter animations
    animateCounters();
    
    // Progress bars (if any)
    animateProgressBars();
}

function animateTyping() {
    const typingElements = document.querySelectorAll('.typing-indicator span');
    
    if (typingElements.length > 0) {
        // Add animation delay to typing indicators
        typingElements.forEach((span, index) => {
            span.style.animationDelay = `${index * 0.2}s`;
        });
    }
}

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const text = counter.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                const suffix = text.replace(/[0-9]/g, '');
                
                if (!isNaN(number)) {
                    animateNumber(counter, 0, number, suffix, 2000);
                    observer.unobserve(counter);
                }
            }
        });
    });
    
    counters.forEach(counter => observer.observe(counter));
}

function animateNumber(element, start, end, suffix, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * easeOutCubic(progress));
        element.textContent = current + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const progress = bar.getAttribute('data-progress') || '0';
                bar.style.width = progress + '%';
                observer.unobserve(bar);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

// Performance Optimizations
function initPerformanceOptimizations() {
    // Lazy load images
    lazyLoadImages();
    
    // Preload critical resources
    preloadCriticalResources();
    
    // Optimize animations for reduced motion
    respectReducedMotion();
}

function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

function preloadCriticalResources() {
    // Preload critical CSS
    const criticalCSS = [
        './css/styles.css'
    ];
    
    criticalCSS.forEach(href => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = href;
        document.head.appendChild(link);
    });
}

function respectReducedMotion() {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    if (prefersReducedMotion.matches) {
        // Disable animations for users who prefer reduced motion
        document.body.classList.add('reduce-motion');
        
        // Override AOS settings
        AOS.init({
            duration: 0,
            easing: 'linear',
            once: true,
            offset: 0,
            delay: 0
        });
    }
}

// Analytics and Tracking
function trackConversion(event, data = {}) {
    // Google Analytics 4 tracking
    if (typeof gtag !== 'undefined') {
        gtag('event', event, {
            event_category: 'landing_page',
            event_label: data.section || 'unknown',
            value: 1,
            ...data
        });
    }
    
    // Facebook Pixel tracking
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead', data);
    }
    
    // Console log for debugging
    console.log('Conversion tracked:', event, data);
}

// Utility Functions
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Contact Method Click Tracking
document.addEventListener('DOMContentLoaded', function() {
    // Track email clicks
    document.querySelectorAll('a[href^="mailto:"]').forEach(link => {
        link.addEventListener('click', () => {
            trackConversion('email_clicked', {
                email: link.href.replace('mailto:', ''),
                section: 'contact'
            });
        });
    });
    
    // Track WhatsApp clicks
    document.querySelectorAll('a[href*="wa.me"]').forEach(link => {
        link.addEventListener('click', () => {
            trackConversion('whatsapp_clicked', {
                section: 'contact'
            });
        });
    });
    
    // Track Instagram clicks
    document.querySelectorAll('a[href*="instagram.com"]').forEach(link => {
        link.addEventListener('click', () => {
            trackConversion('instagram_clicked', {
                section: 'contact'
            });
        });
    });
    
    // Track CTA button clicks
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const href = button.getAttribute('href');
            const text = button.textContent.trim();
            
            if (href && !href.startsWith('#')) {
                trackConversion('cta_clicked', {
                    button_text: text,
                    target_url: href,
                    section: findParentSection(button)
                });
            }
        });
    });
});

function findParentSection(element) {
    let parent = element.parentElement;
    while (parent) {
        if (parent.tagName === 'SECTION' && parent.id) {
            return parent.id;
        }
        parent = parent.parentElement;
    }
    return 'unknown';
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    
    // Track errors for debugging
    if (typeof gtag !== 'undefined') {
        gtag('event', 'exception', {
            description: e.error.message,
            fatal: false
        });
    }
});

// Service Worker Registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
