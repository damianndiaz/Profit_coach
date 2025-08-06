#!/bin/bash

# ProFit Coach Landing Page - Deployment Script
# Automatiza el proceso de configuración y despliegue

set -e  # Exit on error

echo "🚀 ProFit Coach Landing Page - Deployment Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if script is run with necessary permissions
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "This script is running as root. Some operations might need adjustment."
    fi
}

# Collect deployment information
collect_info() {
    log_info "Collecting deployment information..."
    echo ""
    
    read -p "📧 Enter your contact email: " EMAIL
    read -p "📱 Enter your WhatsApp number (with country code, e.g., +34123456789): " WHATSAPP
    read -p "📱 Enter your Instagram username (without @): " INSTAGRAM
    read -p "🌐 Enter your domain name (e.g., profitcoach.app): " DOMAIN
    
    echo ""
    log_info "Deployment Configuration:"
    echo "Email: $EMAIL"
    echo "WhatsApp: $WHATSAPP" 
    echo "Instagram: @$INSTAGRAM"
    echo "Domain: $DOMAIN"
    echo ""
    
    read -p "Is this information correct? (y/N): " CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled by user"
        exit 1
    fi
}

# Update contact information in HTML
update_contact_info() {
    log_info "Updating contact information in HTML..."
    
    # Email updates
    sed -i "s|mailto:hola@profitcoach.app|mailto:$EMAIL|g" index.html
    sed -i "s|hola@profitcoach.app|$EMAIL|g" index.html
    
    # WhatsApp updates  
    sed -i "s|https://wa.me/1234567890|https://wa.me/$WHATSAPP|g" index.html
    
    # Instagram updates
    sed -i "s|https://instagram.com/profitcoach.app|https://instagram.com/$INSTAGRAM|g" index.html
    sed -i "s|@profitcoach.app|@$INSTAGRAM|g" index.html
    
    # Domain updates
    sed -i "s|https://profitcoach.app|https://$DOMAIN|g" index.html
    sed -i "s|profitcoach.app|$DOMAIN|g" sitemap.xml
    
    log_success "Contact information updated successfully"
}

# Optimize images (if tools available)
optimize_images() {
    log_info "Checking for image optimization tools..."
    
    if command -v imagemin &> /dev/null; then
        log_info "Optimizing images..."
        
        if [ -d "assets" ] && [ "$(ls -A assets/*.{jpg,jpeg,png} 2>/dev/null)" ]; then
            imagemin assets/*.{jpg,jpeg,png} --out-dir=assets/optimized --plugin=webp --plugin=mozjpeg --plugin=pngquant
            log_success "Images optimized and saved to assets/optimized/"
        else
            log_warning "No images found in assets/ directory"
        fi
    else
        log_warning "imagemin not installed. Skipping image optimization."
        echo "Install with: npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant"
    fi
}

# Minify CSS and JS (if tools available)
minify_assets() {
    log_info "Checking for minification tools..."
    
    # Minify CSS
    if command -v cssnano &> /dev/null; then
        log_info "Minifying CSS..."
        cssnano css/styles.css css/styles.min.css
        
        # Update HTML to use minified version
        sed -i 's|css/styles.css|css/styles.min.css|g' index.html
        
        log_success "CSS minified successfully"
    else
        log_warning "cssnano not installed. Skipping CSS minification."
    fi
    
    # Minify JavaScript
    if command -v uglifyjs &> /dev/null; then
        log_info "Minifying JavaScript..."
        uglifyjs js/main.js -o js/main.min.js -c -m
        
        # Update HTML to use minified version
        sed -i 's|js/main.js|js/main.min.js|g' index.html
        
        log_success "JavaScript minified successfully"
    else
        log_warning "uglify-js not installed. Skipping JS minification."
    fi
}

# Validate HTML
validate_html() {
    log_info "Validating HTML structure..."
    
    # Basic HTML validation checks
    if ! grep -q "<!DOCTYPE html>" index.html; then
        log_error "HTML DOCTYPE missing"
        return 1
    fi
    
    if ! grep -q "<html lang=" index.html; then
        log_error "HTML lang attribute missing"
        return 1
    fi
    
    if ! grep -q "<meta charset=" index.html; then
        log_error "Meta charset missing"
        return 1
    fi
    
    if ! grep -q "<meta name=\"viewport\"" index.html; then
        log_error "Viewport meta tag missing"
        return 1
    fi
    
    log_success "Basic HTML validation passed"
}

# Create backup
create_backup() {
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    log_info "Creating backup in $BACKUP_DIR..."
    
    mkdir -p "$BACKUP_DIR"
    cp -r *.html css/ js/ assets/ robots.txt sitemap.xml "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup created successfully"
}

# Generate deployment report
generate_report() {
    REPORT_FILE="deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log_info "Generating deployment report..."
    
    cat > "$REPORT_FILE" << EOF
ProFit Coach Landing Page - Deployment Report
==========================================

Date: $(date)
Domain: $DOMAIN
Email: $EMAIL
WhatsApp: $WHATSAPP
Instagram: @$INSTAGRAM

Files Modified:
- index.html (contact information updated)
- sitemap.xml (domain updated)
$([ -f "css/styles.min.css" ] && echo "- css/styles.min.css (created)")
$([ -f "js/main.min.js" ] && echo "- js/main.min.js (created)")

Next Steps:
1. Upload all files to your web server
2. Configure SSL certificate (Let's Encrypt recommended)
3. Set up form backend (see DEPLOYMENT.md)
4. Configure Google Analytics and Facebook Pixel
5. Test contact form functionality
6. Add real screenshots to assets/ directory

Important URLs to test:
- https://$DOMAIN
- https://$DOMAIN/sitemap.xml
- https://$DOMAIN/robots.txt

Contact Methods to Verify:
- Email: mailto:$EMAIL
- WhatsApp: https://wa.me/$WHATSAPP
- Instagram: https://instagram.com/$INSTAGRAM

Performance Recommendations:
- Enable Gzip compression on server
- Configure browser caching
- Add CDN (Cloudflare recommended)
- Monitor Core Web Vitals

Security Recommendations:
- Configure security headers
- Enable HTTPS redirect
- Set up firewall rules
- Regular backups

For support, refer to README.md and DEPLOYMENT.md
EOF

    log_success "Deployment report generated: $REPORT_FILE"
}

# Main deployment process
main() {
    echo ""
    log_info "Starting ProFit Coach Landing Page deployment process..."
    echo ""
    
    # Check current directory
    if [ ! -f "index.html" ]; then
        log_error "index.html not found. Are you in the correct directory?"
        exit 1
    fi
    
    check_permissions
    collect_info
    create_backup
    
    log_info "Processing files..."
    update_contact_info
    validate_html
    optimize_images
    minify_assets
    generate_report
    
    echo ""
    log_success "🎉 Deployment preparation completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Upload all files to your web server"
    echo "2. Configure your domain DNS to point to the server"
    echo "3. Set up SSL certificate"
    echo "4. Configure backend for contact form (see DEPLOYMENT.md)"
    echo "5. Add real screenshots to assets/ directory"
    echo "6. Test everything thoroughly"
    echo ""
    log_info "For detailed instructions, check DEPLOYMENT.md"
    echo ""
    
    read -p "Would you like to open the deployment guide? (y/N): " OPEN_GUIDE
    if [[ $OPEN_GUIDE =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open DEPLOYMENT.md
        elif command -v open &> /dev/null; then
            open DEPLOYMENT.md
        else
            log_info "Please manually open DEPLOYMENT.md for detailed instructions"
        fi
    fi
}

# Run main function
main "$@"
