from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
sessions = {}  # Armazena sessões de usuários

@app.route("/")
def dashboard():
    return render_template("dashboard.html", users=sessions)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')

    if sender not in sessions:
        sessions[sender] = {"step": 0}

    session = sessions[sender]

    if session["step"] == 0:
        session["step"] = 1
        response = "Olá! Qual é o seu nome?"
    elif session["step"] == 1:
        session["name"] = incoming_msg.strip()
        session["step"] = 2
        response = f"Prazer, {session['name']}! Como posso ajudar?"
    else:
        response = f"{session['name']}, você disse: '{incoming_msg}' — já estamos analisando."

    sessions[sender] = session

    reply = MessagingResponse()
    reply.message(response)
    return str(reply)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)