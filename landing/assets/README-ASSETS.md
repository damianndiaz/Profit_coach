# 📸 Assets Necesarios para ProFit Coach Landing

## Imágenes Requeridas

### 1. Favicon (favicon.ico)
- **Tamaño**: 32x32px, 16x16px 
- **Formato**: ICO
- **Contenido**: Logo de ProFit Coach en miniatura
- **Ubicación**: `/assets/favicon.ico`

### 2. Open Graph Image (og-image.jpg)
- **Tamaño**: 1200x630px
- **Formato**: JPG optimizado
- **Contenido**: Logo + "ProFit Coach - IA para Entrenadores Profesionales"
- **Ubicación**: `/assets/og-image.jpg`

### 3. Screenshots de la Aplicación

#### A. Hero Mockup (hero-mockup.png)
- **Tamaño**: 800x600px
- **Contenido**: Captura del chat principal con IA
- **Elementos a incluir**:
  - Interfaz de chat
  - Mensaje del usuario: "Rutina completa para futbolista intermedio"
  - Respuesta de IA con rutina generada
  - Botones de descarga Excel

#### B. Excel Mockup (excel-mockup.png)
- **Tamaño**: 600x400px
- **Contenido**: Captura de Excel con rutina exportada
- **Elementos a incluir**:
  - Hojas por bloque (Bloque 1, 2, 3, 4, 5)
  - Ejercicios detallados
  - Formato profesional

#### C. Metodología Screenshots (5 imágenes)
- **bloque1-activacion.png**: Ejercicios de activación glútea
- **bloque2-dinamico.png**: Movimientos explosivos y potencia
- **bloque3-fuerza1.png**: Patrones fundamentales de fuerza
- **bloque4-fuerza2.png**: Movimientos complejos
- **bloque5-contraste.png**: Velocidad y prevención

#### D. App Features (6 imágenes)
- **ia-especializada.png**: Interface de chat con IA
- **metodologia-5bloques.png**: Vista de rutina estructurada
- **personalizacion.png**: Formulario de personalización
- **excel-profesional.png**: Archivo Excel descargado
- **envio-automatico.png**: Confirmación de email enviado
- **variacion-infinita.png**: Diferentes rutinas generadas

#### E. Mobile Screenshots (3 imágenes)
- **mobile-chat.png**: Chat en móvil
- **mobile-rutina.png**: Rutina en móvil
- **mobile-descarga.png**: Descarga en móvil

### 4. Testimonials (3 imágenes)
- **testimonio1.jpg**: Foto profesional del entrenador 1
- **testimonio2.jpg**: Foto profesional del entrenador 2
- **testimonio3.jpg**: Foto profesional del entrenador 3
- **Tamaño**: 300x300px, formato circular
- **Nota**: Usar imágenes con permiso o placeholder profesionales

## 🎨 Especificaciones Técnicas

### Colores de Marca
- **Azul Principal**: #2563EB
- **Azul Oscuro**: #1E40AF
- **Morado Acento**: #7C3AED
- **Verde Éxito**: #10B981
- **Amarillo Highlight**: #FFD700

### Tipografía
- **Principal**: Inter (Google Fonts)
- **Pesos**: 300, 400, 500, 600, 700, 800

### Logo Elements
- **Icono**: 🏃‍♂️ (o vectorizado)
- **Texto**: "ProFit Coach"
- **Tagline**: "IA para Entrenadores Profesionales"

## 📝 Instrucciones para Screenshots

### Capturar desde ProFit Coach App:

1. **Chat Principal**:
   ```
   Usuario: "Necesito rutina completa para futbolista intermedio con 5 bloques"
   IA: "[Respuesta completa con rutina de 5 bloques]"
   ```

2. **Athlete Management**:
   - Vista con varios atletas registrados
   - Formulario de creación de atleta

3. **Excel Export**:
   - Archivo Excel abierto mostrando hojas por bloque
   - Datos bien formateados y profesionales

4. **Email Confirmation**:
   - Mensaje de confirmación de envío
   - Pantalla de éxito

### Herramientas Recomendadas:
- **Screenshots**: Lightshot, Snagit, o built-in del OS
- **Edición**: Canva, Figma, o Photoshop
- **Optimización**: TinyPNG, ImageOptim
- **Mockups**: Mockuphone para móviles

### Proceso de Captura:
1. **Limpiar Interface**: Remover datos personales/sensibles
2. **Usar Datos Demo**: Atletas ficticios con nombres genéricos
3. **Mostrar Funcionalidad**: Capturar estados activos/éxito
4. **Calidad Alta**: Mínimo 2x resolution para retina

## 🚨 Placeholder Temporales

Si no tienes las imágenes listas, puedes usar estos placeholders:

### CSS para Placeholders:
```css
.placeholder-image {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    text-align: center;
    padding: 20px;
}
```

### HTML Placeholder:
```html
<div class="placeholder-image" style="width: 800px; height: 600px;">
    <div>
        <i class="fas fa-image" style="font-size: 3rem; margin-bottom: 1rem;"></i>
        <p>Screenshot de ProFit Coach<br>Chat con IA</p>
    </div>
</div>
```

## ✅ Checklist Pre-Launch

- [ ] Favicon agregado y funcionando
- [ ] OG Image configurada (test en Facebook Debugger)
- [ ] Hero mockup capturado y optimizado
- [ ] Screenshots de features principales
- [ ] Testimonials con fotos profesionales
- [ ] Mobile screenshots responsivas
- [ ] Todas las imágenes optimizadas (< 100KB)
- [ ] Alt text agregado a todas las imágenes
- [ ] Tests en diferentes dispositivos

## 📊 Optimización de Imágenes

### Comando para optimizar:
```bash
# Instalar herramientas
npm install -g imagemin-cli imagemin-webp imagemin-mozjpeg imagemin-pngquant

# Optimizar
imagemin assets/*.{jpg,png} --out-dir=assets/optimized --plugin=webp --plugin=mozjpeg --plugin=pngquant
```

### Tamaños Objetivo:
- **Hero Images**: < 150KB
- **Feature Screenshots**: < 100KB
- **Icons/Small Images**: < 50KB
- **Total Page Weight**: < 2MB

¡Una vez que tengas estas imágenes, tu landing page estará completa y lista para convertir! 🚀
