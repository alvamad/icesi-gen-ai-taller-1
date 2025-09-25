import os
import csv
import json
import textwrap
from datetime import datetime
from openai import OpenAI

# --- Config OpenAI ---
OPENAI_MODEL = "gpt-4o-mini"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Cargar pedidos del CSV en memoria ---
def load_orders(path="data/orders.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # normaliza JSON de items si viene como string
            items = r.get("items", "[]")
            if isinstance(items, str):
                try:
                    r["items"] = json.loads(items)
                except json.JSONDecodeError:
                    r["items"] = []
            rows.append(r)
    return rows

ORDERS = load_orders()

def build_orders_block(orders):
    # Texto compacto con los pedidos, para meter al prompt como "contexto"
    lines = []
    for o in orders:
        line = (
            f"- {o['tracking_number']}: status={o['status']}; eta={o['eta']}; "
            f"url={o['carrier_url']}; items={o['items']}; notes={o['notes']}"
        )
        lines.append(line)
    return "\n".join(lines)

ORDERS_BLOCK = build_orders_block(ORDERS)

def render_template(tpl: str, **kwargs) -> str:
    out = tpl
    for k, v in kwargs.items():
        out = out.replace("{{" + k + "}}", str(v))
    return textwrap.dedent(out).strip()

# --- Cargar prompts desde archivos ---
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = read_file("prompts/system_agent.txt")
ORDER_PROMPT  = read_file("prompts/order_status_prompt.txt")
RETURN_PROMPT = read_file("prompts/returns_prompt.txt")

def ask_openai(messages, temperature=0.4, max_tokens=300):
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens, 
    )
    return resp.choices[0].message.content

# --- Ejercicio 1: Estado de pedido ---
def order_status(tracking_number: str):
    user_prompt = render_template(
        ORDER_PROMPT,
        tracking_number=tracking_number,
        orders_block=ORDERS_BLOCK
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    return ask_openai(messages)

# --- Ejercicio 2: Devoluciones ---
def returns_flow(tracking_number: str, reason: str):
    user_prompt = render_template(
        RETURN_PROMPT,
        tracking_number=tracking_number,
        reason=reason,
        orders_block=ORDERS_BLOCK
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    return ask_openai(messages)

if __name__ == "__main__":

    print("=== Estado de pedido ===")
    print(order_status("EMK-10003"))

    print("\n=== Devoluciones ===")
    print(returns_flow("EMK-10002", "El producto llegó en mal estado"))
