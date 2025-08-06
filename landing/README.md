# ProFit Coach - Landing Page

## 📋 Descripción

Landing page profesional para ProFit Coach, diseñada para convertir visitantes en clientes potenciales. Incluye todas las funcionalidades necesarias para generar leads y mostrar el valor de la aplicación de IA para entrenadores.

## 🚀 Características

### ✅ Diseño y UX
- **Responsive Design**: Optimizada para desktop, tablet y móvil
- **Animaciones Suaves**: Efectos de scroll y transiciones profesionales
- **Carga Rápida**: Optimizada para performance y SEO
- **Accesibilidad**: Cumple estándares WCAG 2.1

### ✅ Secciones Incluidas
1. **Hero Section**: Propuesta de valor principal con CTA
2. **Problema**: Identifica los pain points del target
3. **Solución**: Presenta ProFit Coach como la solución
4. **Características**: 6 features principales con iconos
5. **Metodología**: Explicación detallada de los 5 bloques
6. **Demo**: Video placeholder y pasos del proceso
7. **Testimonios**: 3 testimonios con sistema de estrellas
8. **CTA Final**: Llamada a la acción principal
9. **Contacto**: 3 métodos + formulario funcional
10. **Footer**: Información adicional y links

### ✅ Funcionalidades Técnicas
- **Formulario de Contacto**: Validación completa y envío
- **Navegación Inteligente**: Scroll suave y highlights automáticos
- **Sistema de Notificaciones**: Feedback visual para acciones
- **Tracking de Conversiones**: Google Analytics y Facebook Pixel ready
- **Lazy Loading**: Carga optimizada de imágenes
- **PWA Ready**: Preparada para Progressive Web App

## 📁 Estructura de Archivos

```
landing/
├── index.html              # Página principal
├── css/
│   └── styles.css          # Estilos CSS completos
├── js/
│   └── main.js            # JavaScript funcional
├── assets/                 # Imágenes y recursos
│   ├── favicon.ico
│   ├── og-image.jpg
│   └── screenshots/       # Capturas de la app
└── README.md              # Este archivo
```

## 🛠️ Instalación y Configuración

### 1. Preparar Archivos
```bash
# Crear directorio en tu servidor
mkdir profitcoach-landing
cd profitcoach-landing

# Copiar archivos
cp -r landing/* .
```

### 2. Configurar Contacto
Edita las siguientes líneas en `index.html`:

```html
<!-- Línea ~680: Email -->
<a href="mailto:TU_EMAIL@dominio.com" class="method-link">

<!-- Línea ~695: WhatsApp -->
<a href="https://wa.me/TU_NUMERO?text=Hola%2C%20me%20interesa%20ProFit%20Coach" target="_blank">

<!-- Línea ~710: Instagram -->
<a href="https://instagram.com/TU_USUARIO" target="_blank">

<!-- Footer - Líneas ~850-870 -->
<a href="https://instagram.com/TU_USUARIO" target="_blank">
<a href="https://wa.me/TU_NUMERO" target="_blank">
<a href="mailto:TU_EMAIL@dominio.com">
```

### 3. Configurar Formulario
En `js/main.js`, línea ~150, configura tu endpoint:

```javascript
// Reemplazar con tu endpoint real
const response = await fetch('/api/contact', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

### 4. Agregar Imágenes
Crea la carpeta `assets/` y agrega:
- `favicon.ico` - Icono del sitio
- `og-image.jpg` - Imagen para redes sociales (1200x630px)
- `screenshots/` - Capturas de la aplicación

### 5. Configurar Analytics (Opcional)
Agrega antes de `</head>` en `index.html`:

```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>

<!-- Facebook Pixel -->
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
```

## 🌐 Despliegue

### Opción 1: Hosting Tradicional (Recomendado)
Subir archivos vía FTP/SFTP a:
- **Hostinger**: Plan Premium o superior
- **SiteGround**: Plan GrowBig o superior  
- **DigitalOcean**: App Platform o Droplet
- **Cloudflare Pages**: Gratis con dominio personalizado

### Opción 2: Netlify (Gratis)
```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=./
```

### Opción 3: Vercel (Gratis)
```bash
# Instalar Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Opción 4: GitHub Pages
1. Subir archivos a repositorio GitHub
2. Ir a Settings > Pages
3. Seleccionar branch main
4. Tu sitio estará en `https://usuario.github.io/repo`

## 📧 Configurar Backend para Formulario

### Opción 1: Formspree (Más Fácil)
1. Registrarse en [formspree.io](https://formspree.io)
2. Crear nuevo formulario
3. Reemplazar endpoint en `js/main.js`:

```javascript
const response = await fetch('https://formspree.io/f/TU_FORM_ID', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

### Opción 2: Netlify Forms
Si usas Netlify, agrega a tu `<form>`:
```html
<form class="contact-form" id="contactForm" netlify>
```

### Opción 3: Backend Propio (Node.js + Express)
```javascript
// server.js
const express = require('express');
const nodemailer = require('nodemailer');
const app = express();

app.use(express.json());

app.post('/api/contact', async (req, res) => {
    const { nombre, email, mensaje } = req.body;
    
    // Configurar Nodemailer
    const transporter = nodemailer.createTransporter({
        // Tu configuración SMTP
    });
    
    // Enviar email
    await transporter.sendMail({
        from: email,
        to: 'tu-email@dominio.com',
        subject: `Nuevo contacto: ${nombre}`,
        text: mensaje
    });
    
    res.json({ success: true });
});

app.listen(3000);
```

## 🎨 Personalización Visual

### Colores Principales
```css
:root {
    --primary-blue: #2563EB;    /* Azul principal */
    --primary-dark: #1E40AF;    /* Azul oscuro */
    --accent-purple: #7C3AED;   /* Morado acento */
    --accent-green: #10B981;    /* Verde éxito */
}
```

### Fuentes
La landing usa **Inter** (Google Fonts). Para cambiar:
```html
<!-- En <head> -->
<link href="https://fonts.googleapis.com/css2?family=TU_FUENTE:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

```css
/* En CSS */
:root {
    --font-family: 'TU_FUENTE', sans-serif;
}
```

## 📱 Screenshots de la App

Para mejor conversión, agrega screenshots reales de ProFit Coach:

1. **Hero Mockup**: Captura del chat de IA
2. **Features**: Pantallas de diferentes funciones
3. **Testimonials**: Fotos de usuarios reales (con permiso)

Ubicación: `assets/screenshots/`
Formatos: WebP (preferido) o PNG
Tamaños recomendados: 800x600px para mockups

## 🔧 Optimización SEO

### Meta Tags Incluidos
- Title y Description optimizados
- Open Graph para redes sociales
- Twitter Cards
- Structured Data (JSON-LD) - Agregar si necesario

### Mejoras Adicionales
1. **Sitemap.xml**: Generar y subir
2. **Robots.txt**: Configurar correctamente
3. **Schema.org**: Agregar structured data
4. **Core Web Vitals**: La landing ya está optimizada

## 📈 Conversión y Tracking

### Eventos Trackeados
- `contact_form_submitted`: Formulario enviado
- `demo_clicked`: Video demo clickeado
- `email_clicked`: Email clickeado
- `whatsapp_clicked`: WhatsApp clickeado
- `instagram_clicked`: Instagram clickeado
- `cta_clicked`: Cualquier botón CTA

### KPIs Importantes
- **Bounce Rate**: < 60%
- **Time on Page**: > 2 minutos
- **Conversion Rate**: 2-5% (formulario)
- **Page Load Speed**: < 3 segundos

## 🚨 Troubleshooting

### Problema: Formulario no envía
1. Verificar endpoint en `js/main.js`
2. Revisar CORS headers en backend
3. Comprobar console del navegador

### Problema: Animaciones no funcionan
1. Verificar que AOS library se carga
2. Comprobar JavaScript errors
3. Verificar `prefers-reduced-motion`

### Problema: Imágenes no cargan
1. Verificar rutas en `index.html`
2. Confirmar archivos en `/assets/`
3. Revisar permisos de archivos

## 📞 Soporte

Para dudas sobre implementación:
- **Email**: [tu-email@dominio.com]
- **WhatsApp**: [tu-numero]

## 📄 Licencia

Código propietario para ProFit Coach. No redistribuir sin autorización.

---

**¡Tu landing page está lista para convertir visitantes en clientes! 🚀**
