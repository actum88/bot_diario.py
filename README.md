# bot-bitcoin-zapi-ai
Bot para envio diário de relatórios BTC via Z-API com IA
import schedule
import time
import requests
import os
import openai
from datetime import datetime

INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

API_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-messages"

DESTINATARIOS = [
    '5511983260077', '5511996898090', '5514996144947'
]

def gerar_relatorio_com_ia(pergunta):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista financeiro e técnico especializado em Bitcoin. Gere relatórios objetivos, mas completos."},
                {"role": "user", "content": pergunta}
            ]
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {e}"

MENSAGEM_MENU = """
👋 Bom dia!

Quer acompanhar o mercado do Bitcoin?

Escolha uma opção:
1️⃣ Relatório Técnico BTC (agora)
2️⃣ Projeção de curto prazo
3️⃣ Últimas notícias e estratégias
4️⃣ Relatório Detalhado PRO 🧠
5️⃣ Relatório completo BTC (tudo em um só)

Responda com o número da opção desejada 😉
"""

def enviar_mensagem(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    try:
        r = requests.post(API_URL, json=payload)
        print(f"[{datetime.now()}] Enviado para {numero} | Status: {r.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para {numero}: {e}")

def tarefa_diaria():
    for numero in DESTINATARIOS:
        enviar_mensagem(numero, MENSAGEM_MENU)

from flask import Flask, request, jsonify
app = Flask(__name__)

PERGUNTAS = {
    "1": "Gere um relatório técnico atualizado e resumido do Bitcoin (BTC), incluindo médias móveis, RSI, suporte, resistência e volume.",
    "2": "Projeção de curto prazo para o Bitcoin, considerando análise técnica, sentimento de mercado e eventos recentes.",
    "3": "Principais notícias e estratégias atuais para operar com Bitcoin no contexto do dia.",
    "4": "Gere um relatório detalhado do Bitcoin com análise em 4 camadas: técnica básica, indicadores avançados, sentimento de mercado e contexto macro.",
    "5": "Gere um relatório completo e estratégico do Bitcoin consolidando análise técnica, projeção, sentimento e notícias."
}

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    data = request.get_json()
    mensagem = data.get("message", "").strip()
    numero = data.get("phone")

    if mensagem in PERGUNTAS:
        pergunta = PERGUNTAS[mensagem]
        resposta = gerar_relatorio_com_ia(pergunta)
    else:
        resposta = MENSAGEM_MENU

    enviar_mensagem(numero, resposta)
    return jsonify({"status": "ok"})

import threading

def iniciar_agendador():
    schedule.every().day.at("08:00").do(tarefa_diaria)
    print("⏳ Aguardando 08:00 para enviar o menu diário...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=iniciar_agendador).start()
    app.run(host="0.0.0.0", port=8080)
