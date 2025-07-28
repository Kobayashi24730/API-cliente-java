from flask import Flask, jsonify, request, abort
import psycopg2
import os

app = Flask(__name__)
TOKEN = "Meu_token"
DATABASE_URL = os.environ.get("DATABASE_URL")

def conectar():
	return psycopg2.connect(DATABASE_URL)

def criar_tabela():
	conn = conectar()
	cursor = conn.cursor()
	cursor.execute('''
                          CREATE TABLE IF NOT EXISTS sensores(
			     id SERIAL PRIMARY KEY,
			     nome TEXT NOT NULL,
			     valor TEXT NOT NULL
		            )
			''')
	conn.commit()
	conn.close()

def iniciar_dados_iniciais():
	dados = [
			("Água A1","7.2"),
			("Água B1","8.2"),
			("Água C1","6.2")
  ]
	conn = conectar()
	cursor = conn.cursor()
	for nome,valor in dados:
		cursor.execute("INSERT INTO sensores (nome,valor) VALUES (%s,%s)", (nome,valor))
	conn.commmit()
	conn.close()

# inicialização tantos dos dados iniciais quanto do db
iniciar_dados_iniciais()
criar_tabela()

@app.route("/dados", methods=["GET"])
def get_dados():
	if request.headers.get("Authorization") != f"Bearer{TOKEN}":
		abort(401,"Token invalido!")
		
	conn = conectar()
	cursor = conn.cursor()
	cursor.execute("SELECT name, valor FROM sensores")
	rows = cursor.fetchall()
	conn.close()
	
	return jsonify ([{"nome": r[o],"valor": r[1]} for r in rows])
	
@app.route("/dados", methods=["POST"])
def add_dados():
	if request.headers.get("Authorization") != f"Bearer {TOKEN}":
		abort(401,"Token invalido")
	
	data = request.get_json()
	nome = data.get("nome")
	valor = data.get("valor")
	
	conn = conectar()
	cursor = conn.cursor()
	cursor.execute("INSERT INTO sensores (nome,valor) VALUES (%s,%s)", (nome,valor))
	conn.commit()
	conn.close()
	
	return jsonify({"Messagem": "Dados inseridos com sucesso!"}),201
	
if __name__ == "__main__":
	app.run(debug=True)
