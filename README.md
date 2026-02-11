# Chatbot de Pedidos con IA para "La Pizza Feliz"

Este proyecto es una aplicación web completa que simula un chatbot para tomar pedidos en una pizzería. Utiliza un modelo de lenguaje de OpenAI para mantener una conversación natural con el usuario, gestionar un carrito de la compra en tiempo real y guardar el pedido final en una base de datos.

## ✨ Características Principales

- **Interfaz de Chat Interactiva:** Un frontend limpio y sencillo construido con HTML y JavaScript puro.
- **Resumen de Pedido en Tiempo Real:** Un panel lateral que se actualiza instantáneamente a medida que el usuario interactúa con el bot.
- **Backend Inteligente con IA:** Un servidor en Python con FastAPI que se conecta a OpenAI para procesar el lenguaje natural.
- **Memoria de Conversación:** El chatbot recuerda el historial de la conversación y el estado del carrito para ofrecer una experiencia fluida.
- **Menú Dinámico:** El menú de la pizzería se carga desde una base de datos, permitiendo añadir o modificar productos sin cambiar el código.
- **Persistencia de Datos:** Los pedidos completados se guardan en una base de datos SQLite.

---

## 🚀 Guía de Instalación y Ejecución en Windows

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### 1. Prerrequisitos

- **Python 3.7+** instalado en tu sistema.
- Una clave de API de OpenAI.

### 2. Configuración del Backend

1.  **Abre una terminal:**
    Puedes usar PowerShell o el Símbolo del sistema (cmd). Para abrirlo, pulsa la tecla de Windows y escribe "PowerShell".

2.  **Navega a la carpeta `backend`:**
    Usa el comando `cd` para moverte al directorio donde guardaste el proyecto.
    ```powershell
    cd ruta\a\tu\proyecto\chatbot_pedidos\backend
    ```

3.  **Crea un entorno virtual:**
    Este comando crea una carpeta llamada `venv` que contendrá todas las librerías específicas para este proyecto.
    ```powershell
    python -m venv venv
    ```

4.  **Activa el entorno virtual:**
    Es crucial activar el entorno antes de instalar nada.
    ```powershell
    .\venv\Scripts\activate
    ```
    Verás que `(venv)` aparece al principio de la línea de tu terminal.

5.  **Instala las dependencias:**
    Este comando instalará FastAPI, Uvicorn, OpenAI y las demás librerías necesarias.
    ```powershell
    pip install "fastapi[all]" uvicorn openai python-dotenv
    ```

6.  **Configura tu clave de API:**
    Dentro de la carpeta `backend`, crea un archivo de texto simple, llámalo `.env` y escribe dentro tu clave de API de OpenAI.
    ```
    OPENAI_API_KEY="tu_clave_secreta_aqui"
    ```

### 3. Ejecución del Proyecto

1.  **Inicia el servidor Backend:**
    Asegúrate de que la terminal sigue en la carpeta `backend` y el entorno `(venv)` está activo. Luego, ejecuta:
    ```powershell
    uvicorn main:app --reload
    ```
    El servidor se iniciará. Verás un mensaje que dice `Uvicorn running on http://127.0.0.1:8000`.

2.  **Inicia el Frontend:**
    Navega a la carpeta `frontend` y simplemente haz doble clic en el archivo `index.html`. Se abrirá en tu navegador web predeterminado.

¡Y listo! El chatbot debería estar funcionando y listo para tomar pedidos.
