# ProFit Coach Landing - Deployment Guide

## 🚀 Guía de Despliegue Rápido

### Paso 1: Preparar tu Servidor
```bash
# Si usas Ubuntu/Debian
sudo apt update
sudo apt install nginx

# Si usas CentOS/RHEL
sudo yum install nginx
```

### Paso 2: Subir Archivos
```bash
# Vía SCP (reemplaza con tus datos)
scp -r landing/* usuario@tu-servidor.com:/var/www/html/

# O vía FTP usando FileZilla
# Host: tu-servidor.com
# Usuario: tu-usuario-ftp
# Puerto: 21 (FTP) o 22 (SFTP)
```

### Paso 3: Configurar Nginx
```nginx
# /etc/nginx/sites-available/profitcoach
server {
    listen 80;
    server_name profitcoach.app www.profitcoach.app;
    root /var/www/html;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_types text/css text/javascript application/javascript application/json;
    
    # Cache static assets
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Handle form submissions (if using backend)
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Paso 4: SSL con Let's Encrypt
```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d profitcoach.app -d www.profitcoach.app

# Verificar auto-renovación
sudo certbot renew --dry-run
```

### Paso 5: Activar Configuración
```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/profitcoach /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Reiniciar nginx
sudo systemctl restart nginx
```

## 🔧 Backend Simple para Formulario (Node.js)

### Instalación
```bash
# Crear directorio backend
mkdir profitcoach-backend
cd profitcoach-backend

# Inicializar proyecto
npm init -y

# Instalar dependencias
npm install express nodemailer cors helmet rate-limit
```

### Código del Servidor
```javascript
// server.js
const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = 3000;

// Middleware
app.use(helmet());
app.use(cors({
    origin: ['https://profitcoach.app', 'https://www.profitcoach.app']
}));
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5 // limit each IP to 5 requests per windowMs
});
app.use('/api/', limiter);

// Configurar Nodemailer (Gmail example)
const transporter = nodemailer.createTransporter({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER, // tu-email@gmail.com
        pass: process.env.EMAIL_PASS  // tu-app-password
    }
});

// Endpoint para formulario de contacto
app.post('/api/contact', async (req, res) => {
    try {
        const { nombre, email, telefono, profesion, atletas, mensaje } = req.body;
        
        // Validación básica
        if (!nombre || !email) {
            return res.status(400).json({ 
                success: false, 
                message: 'Nombre y email son obligatorios' 
            });
        }
        
        // Email al administrador
        await transporter.sendMail({
            from: `"ProFit Coach Landing" <${process.env.EMAIL_USER}>`,
            to: 'admin@profitcoach.app', // TU EMAIL
            subject: `🚀 Nuevo Lead: ${nombre}`,
            html: `
                <h2>Nuevo Contacto desde Landing Page</h2>
                <p><strong>Nombre:</strong> ${nombre}</p>
                <p><strong>Email:</strong> ${email}</p>
                <p><strong>Teléfono:</strong> ${telefono || 'No proporcionado'}</p>
                <p><strong>Profesión:</strong> ${profesion || 'No especificada'}</p>
                <p><strong>Cantidad Atletas:</strong> ${atletas || 'No especificado'}</p>
                <p><strong>Mensaje:</strong></p>
                <blockquote>${mensaje || 'Sin mensaje adicional'}</blockquote>
                
                <hr>
                <p><em>Enviado desde: ${req.get('origin') || 'Desconocido'}</em></p>
                <p><em>IP: ${req.ip}</em></p>
                <p><em>Fecha: ${new Date().toLocaleString('es-ES')}</em></p>
            `
        });
        
        // Email de confirmación al usuario
        await transporter.sendMail({
            from: `"ProFit Coach" <${process.env.EMAIL_USER}>`,
            to: email,
            subject: '✅ Hemos recibido tu mensaje - ProFit Coach',
            html: `
                <h2>¡Gracias por tu interés en ProFit Coach!</h2>
                <p>Hola ${nombre},</p>
                
                <p>Hemos recibido tu mensaje y nuestro equipo te contactará en las próximas 24 horas.</p>
                
                <p><strong>Mientras tanto, puedes:</strong></p>
                <ul>
                    <li>📱 Seguirnos en <a href="https://instagram.com/profitcoach.app">Instagram</a></li>
                    <li>💬 Escribirnos por <a href="https://wa.me/TU_NUMERO">WhatsApp</a> para consultas urgentes</li>
                    <li>📧 Responder este email con preguntas específicas</li>
                </ul>
                
                <p>¡Gracias por confiar en nosotros!</p>
                
                <p>El equipo de ProFit Coach 🏃‍♂️</p>
                
                <hr>
                <p style="font-size: 12px; color: #666;">
                    Este es un email automático. Si no solicitaste información sobre ProFit Coach, 
                    puedes ignorar este mensaje.
                </p>
            `
        });
        
        console.log(`✅ Nuevo lead: ${nombre} - ${email}`);
        
        res.json({ 
            success: true, 
            message: 'Mensaje enviado correctamente' 
        });
        
    } catch (error) {
        console.error('❌ Error enviando email:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Error interno del servidor' 
        });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`🚀 Servidor backend ejecutándose en puerto ${PORT}`);
});
```

### Variables de Entorno
```bash
# .env
EMAIL_USER=tu-email@gmail.com
EMAIL_PASS=tu-app-password-de-gmail
```

### Ejecutar Backend
```bash
# Instalar PM2 para producción
npm install -g pm2

# Ejecutar en desarrollo
npm start

# Ejecutar en producción
pm2 start server.js --name profitcoach-backend
pm2 startup
pm2 save
```

## 📊 Análisis y Métricas

### Google Analytics 4 Setup
1. Crear cuenta en analytics.google.com
2. Obtener GA_MEASUREMENT_ID
3. Agregar código a index.html:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID', {
    page_title: 'ProFit Coach - IA para Entrenadores',
    page_location: window.location.href
  });
</script>
```

### Facebook Pixel
```html
<!-- Facebook Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'TU_PIXEL_ID');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=TU_PIXEL_ID&ev=PageView&noscript=1"
/></noscript>
<!-- End Facebook Pixel Code -->
```

## 🔐 Seguridad

### Headers de Seguridad
```nginx
# En tu configuración nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google-analytics.com https://connect.facebook.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;" always;
```

### Firewall Básico
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Fail2ban
sudo apt install fail2ban
```

## 📈 Optimización Performance

### Compresión de Imágenes
```bash
# Instalar imagemin
npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant

# Convertir imágenes
imagemin assets/*.{jpg,png} --out-dir=assets/optimized --plugin=webp
```

### Minificación CSS/JS
```bash
# CSS
npm install -g cssnano-cli
cssnano css/styles.css css/styles.min.css

# JavaScript
npm install -g uglify-js
uglifyjs js/main.js -o js/main.min.js -c -m
```

## 🚨 Troubleshooting Común

### Error 404 en assets
```bash
# Verificar permisos
sudo chown -R www-data:www-data /var/www/html/
sudo chmod -R 755 /var/www/html/
```

### Formulario no funciona
1. Verificar CORS en backend
2. Revisar logs: `sudo tail -f /var/log/nginx/error.log`
3. Probar endpoint manualmente: `curl -X POST https://tu-sitio.com/api/contact`

### SSL Certificate Error
```bash
# Renovar certificado
sudo certbot renew

# Si falla, regenerar
sudo certbot delete
sudo certbot --nginx -d tu-dominio.com
```

## 📞 Soporte Post-Deploy

Una vez desplegada tu landing page:

1. **Monitorear**: Configurar alertas en Google Analytics
2. **Testear**: Probar formulario de diferentes dispositivos
3. **Optimizar**: Usar herramientas como PageSpeed Insights
4. **Actualizar**: Mantener contenido y testimonios actualizados

¡Tu landing page está lista para generar leads de calidad! 🚀
