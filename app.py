from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import csv
import json

app = Flask(__name__)
CORS(app)

alunos = []
questoes = []
resultados = []
servidores = []
casa_avaliacao = []

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def carregar_csv():
    global alunos, servidores, casa_avaliacao
    with open('alunos.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        alunos.extend([{"matricula": row['matricula'], "nome": row['nome'], "unidade": row['unidade'], 
                        "etapa": row['etapa'], "turma": row['turma']} for row in reader])
    with open('diretores.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        servidores.extend([{"cpf": row['cpf'], "nome": row['nome'], "unidade": row['unidade']} for row in reader])
    with open('coordenadores.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        casa_avaliacao.extend([{"cpf": row['cpf'], "nome": row['nome'], "etapas": row['etapas'], 
                                "disciplinas": row['disciplinas']} for row in reader])

@app.route('/')
@app.route('/index.html')
def serve_index():
    return send_file('index.html')

@app.route('/realizar_prova.html')
def serve_realizar_prova():
    return send_file('realizar_prova.html')

@app.route('/resultados_unidade.html')
def serve_resultados_unidade():
    return send_file('resultados_unidade.html')

@app.route('/opcoes_unidade.html')
def serve_opcoes_unidade():
    return send_file('opcoes_unidade.html')

@app.route('/casa_avaliacao.html')
def serve_casa_avaliacao():
    return send_file('casa_avaliacao.html')

@app.route('/resultados_casa.html')
def serve_resultados_casa():
    return send_file('resultados_casa.html')

@app.route('/criar_prova.html')
def serve_criar_prova():
    return send_file('criar_prova.html')

@app.route('/visualizar_prova.html')
def serve_visualizar_prova():
    return send_file('visualizar_prova.html')

@app.route('/visualizar_avaliacao.html')
def serve_visualizar_avaliacao():
    return send_file('visualizar_avaliacao.html')

@app.route('/resultado.html')
def serve_resultado():
    return send_file('resultado.html')

@app.route('/verificar_matricula', methods=['POST'])
def verificar_matricula():
    data = request.get_json()
    matricula = data.get('matricula')
    aluno = next((a for a in alunos if a['matricula'] == matricula), None)
    if aluno:
        return jsonify({"status": "success", "aluno": aluno})
    return jsonify({"status": "error", "message": "Matrícula não encontrada"})

@app.route('/carregar_questoes')
def carregar_questoes():
    etapa = request.args.get('etapa')
    disciplina = request.args.get('disciplina')
    nome_avaliacao = request.args.get('nome_avaliacao')
    if nome_avaliacao and disciplina:
        filtered_questoes = [q for q in questoes if q['nome_avaliacao'] == nome_avaliacao and q['disciplina'] == disciplina and q['etapa'] == etapa]
    elif disciplina:
        filtered_questoes = [q for q in questoes if q['disciplina'] == disciplina and q['etapa'] == etapa]
    else:
        filtered_questoes = [q for q in questoes if q['etapa'] == etapa]
    return jsonify(filtered_questoes)

@app.route('/salvar_questao', methods=['POST'])
def salvar_questao():
    etapa = request.form['etapa']
    disciplina = request.form['disciplina']
    nome_avaliacao = request.form['nome_avaliacao']
    pergunta = request.form['pergunta']
    pergunta_complementar = request.form.get('pergunta_complementar', '')
    opcao_a = request.form['opcao_a']
    opcao_b = request.form['opcao_b']
    opcao_c = request.form['opcao_c']
    opcao_d = request.form['opcao_d']
    resposta_correta = request.form['resposta_correta']
    imagem = request.files.get('imagem')
    imagem_path = None
    if imagem:
        imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename)
        imagem.save(imagem_path)
        imagem_path = f"/uploads/{imagem.filename}"
    
    questao = {
        "id": len(questoes) + 1,
        "etapa": etapa,
        "disciplina": disciplina,
        "nome_avaliacao": nome_avaliacao,
        "identificador": f"{nome_avaliacao} - {disciplina} - {etapa}",
        "pergunta": pergunta,
        "pergunta_complementar": pergunta_complementar,
        "opcao_a": opcao_a,
        "opcao_b": opcao_b,
        "opcao_c": opcao_c,
        "opcao_d": opcao_d,
        "resposta_correta": resposta_correta,
        "imagem": imagem_path
    }
    questoes.append(questao)
    return jsonify({"status": "success", "message": "Questão salva com sucesso"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/verificar_cpf_unidade', methods=['POST'])
def verificar_cpf_unidade():
    data = request.get_json()
    cpf = data.get('cpf')
    servidor = next((s for s in servidores if s['cpf'] == cpf), None)
    if servidor:
        return jsonify({"status": "success", "unidade": servidor['unidade']})
    return jsonify({"status": "error", "message": "CPF não encontrado ou sem permissão"})

@app.route('/resultados_unidade')
def resultados_unidade():
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    filtered_resultados = [r for r in resultados if r['unidade'] == unidade]
    if etapa:
        filtered_resultados = [r for r in filtered_resultados if r['etapa'] == etapa]
    if turma:
        filtered_resultados = [r for r in filtered_resultados if r['turma'] == turma]
    
    alunos_unidade = [a for a in alunos if a['unidade'] == unidade]
    if etapa:
        alunos_unidade = [a for a in alunos_unidade if a['etapa'] == etapa]
    if turma:
        alunos_unidade = [a for a in alunos_unidade if a['turma'] == turma]
    
    fizeram = len(filtered_resultados)
    ausentes = len(alunos_unidade) - fizeram
    
    etapas = sorted(set(a['etapa'] for a in alunos_unidade))
    turmas = sorted(set(a['turma'] for a in alunos_unidade if etapa and a['etapa'] == etapa or not etapa))
    
    return jsonify({
        "resultados": filtered_resultados,
        "fizeram": fizeram,
        "ausentes": ausentes,
        "etapas": etapas,
        "turmas": turmas
    })

@app.route('/verificar_cpf_casa', methods=['POST'])
def verificar_cpf_casa():
    data = request.get_json()
    cpf = data.get('cpf')
    usuario = next((u for u in casa_avaliacao if u['cpf'] == cpf), None)
    if usuario:
        return jsonify({"status": "success", "etapas": usuario['etapas'], "disciplinas": usuario['disciplinas']})
    return jsonify({"status": "error", "message": "CPF não encontrado ou sem permissão"})

@app.route('/resultados_casa')
def resultados_casa():
    cpf = request.args.get('cpf')
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    usuario = next((u for u in casa_avaliacao if u['cpf'] == cpf), None)
    if not usuario:
        return jsonify({"resultados": [], "fizeram": 0, "ausentes": 0, "unidades": [], "etapas": [], "turmas": []})
    
    etapas_permitidas = usuario['etapas'].split(',')
    filtered_resultados = [r for r in resultados if r['etapa'] in etapas_permitidas]
    if unidade:
        filtered_resultados = [r for r in filtered_resultados if r['unidade'] == unidade]
    if etapa:
        filtered_resultados = [r for r in filtered_resultados if r['etapa'] == etapa]
    if turma:
        filtered_resultados = [r for r in filtered_resultados if r['turma'] == turma]
    
    alunos_casa = [a for a in alunos if a['etapa'] in etapas_permitidas]
    if unidade:
        alunos_casa = [a for a in alunos_casa if a['unidade'] == unidade]
    if etapa:
        alunos_casa = [a for a in alunos_casa if a['etapa'] == etapa]
    if turma:
        alunos_casa = [a for a in alunos_casa if a['turma'] == turma]
    
    fizeram = len(filtered_resultados)
    ausentes = len(alunos_casa) - fizeram
    
    unidades = sorted(set(a['unidade'] for a in alunos_casa))
    etapas = sorted(set(a['etapa'] for a in alunos_casa if a['etapa'] in etapas_permitidas))
    turmas = sorted(set(a['turma'] for a in alunos_casa if etapa and a['etapa'] == etapa or not etapa))
    
    return jsonify({
        "resultados": filtered_resultados,
        "fizeram": fizeram,
        "ausentes": ausentes,
        "unidades": unidades,
        "etapas": etapas,
        "turmas": turmas
    })

@app.route('/salvar_resultado', methods=['POST'])
def salvar_resultado():
    data = request.get_json()
    matricula = data.get('matricula')
    nome = data.get('nome')
    unidade = data.get('unidade')
    etapa = data.get('etapa')
    turma = data.get('turma')
    respostas = data.get('respostas')
    questoes = data.get('questoes')

    acertos = 0
    total = len(questoes)
    portugues_acertos = 0
    portugues_total = 0
    matematica_acertos = 0
    matematica_total = 0

    for i, questao in enumerate(questoes):
        resposta_aluno = respostas.get(f"q{i}")
        if resposta_aluno == questao['resposta_correta']:
            acertos += 1
            if questao['disciplina'] == "Língua Portuguesa":
                portugues_acertos += 1
            elif questao['disciplina'] == "Matemática":
                matematica_acertos += 1
        if questao['disciplina'] == "Língua Portuguesa":
            portugues_total += 1
        elif questao['disciplina'] == "Matemática":
            matematica_total += 1

    porcentagem = (acertos / total * 100) if total > 0 else 0
    portugues_porcentagem = (portugues_acertos / portugues_total * 100) if portugues_total > 0 else 0
    matematica_porcentagem = (matematica_acertos / matematica_total * 100) if matematica_total > 0 else 0

    resultado = {
        "matricula": matricula,
        "nome": nome,
        "unidade": unidade,
        "etapa": etapa,
        "turma": turma,
        "acertos": acertos,
        "total": total,
        "porcentagem": porcentagem,
        "respostas": respostas,
        "portugues_acertos": portugues_acertos,
        "portugues_total": portugues_total,
        "portugues_porcentagem": portugues_porcentagem,
        "matematica_acertos": matematica_acertos,
        "matematica_total": matematica_total,
        "matematica_porcentagem": matematica_porcentagem
    }
    resultados.append(resultado)

    return jsonify({
        "status": "success",
        "matricula": matricula,
        "nome": nome,
        "unidade": unidade,
        "etapa": etapa,
        "turma": turma,
        "acertos": acertos,
        "total": total,
        "porcentagem": porcentagem,
        "portugues_acertos": portugues_acertos,
        "portugues_total": portugues_total,
        "portugues_porcentagem": portugues_porcentagem,
        "matematica_acertos": matematica_acertos,
        "matematica_total": matematica_total,
        "matematica_porcentagem": matematica_porcentagem
    })

@app.route('/etapas_permitidas', methods=['POST'])
def etapas_permitidas():
    data = request.get_json()
    cpf = data.get('cpf')
    usuario = next((u for u in casa_avaliacao if u['cpf'] == cpf), None)
    if usuario:
        etapas = usuario['etapas'].split(',')
        return jsonify({"status": "success", "etapas": etapas})
    return jsonify({"status": "error", "message": "CPF não encontrado"})

@app.route('/carregar_avaliacao_completa')
def carregar_avaliacao_completa():
    etapa = request.args.get('etapa')
    nome_avaliacao = request.args.get('nome_avaliacao')
    filtered_questoes = [q for q in questoes if q['etapa'] == etapa and q['nome_avaliacao'] == nome_avaliacao]
    return jsonify(filtered_questoes)

if __name__ == '__main__':
    carregar_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)