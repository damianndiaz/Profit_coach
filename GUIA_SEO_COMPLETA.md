🚀 GUÍA PASO A PASO: CONFIGURAR SEO PARA PROFIT COACH
=====================================================

PASO 1: ACTUALIZAR VERCEL (YA HECHO ✅)
======================================
✅ URLs actualizadas en index.html
✅ Sitemap.xml corregido  
✅ Robots.txt actualizado
✅ Cambios commiteados

PASO 2: DEPLOY A VERCEL
======================
1. Abrir terminal en la carpeta landing:
   cd "/workspaces/ProFit Coach/landing"

2. Deploy a Vercel:
   vercel --prod

3. O usar el script automático:
   ./deploy-seo.sh

PASO 3: GOOGLE SEARCH CONSOLE (MUY IMPORTANTE)
==============================================
1. Ir a: https://search.google.com/search-console

2. Hacer clic en "Agregar una propiedad"

3. Seleccionar "Prefijo de URL" y poner:
   https://profit-coach-landing.vercel.app

4. VERIFICAR PROPIEDAD - Opción más fácil:
   a) Descargar el archivo HTML de verificación
   b) Subirlo a tu carpeta landing/
   c) Hacer nuevo deploy
   d) Confirmar verificación

5. Una vez verificado:
   a) Ir a "Sitemaps" en el menú izquierdo
   b) Agregar: sitemap.xml
   c) Enviar

PASO 4: GOOGLE ANALYTICS (OPCIONAL PERO RECOMENDADO)
==================================================
1. Ir a: https://analytics.google.com

2. Crear cuenta/propiedad nueva

3. Copiar el código de tracking

4. Pegarlo en index.html después de <head>

PASO 5: VERIFICAR QUE TODO FUNCIONA
===================================
1. Probar que la página carga: https://profit-coach-landing.vercel.app

2. Verificar sitemap: https://profit-coach-landing.vercel.app/sitemap.xml

3. Verificar robots.txt: https://profit-coach-landing.vercel.app/robots.txt

4. Test SEO: https://developers.google.com/speed/pagespeed/insights/

PASO 6: MONITOREO (DESPUÉS DE 1-2 SEMANAS)
==========================================
1. Google Search Console:
   - Ver qué páginas están indexadas
   - Revisar errores de rastreo
   - Monitorear posiciones

2. Google Analytics:
   - Tráfico orgánico
   - Páginas más visitadas
   - Conversiones

COMANDOS ÚTILES:
===============
# Deploy rápido
cd "/workspaces/ProFit Coach/landing"
vercel --prod

# Verificar que sitemap funciona
curl https://profit-coach-landing.vercel.app/sitemap.xml

# Ping a Google (después de deploy)
curl "https://www.google.com/ping?sitemap=https://profit-coach-landing.vercel.app/sitemap.xml"

EXPECTATIVAS REALISTAS:
======================
- 1-3 días: Google empieza a indexar
- 1-2 semanas: Apareces en búsquedas nicho
- 1-3 meses: Posicionamiento estable
- 6+ meses: Top rankings para keywords principales

KEYWORDS PARA TRACKEAR:
=======================
- "entrenador personal IA"
- "rutinas entrenamiento automáticas" 
- "software preparador físico"
- "ProFit Coach"
- "metodología 5 bloques entrenamiento"

¡PRÓXIMO PASO: HACER EL DEPLOY! 🚀
