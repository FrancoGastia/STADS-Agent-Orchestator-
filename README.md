# 🤖 Orquestador de Agentes IA - Toqan

Sistema inteligente que enruta automáticamente consultas entre un agente FAQ y un agente de Reportes.

## 📋 Requisitos Previos

- Python 3.8 o superior
- 3 API Keys de Toqan:
  - 1 para el agente orquestador
  - 1 para el agente FAQ
  - 1 para el agente de Reportes

## 🚀 Instalación y Configuración

### 1. Descarga los archivos

Descarga todos los archivos del proyecto en una carpeta:
- `app.py`
- `requirements.txt`
- `.env.example`
- `faq_docs.txt`
- `README.md`

### 2. Instala Python

Si no tienes Python instalado:
- Windows/Mac: https://www.python.org/downloads/
- Asegúrate de marcar "Add Python to PATH" durante la instalación

### 3. Instala las dependencias

Abre una terminal/consola en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### 4. Configura tus API Keys

1. Copia el archivo `.env.example` y renómbralo a `.env`:
   ```bash
   # En Windows
   copy .env.example .env
   
   # En Mac/Linux
   cp .env.example .env
   ```

2. Abre el archivo `.env` con un editor de texto

3. Reemplaza los valores con tus API Keys reales de Toqan:
   ```
   ORCHESTRATOR_API_KEY=sk-tu-key-real-aqui
   FAQ_AGENT_API_KEY=sk-tu-key-real-aqui
   REPORTS_AGENT_API_KEY=sk-tu-key-real-aqui
   TEAM_PASSWORD=tu_contraseña_personalizada
   ```

4. Guarda el archivo

### 5. Configura el documento FAQ

1. Abre el archivo `faq_docs.txt`
2. Reemplaza el contenido de ejemplo con tu documentación real del producto
3. Guarda el archivo

## 🎮 Uso Local

### Ejecutar en tu computadora

En la terminal, ejecuta:

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en: `http://localhost:8501`

- **Usuario**: No hay usuario
- **Contraseña**: La que configuraste en `.env` (por defecto: `mi_equipo_2024`)

### Compartir en tu red local

Si quieres que otros en tu WiFi accedan:

```bash
streamlit run app.py --server.address 0.0.0.0
```

Luego comparte la URL que aparece (ejemplo: `http://192.168.1.10:8501`)

## ☁️ Deploy en Streamlit Cloud (GRATIS)

### Paso 1: Sube a GitHub

1. Crea una cuenta en GitHub (si no tienes): https://github.com
2. Crea un nuevo repositorio (botón "New repository")
3. Sube todos los archivos EXCEPTO el archivo `.env`
4. **IMPORTANTE**: No subas el archivo `.env` a GitHub (contiene tus API Keys)

### Paso 2: Deploy en Streamlit Cloud

1. Ve a: https://streamlit.io/cloud
2. Inicia sesión con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona tu repositorio de GitHub
5. En "Main file path" escribe: `app.py`
6. Click en "Advanced settings"
7. En "Secrets", pega el contenido de tu archivo `.env`:
   ```
   ORCHESTRATOR_API_KEY="tu_key_aqui"
   FAQ_AGENT_API_KEY="tu_key_aqui"
   REPORTS_AGENT_API_KEY="tu_key_aqui"
   TEAM_PASSWORD="tu_password_aqui"
   ```
8. Click en "Deploy"

¡Listo! En 2-3 minutos tendrás una URL pública tipo: `https://tu-app.streamlit.app`

## 🏗️ Arquitectura

```
Usuario → Streamlit UI → Orquestador (Agente 1)
                              ↓
                         Clasifica consulta
                         /              \
                        /                \
              Agente FAQ            Agente Reportes
              (con docs)            (sin contexto)
                    \                  /
                     \                /
                      Respuesta Final
```

## 🔧 Personalización

### Cambiar la lógica de clasificación

Edita la función `orchestrate()` en `app.py`, específicamente el prompt del orquestador.

### Agregar más agentes

1. Agrega una nueva API Key en `.env`
2. Modifica la función `orchestrate()` para incluir el nuevo tipo
3. Agrega el nuevo caso en el if/elif

### Cambiar la contraseña

Edita la variable `TEAM_PASSWORD` en el archivo `.env`

## 📊 Monitoreo

El sidebar muestra:
- ✅ Estado de las API Keys
- ✅ Estado del documento FAQ
- 🚪 Botón de cierre de sesión

## ❓ Troubleshooting

### Error: "Faltan API Keys"
- Verifica que el archivo `.env` existe
- Verifica que las 3 API Keys están configuradas
- Reinicia la aplicación

### Error: "Archivo faq_docs.txt no encontrado"
- Verifica que el archivo existe en la misma carpeta que `app.py`
- Verifica que se llama exactamente `faq_docs.txt`

### Error: "Timeout: El agente tardó demasiado"
- El agente está procesando consultas muy complejas
- Verifica tu conexión a internet
- Intenta con una consulta más simple

### La app no se abre en el navegador
- Abre manualmente: http://localhost:8501
- Verifica que no haya errores en la terminal

## 🔐 Seguridad

- ⚠️ **NUNCA** subas el archivo `.env` a GitHub
- ⚠️ Usa contraseñas fuertes
- ⚠️ No compartas tus API Keys públicamente
- ✅ Rota tus API Keys periódicamente
- ✅ En Streamlit Cloud, usa "Secrets" para variables sensibles

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la terminal
2. Verifica que todas las API Keys son válidas
3. Consulta la documentación de Toqan: https://toqan-api.readme.io

## 📄 Licencia

Uso interno privado.
