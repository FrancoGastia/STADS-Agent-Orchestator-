import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ===========================
# CONFIGURACIÓN
# ===========================

# API Keys de Toqan (una por cada agente)
ORCHESTRATOR_API_KEY = st.secrets.get("ORCHESTRATOR_API_KEY") or os.getenv("ORCHESTRATOR_API_KEY")
FAQ_AGENT_API_KEY = st.secrets.get("FAQ_AGENT_API_KEY") or os.getenv("FAQ_AGENT_API_KEY")
REPORTS_AGENT_API_KEY = st.secrets.get("REPORTS_AGENT_API_KEY") or os.getenv("REPORTS_AGENT_API_KEY")
TEAM_PASSWORD = st.secrets.get("TEAM_PASSWORD") or os.getenv("TEAM_PASSWORD", "STADS2026")

# URL base de la API de Toqan
BASE_URL = "https://api.toqan.ai/api"

# Cargar documento FAQ
FAQ_DOCS_PATH = "faq_docs.txt"


# ===========================
# FUNCIONES AUXILIARES
# ===========================

def load_faq_docs():
    """Carga el documento de FAQs"""
    try:
        with open(FAQ_DOCS_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.warning("⚠️ Archivo faq_docs.txt no encontrado. El agente FAQ funcionará sin contexto.")
        return ""


def create_conversation(api_key, user_message, private_files=None):
    """
    Crea una nueva conversación en Toqan
    
    Args:
        api_key: API key del agente a usar
        user_message: Mensaje del usuario
        private_files: Lista de archivos privados (opcional)
    
    Returns:
        dict con conversation_id y request_id, o None si hay error
    """
    url = f"{BASE_URL}/create_conversation"
    
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "X-Api-Key": api_key
    }
    
    body = {
        "user_message": user_message
    }
    
    if private_files:
        body["private_user_files"] = private_files
    
    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Error creando conversación: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error de conexión: {str(e)}")
        return None


def get_answer(api_key, conversation_id, request_id, max_attempts=60):
    """
    Obtiene la respuesta del agente (con polling hasta que termine)
    
    Args:
        api_key: API key del agente
        conversation_id: ID de la conversación
        request_id: ID de la petición
        max_attempts: Intentos máximos de polling
    
    Returns:
        str con la respuesta, o None si hay error
    """
    url = f"{BASE_URL}/get_answer"
    
    headers = {
        "accept": "*/*",
        "X-Api-Key": api_key
    }
    
    params = {
        "conversation_id": conversation_id,
        "request_id": request_id
    }
    
    # Polling para esperar respuesta
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "finished":
                    return data.get("answer")
                elif status == "error":
                    st.error(f"❌ Error del agente: {data}")
                    return None
                elif status == "in_progress":
                    # Esperar 2 segundos antes de reintentar
                    time.sleep(1)
                    continue
                    
            else:
                st.error(f"❌ Error obteniendo respuesta: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None
    
    # Si llegamos aquí, se agotaron los intentos
    st.error("❌ Timeout: El agente tardó demasiado en responder")
    return None


def call_agent(api_key, message, context=None):
    """
    Función wrapper para llamar a cualquier agente
    
    Args:
        api_key: API key del agente
        message: Mensaje del usuario
        context: Contexto adicional (para FAQ docs)
    
    Returns:
        str con la respuesta del agente
    """
    # Si hay contexto, agregarlo al mensaje
    if context:
        full_message = f"""Contexto de documentación:

{context}

---

Pregunta del usuario: {message}"""
    else:
        full_message = message
    
    # Crear conversación
    conv_data = create_conversation(api_key, full_message)
    
    if not conv_data:
        return None
    
    # Obtener respuesta
    answer = get_answer(
        api_key, 
        conv_data["conversation_id"], 
        conv_data["request_id"]
    )
    
    return answer


# ===========================
# ORQUESTADOR
# ===========================

def orchestrate(user_query, faq_docs):
    """
    Función principal del orquestador
    
    1. Llama al agente orquestador para decidir
    2. Según la decisión, llama a FAQ o Reportes
    3. Devuelve la respuesta final
    """
    
    # Paso 1: Orquestador decide
    st.info("🤔 Analizando tu consulta...")
    
    orchestrator_prompt = f"""Clasifica esta consulta del usuario.

CONSULTA: {user_query}
¿Es FAQ o REPORTE?"""
    
    decision = call_agent(ORCHESTRATOR_API_KEY, orchestrator_prompt)
    
    if not decision:
        return "❌ Error: No se pudo conectar con el orquestador"
    
    # Limpiar la decisión
    decision = decision.strip().upper()
    
    # Paso 2: Llamar al agente correspondiente
    if "FAQ" in decision:
        st.info("📚 Consultando al agente de FAQs...")
        final_answer = call_agent(FAQ_AGENT_API_KEY, user_query, context=faq_docs)
        agent_type = "FAQ"
        
    elif "REPORTE" in decision:
        st.info("📊 Consultando al agente de Reportes...")
        final_answer = call_agent(REPORTS_AGENT_API_KEY, user_query)
        agent_type = "Reportes"
        
    else:
        # Si la decisión no es clara, usar FAQ por defecto
        st.warning(f"⚠️ Decisión no clara ({decision}), usando agente FAQ por defecto")
        final_answer = call_agent(FAQ_AGENT_API_KEY, user_query, context=faq_docs)
        agent_type = "FAQ (por defecto)"
    
    return final_answer, agent_type


# ===========================
# INTERFAZ STREAMLIT
# ===========================

def check_password():
    """Verifica la contraseña del equipo"""
    
    def password_entered():
        """Callback cuando se ingresa contraseña"""
        if st.session_state["password"] == TEAM_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primera vez que se carga
        st.text_input(
            "🔒 Contraseña del equipo", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
        
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta
        st.text_input(
            "🔒 Contraseña del equipo", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("❌ Contraseña incorrecta")
        return False
        
    else:
        # Contraseña correcta
        return True


def main():
    """Aplicación principal"""
    
    st.set_page_config(
        page_title="Orquestador de Agentes IA",
        page_icon="🤖",
        layout="centered"
    )
    
    st.title("🤖 Orquestador de Agentes IA")
    st.markdown("*Sistema inteligente de enrutamiento entre agentes FAQ y Reportes*")
    
    # Verificar contraseña
    if not check_password():
        st.stop()
    
    # Botón de logout
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state["password_correct"] = False
        st.rerun()
    
    # Información de estado
    st.sidebar.markdown("### 📊 Estado del Sistema")
    
    # Verificar API Keys
    keys_ok = all([ORCHESTRATOR_API_KEY, FAQ_AGENT_API_KEY, REPORTS_AGENT_API_KEY])
    
    if keys_ok:
        st.sidebar.success("✅ API Keys configuradas")
    else:
        st.sidebar.error("❌ Faltan API Keys")
        st.error("⚠️ Configura las API Keys en el archivo .env")
        st.stop()
    
    # Cargar docs FAQ
    faq_docs = load_faq_docs()
    if faq_docs:
        st.sidebar.success(f"✅ Docs FAQ cargados ({len(faq_docs)} caracteres)")
    else:
        st.sidebar.warning("⚠️ Sin docs FAQ")
    
    # Instrucciones
    with st.expander("ℹ️ ¿Cómo funciona?"):
        st.markdown("""
        1. **Escribe tu pregunta** en el campo de texto
        2. El **orquestador** analiza tu consulta
        3. Decide automáticamente si debe consultar:
           - 📚 **Agente FAQ**: Preguntas sobre el producto
           - 📊 **Agente Reportes**: Consultas sobre campañas
        4. El agente seleccionado procesa tu solicitud
        5. Recibes la respuesta final
        """)
    
    # Input del usuario
    st.markdown("---")
    user_query = st.text_area(
        "💬 Escribe tu consulta:",
        height=100,
        placeholder="Ejemplo: ¿Cómo funciona la integración con Salesforce?"
    )
    
    # Botón de envío
    col1, col2 = st.columns([1, 5])
    with col1:
        submit = st.button("🚀 Consultar", type="primary")
    
    # Procesar consulta
    if submit and user_query.strip():
        with st.spinner("🔄 Procesando tu consulta..."):
            answer, agent_type = orchestrate(user_query, faq_docs)
            
            if answer:
                st.success(f"✅ Respuesta del agente: **{agent_type}**")
                st.markdown("### 💡 Respuesta:")
                st.markdown(answer)
            else:
                st.error("❌ No se pudo obtener una respuesta. Intenta nuevamente.")
    
    elif submit:
        st.warning("⚠️ Por favor escribe una consulta")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>Powered by Toqan AI</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
