import schedule
import time
import requests
import os
import openai
from datetime import datetime
from flask import Flask, request, jsonify
import threading

# === VARIÁVEIS DE AMBIENTE ===
INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# === URL DA Z-API ===
API_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{TOKEN}/send-messages"

# === LISTA DE DESTINATÁRIOS PARA O MENU DIÁRIO ===
DESTINATARIOS = ['5511983260077', '5511996898090', '5514996144947']

# === MENSAGEM DE MENU ===
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

# === PERGUNTAS ENVIADAS PARA O CHATGPT COM BASE NA OPÇÃO ===
PERGUNTAS = {
    "1": "Gere um relatório técnico atualizado e resumido do Bitcoin (BTC), incluindo médias móveis, RSI, suporte, resistência e volume.",
    "2": "Projeção de curto prazo para o Bitcoin, considerando análise técnica, sentimento de mercado e eventos recentes.",
    "3": "Principais notícias e estratégias atuais para operar com Bitcoin no contexto do dia.",
    "4": "Gere um relatório detalhado do Bitcoin com análise em 4 camadas: técnica básica, indicadores avançados, sentimento de mercado e contexto macro.",
    "5": "Gere um relatório completo e estratégico do Bitcoin consolidando análise técnica, projeção, sentimento e notícias."
}

# === ENVIA MENSAGEM PARA O WHATSAPP VIA Z-API ===
def enviar_mensagem(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }
    try:
        r = requests.post(API_URL, json=payload)
        print(f"[{datetime.now()}] Enviado para {numero} | Status: {r.status_code}")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

# === GERA RESPOSTA DA IA ===
def gerar_resposta(pergunta):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista financeiro e técnico especializado em criptomoedas. Gere respostas detalhadas, claras e confiáveis."},
                {"role": "user", "content": pergunta}
            ]
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar a OpenAI: {e}"

# === FLASK APP ===
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receber():
    data = request.get_json()
    numero = data.get("phone")
    mensagem = data.get("message", "").strip().lower()

    if mensagem in PERGUNTAS:
        resposta = gerar_resposta(PERGUNTAS[mensagem])
    elif mensagem in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "menu", "btc", "relatório", "relatorio"]:
        resposta = MENSAGEM_MENU
    else:
        resposta = (
            "👋 Olá! Para acessar os relatórios BTC, digite uma das opções abaixo:\n\n"
            "1️⃣ Relatório Técnico\n2️⃣ Projeção de Curto Prazo\n3️⃣ Últimas notícias\n"
            "4️⃣ Relatório Detalhado PRO\n5️⃣ Relatório completo BTC\n\n"
            "Ou apenas envie 'menu' para receber novamente a lista 😉"
        )

    enviar_mensagem(numero, resposta)
    return jsonify({"status": "ok"})

# === ENVIO AUTOMÁTICO DO MENU ÀS 08:00 ===
def tarefa_diaria():
    for numero in DESTINATARIOS:
        enviar_mensagem(numero, MENSAGEM_MENU)

# === THREAD PARA AGENDAMENTO + SERVIDOR ===
def agendar():
    schedule.every().day.at("08:00").do(tarefa_diaria)
    print("⏳ Aguardando 08:00 para enviar o menu diário...")
    while True:
        schedule.run_pending()
        time.sleep(30)

# === INICIALIZAÇÃO DO APP ===
if __name__ == "__main__":
    threading.Thread(target=agendar).start()
    app.run(host="0.0.0.0", port=8080)
