# Comandos para conectar con GitHub (reemplaza con tu URL real)

# Una vez que crees el repositorio en GitHub, ejecuta estos comandos:

# 1. Agregar el repositorio remoto (reemplaza USERNAME con tu usuario de GitHub)
git remote add origin https://github.com/USERNAME/profit-coach.git

# 2. Verificar que se agregó correctamente
git remote -v

# 3. Subir la rama master al repositorio
git push -u origin master

# 4. Subir la rama development
git push -u origin development

# 5. Establecer la rama master como principal para despliegue
# (En GitHub, ve a Settings > Branches y configura master como default)

# 6. Para futuras actualizaciones, usar:
# git push origin master      # Para actualizaciones de producción
# git push origin development # Para desarrollo

# IMPORTANTE: 
# - La rama 'master' será tu rama de producción (para Streamlit Deploy)
# - La rama 'development' será tu rama de trabajo
# - Siempre trabaja en development y luego merge a master cuando esté listo
