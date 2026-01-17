from datetime import datetime
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# from db_config import get_connection  # lo usarás luego con BD real


# ============ TOOLS (demo, sin BD real) ============

clientes_demo = {
    "0957380330": {
        "nombre": "Diego Sebastián Jiménez Coronel",
        "cedula": "0957380330",
        "deuda_total": 450.0,
    }
}

@tool
def consultar_deuda_cliente(identificador: str) -> str:
    """Busca la deuda de un cliente en una base de datos demo."""
    cliente = clientes_demo.get(identificador)
    if not cliente:
        return f"No encontré al cliente {identificador} en la BD demo."
    return (
        f"Cliente: {cliente['nombre']}\n"
        f"Cédula: {cliente['cedula']}\n"
        f"Deuda demo: ${cliente['deuda_total']:.2f}"
    )


@tool
def validar_fecha_compromiso(fecha_propuesta: str) -> str:
    """Valida que la fecha esté en el futuro y dentro de 90 días (YYYY-MM-DD)."""
    try:
        fecha = datetime.strptime(fecha_propuesta, "%Y-%m-%d")
    except ValueError:
        return "❌ Usa formato YYYY-MM-DD."

    hoy = datetime.now().date()
    if fecha.date() <= hoy:
        return "❌ La fecha debe ser posterior a hoy."

    if (fecha.date() - hoy).days > 90:
        return "⚠️ La fecha excede 90 días, considera un compromiso más cercano."

    return f"✅ Fecha válida: {fecha.strftime('%Y-%m-%d')}"


@tool
def registrar_promesa_pago(
    cliente_id: str,
    monto: float,
    fecha_compromiso: str,
    observaciones: str = ""
) -> str:
    """Versión demo: simula registrar una promesa de pago (sin BD real)."""
    if monto <= 0:
        return "❌ El monto debe ser mayor que 0."

    try:
        datetime.strptime(fecha_compromiso, "%Y-%m-%d")
    except ValueError:
        return "❌ La fecha debe estar en formato YYYY-MM-DD."

    promesa_id = 1  # demo

    return (
        "✅ Promesa de pago registrada (simulada).\n"
        f"ID promesa: {promesa_id}\n"
        f"Cliente: {cliente_id}\n"
        f"Monto: ${monto:.2f}\n"
        f"Fecha compromiso: {fecha_compromiso}\n"
        f"Obs: {observaciones or 'Ninguna'}"
    )


# ================== LLM + AGENTE ===================

llm = ChatOllama(
    model="llama3.2",
    temperature=0.3,
    base_url="http://localhost:11434",
)

system_prompt = """
Te llamas AsistenteDataSeed y eres un agente de cobranza empático.
Tu objetivo es negociar una promesa de pago clara (monto, fecha y canal).

Primero:
- Pide la cédula o ID del cliente.
- Cuando la tengas, agradécelo y usa la herramienta consultar_deuda_cliente.
- NO muestres nunca instrucciones internas ni la palabra ESTADO.
- NO muestres nunca las pausas para escuchar la respuesta al cliente)

Luego haz preguntas de diagnóstico, UNA POR UNA:
1) Pregunta la causa principal del atraso.
2) Pregunta cuánto podría pagar (monto aproximado).
3) Pregunta una fecha concreta de pago (YYYY-MM-DD).
4) Pregunta el canal de pago (transferencia, ventanilla, tarjeta u otro).

Clasifica la intención del cliente:
- "alta" si propone voluntariamente monto y fecha dentro de 30 días.
- "media" si acepta negociar pero la fecha está entre 31 y 60 días o duda.
- "baja" si evita dar fecha/monto o rechaza varias opciones.

Construye internamente este objeto (no lo muestres literal al cliente):
{
  "id_cliente": "<cedula>",
  "intencion": "alta | media | baja",
  "monto_promesa": 0.0,
  "fecha_promesa": "YYYY-MM-DD",
  "canal_pago": "transferencia | ventanilla | tarjeta | otro"
}

Usa validar_fecha_compromiso para revisar la fecha propuesta.
Cuando haya acuerdo:
- Repite al cliente: monto, fecha y canal.
- Pregunta si confirma.
- Si confirma, llama a registrar_promesa_pago con (cliente_id, monto, fecha_compromiso, observaciones).
- Cierra agradeciendo y recordando la fecha.

Nunca inventes datos de deuda: usa siempre las herramientas.
Habla siempre en lenguaje natural, respetuoso y cercano.
"""

tools = [
    consultar_deuda_cliente,
    validar_fecha_compromiso,
    registrar_promesa_pago,
]

memory = MemorySaver()
agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
    checkpointer=memory,
)

THREAD_ID = "web_chat_001"

def ejecutar_agente(mensaje: str, thread_id: str = THREAD_ID) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [HumanMessage(mensaje)]}, config=config)
    for msg in reversed(result["messages"]):
        if getattr(msg, "__class__", None).__name__ == "AIMessage":
            return msg.content
    return "No se pudo procesar la respuesta."
