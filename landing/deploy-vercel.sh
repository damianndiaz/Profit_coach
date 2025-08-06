#!/bin/bash

# Script para deploy a Vercel vía GitHub
echo "🚀 Preparando deploy a Vercel..."

# 1. Crear .gitignore si no existe
if [ ! -f .gitignore ]; then
    echo "node_modules/" > .gitignore
    echo ".env" >> .gitignore
    echo ".vercel" >> .gitignore
    echo "*.log" >> .gitignore
fi

# 2. Crear vercel.json para configuración
cat > vercel.json << EOL
{
  "version": 2,
  "name": "profit-coach-landing",
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/\$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
EOL

echo "✅ Archivos de configuración creados"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ve a https://vercel.com y crea una cuenta"
echo "2. Conecta tu repositorio de GitHub"
echo "3. Vercel detectará automáticamente tu proyecto"
echo "4. Click en 'Deploy'"
echo ""
echo "🌐 Tu landing estará live en segundos!"
