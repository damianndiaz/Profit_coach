# Streamlit Community Cloud Deployment Configuration

## 📋 Configuración Paso a Paso

### 1. **Preparar el Repositorio en GitHub**
- Crear repositorio público en GitHub
- Subir código usando las instrucciones en `GITHUB_SETUP.md`
- Asegurar que la rama `master` contiene código estable

### 2. **Configurar Streamlit Community Cloud**

#### A. **Conectar GitHub**
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Login con tu cuenta de GitHub
3. Autoriza el acceso a tu repositorio

#### B. **Crear Nueva App**
1. Haz clic en "New app"
2. Selecciona tu repositorio `profit-coach`
3. Selecciona rama: `master`
4. Main file path: `main.py`
5. App URL: elige un nombre único (ej: `profit-coach-ai`)

### 3. **Configurar Secretos (IMPORTANTE)**

En la configuración de tu app en Streamlit Cloud, agrega estos secretos:

```toml
# En Streamlit Cloud > App settings > Secrets

[database]
url = "postgresql://usuario:contraseña@host:puerto/database"

[openai]
api_key = "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
assistant_id = "asst_XXXXXXXXXXXXXXXXXXXXXXXX"

[email]
host = "smtp.gmail.com"
port = 587
use_tls = true
username = "tu_email@gmail.com"
password = "tu_app_password_de_gmail"
from_name = "ProFit Coach"
from_email = "tu_email@gmail.com"
```

### 4. **Configurar Base de Datos**

#### Opción A: **Supabase (Recomendado - Gratis)**
1. Ve a [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Ve a Settings > Database
4. Copia la connection string
5. Úsala en los secretos de Streamlit

#### Opción B: **PostgreSQL Remoto**
- Railway.app
- Heroku Postgres
- AWS RDS (Free Tier)

### 5. **Variables de Entorno para Desarrollo Local**

Archivo `.env` (NO subir a GitHub):
```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
OPENAI_ASSISTANT_ID=asst_XXXXXXXXXXXXXXXXXXXXXXXX
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password_de_16_caracteres
EMAIL_FROM_NAME=ProFit Coach
EMAIL_FROM_EMAIL=tu_email@gmail.com
```

### 6. **Flujo de Trabajo Recomendado**

```bash
# Desarrollo local (rama development)
git checkout development
# ... hacer cambios ...
git add .
git commit -m "feat: nueva funcionalidad"
git push origin development

# Cuando esté listo para producción
git checkout master
git merge development
git push origin master
# ↑ Esto automáticamente actualizará tu app en Streamlit Cloud
```

### 7. **Checklist Pre-Deploy**

- [ ] ✅ Repositorio en GitHub configurado
- [ ] ✅ Rama `master` con código estable  
- [ ] ✅ `requirements.txt` actualizado
- [ ] ✅ Secretos configurados en Streamlit Cloud
- [ ] ✅ Base de datos PostgreSQL remota configurada
- [ ] ✅ OpenAI API Key válida
- [ ] ✅ Assistant ID configurado
- [ ] ✅ Email SMTP configurado (opcional)
- [ ] ✅ `.env` local para desarrollo
- [ ] ✅ `.gitignore` protegiendo información sensible

### 8. **URLs Importantes**

- **App Live:** `https://tu-app-name.streamlit.app`
- **GitHub Repo:** `https://github.com/tu-usuario/profit-coach`
- **Streamlit Cloud:** `https://share.streamlit.io`
- **Logs:** Disponibles en Streamlit Cloud dashboard

### 9. **Troubleshooting Común**

#### **Error de Módulos**
```bash
# Si falta algún módulo, agregar a requirements.txt
pip freeze > requirements.txt
```

#### **Error de Base de Datos**
- Verificar connection string en secretos
- Asegurar que la DB permite conexiones externas
- Verificar firewall/whitelist

#### **Error de OpenAI**
- Verificar API Key válida
- Verificar créditos disponibles
- Asegurar que el Assistant ID existe

#### **Error de Email**
- Verificar que usas App Password (no la contraseña normal de Gmail)
- Activar 2FA en Gmail para generar App Password

### 10. **Monitoreo y Mantenimiento**

- **Logs:** Revisar logs en Streamlit Cloud regularmente
- **Performance:** Monitorear uso de recursos
- **Actualizaciones:** Mantener dependencias actualizadas
- **Backups:** Hacer backups regulares de la base de datos

---

**🚀 ¡Una vez configurado, tu app estará disponible 24/7 en la nube!**
