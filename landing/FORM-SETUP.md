# 📧 Configuración de Backend para Formulario

## Opción 1: Formspree (Más Simple)
1. Ve a [formspree.io](https://formspree.io)
2. Crea cuenta gratuita
3. Reemplaza el action del formulario:
```html
<form action="https://formspree.io/f/TU_ENDPOINT" method="POST" class="contact-form" id="contactForm">
```

## Opción 2: Netlify Forms (Si usas Netlify)
1. Agrega `netlify` al formulario:
```html
<form netlify class="contact-form" id="contactForm">
```

## Opción 3: EmailJS (Frontend Only)
1. Ve a [emailjs.com](https://www.emailjs.com/)
2. Configura servicio de email
3. Usa JavaScript para enviar emails

## Opción 4: Backend Propio
- Node.js + Express + Nodemailer
- Python + Flask/FastAPI + SMTP
- PHP + Mail()

## Variables de Entorno Necesarias
```
FORM_EMAIL=diazzdamian00@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_usuario
SMTP_PASS=tu_contraseña_app
```
