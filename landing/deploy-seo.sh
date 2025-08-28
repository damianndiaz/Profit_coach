#!/bin/bash

echo "🚀 Deploying ProFit Coach Landing with SEO optimizations..."

# Update sitemap lastmod dates
current_date=$(date +%Y-%m-%d)
sed -i "s/<lastmod>.*<\/lastmod>/<lastmod>$current_date<\/lastmod>/g" sitemap.xml

# Optimize images (if imagemagick is available)
if command -v convert &> /dev/null; then
    echo "📸 Optimizing images..."
    find ./assets -name "*.png" -exec convert {} -strip -quality 80 {} \;
    find ./assets -name "*.jpg" -exec convert {} -strip -quality 80 {} \;
fi

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

# Submit sitemap to Google (requires Google Search Console setup)
echo "🔍 Submitting sitemap to Google..."
curl -X GET "https://www.google.com/ping?sitemap=https://profit-coach-landing.vercel.app/sitemap.xml"

echo "✅ Deployment complete!"
echo "📊 Next steps:"
echo "1. Check Google Search Console"
echo "2. Monitor Google Analytics"
echo "3. Test site speed with PageSpeed Insights"
