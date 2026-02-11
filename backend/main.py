# backend/main.py

# --- 1. IMPORTS ---
import os
import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# --- 2. INITIAL SETUP & CONFIGURATION ---
load_dotenv()
api_key_from_env = os.getenv("OPENAI_API_KEY")
if not api_key_from_env:
    raise ValueError("ERROR: La variable de entorno OPENAI_API_KEY no se encontró.")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
openai_client = OpenAI(api_key=api_key_from_env)
DATABASE_FILE = "pedidos.db"

# --- 3. DATABASE LOGIC (SQLite) ---
# (Esta sección no necesita cambios, la omito por brevedad, usa la que ya tienes)
def inicializar_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, direccion_entrega TEXT, fecha_pedido TEXT, precio_total REAL, estado TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS items_pedido (id INTEGER PRIMARY KEY, pedido_id INTEGER, nombre_producto TEXT, cantidad INTEGER, precio_unitario REAL, FOREIGN KEY (pedido_id) REFERENCES pedidos (id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, precio REAL, categoria TEXT, descripcion TEXT)")
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_iniciales = [
            ('Margarita', 10.0, 'Pizzas', ''), ('Pepperoni', 12.0, 'Pizzas', ''), ('Cuatro Quesos', 13.0, 'Pizzas', ''), ('Vegetal', 11.0, 'Pizzas', ''),
            ('Salsa', 1.0, 'Extras en pizza', ''), ('Queso', 0.5, 'Extras en pizza', ''), ('Borde relleno', 2.0, 'Extras en pizza', ''),
            ('Refresco de Cola', 2.0, 'Bebidas', ''), ('Agua', 1.5, 'Bebidas', ''), ('Cerveza', 2.5, 'Bebidas', ''),
            ('Tarta de Queso', 5.0, 'Postres', ''), ('Helado', 3.0, 'Postres', ''), ('Pan de ajo', 1.5, 'Extras', '')
        ]
        cursor.executemany("INSERT INTO productos (nombre, precio, categoria, descripcion) VALUES (?, ?, ?, ?)", productos_iniciales)
    conn.commit()
    conn.close()

def guardar_pedido_en_db(pedido_data: dict):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pedidos (direccion_entrega, fecha_pedido, precio_total) VALUES (?, ?, ?)", (pedido_data['address'], datetime.now().isoformat(), pedido_data['total_price']))
        pedido_id = cursor.lastrowid
        for item in pedido_data['items']:
            cursor.execute("INSERT INTO items_pedido (pedido_id, nombre_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)", (pedido_id, item['name'], item['quantity'], item['price']))
        conn.commit()
        return pedido_id
    except Exception as e:
        conn.rollback(); print(f"Error al guardar en la base de datos: {e}"); return None
    finally:
        conn.close()

# --- 4. DATA MODELS (Pydantic) ---
class ChatRequest(BaseModel):
    conversation_history: list[dict] = []

# --- 5. API ENDPOINTS ---
@app.on_event("startup")
def on_startup():
    print("Inicializando la base de datos...")
    inicializar_db()
    print("Base de datos lista.")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, precio FROM productos")
        menu_items = {row['nombre']: row['precio'] for row in cursor.fetchall()}
        menu_string = "\n".join([f"- {name} ({price}€)" for name, price in menu_items.items()])
        conn.close()

        # SIMPLIFIED PROMPT
        system_message_content = f"""
        Eres un asistente de pedidos. Tu única tarea es generar un objeto JSON que represente el estado del pedido del cliente basándote en la conversación.

        **MENÚ DISPONIBLE (nombre y precio unitario):**
        {menu_string}

        **INSTRUCCIÓN OBLIGATORIA:**
        Tu respuesta DEBE ser SIEMPRE un único objeto JSON, y nada más. No añadas texto conversacional. El JSON debe tener la siguiente estructura:
        {{"response_for_user": "Texto para mostrar al usuario.", "cart": {{"items": [{{"name": "Nombre Producto", "quantity": X, "price": Y}}], "total_price": Z, "address": "Dirección o null"}}}}

        **REGLAS DEL JSON:**
        1.  `response_for_user`: Un mensaje amable y corto para el usuario.
        2.  `cart`: El estado completo del carrito. Si no hay nada, `items` debe ser una lista vacía `[]`.
        3.  `price`: Debe ser siempre el PRECIO UNITARIO del producto según el menú.
        4.  `total_price`: La suma total correcta del carrito.

        Ejemplo de conversación:
        - Historial: [{{"role": "user", "content": "hola"}}]
        - Tu respuesta JSON: {{"response_for_user": "¡Hola! ¿Qué te gustaría pedir?", "cart": {{"items": [], "total_price": 0, "address": null}}}}

        - Historial: [{{"role": "user", "content": "hola"}}, {{"role": "assistant", "content": "{...}"}}, {{"role": "user", "content": "quiero 2 margaritas"}}]
        - Tu respuesta JSON: {{"response_for_user": "¡Añadidas 2 pizzas Margarita! ¿Algo más?", "cart": {{"items": [{{"name": "Margarita", "quantity": 2, "price": 10.0}}], "total_price": 20.0, "address": null}}}}
        """

        messages = [{"role": "system", "content": system_message_content}] + request.conversation_history

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"} # Force JSON output
        )
        
        # The entire response should be a single JSON string.
        response_data = json.loads(response.choices[0].message.content)
        
        # We directly return the JSON object that the AI generated.
        return response_data

    except Exception as e:
        print(f"Ha ocurrido un error CRÍTICO: {e}")
        # If something fails, return a valid structure so the frontend doesn't break.
        return {"response_for_user": "Lo siento, he tenido un problema interno. Por favor, inténtalo de nuevo.", "cart": {"items": [], "total_price": 0, "address": null}}