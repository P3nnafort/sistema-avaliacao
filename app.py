from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
import os

app = Flask(__name__)
CORS(app)

# Configuração do Supabase
SUPABASE_URL = 'https://neacrwveqwijlhygscrn.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lYWNyd3ZlcXdpamxoeWdzY3JuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2ODczMTUsImV4cCI6MjA1OTI2MzMxNX0.WOcU9ef6QJClWTo6i3REz_n-DCWQYg5L3Tfn2rCTYng'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Pastas locais temporárias (ainda necessárias pro upload)
UPLOAD_FOLDER = 'uploads'
INFORMATIVOS_FOLDER = 'informativos'
AVALIACOES_FISICAS_FOLDER = 'avaliacoes_fisicas'  # Mantém local como está, mas bucket muda
for folder in [UPLOAD_FOLDER, INFORMATIVOS_FOLDER, AVALIACOES_FISICAS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['INFORMATIVOS_FOLDER'] = INFORMATIVOS_FOLDER
app.config['AVALIACOES_FISICAS_FOLDER'] = AVALIACOES_FISICAS_FOLDER

# Rotas de páginas (inalteradas, apenas listando pra contexto)
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

@app.route('/escolha_avaliacao_unidade.html')
def serve_escolha_avaliacao_unidade():
    return send_file('escolha_avaliacao_unidade.html')

@app.route('/casa_avaliacao.html')
def serve_casa_avaliacao():
    return send_file('casa_avaliacao.html')

@app.route('/escolha_avaliacao_casa.html')
def serve_escolha_avaliacao_casa():
    return send_file('escolha_avaliacao_casa.html')

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

@app.route('/informativos_unidade.html')
def serve_informativos_unidade():
    return send_file('informativos_unidade.html')

@app.route('/informativos_casa.html')
def serve_informativos_casa():
    return send_file('informativos_casa.html')

@app.route('/avaliacoes_fisicas_unidade.html')
def serve_avaliacoes_fisicas_unidade():
    return send_file('avaliacoes_fisicas_unidade.html')

@app.route('/avaliacoes_fisicas_casa.html')
def serve_avaliacoes_fisicas_casa():
    return send_file('avaliacoes_fisicas_casa.html')

@app.route('/resultado.html')
def serve_resultado():
    return send_file('resultado.html')

# Rotas de API (apenas as ajustadas pra Supabase Storage)
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
        temp_path = os.path.join('uploads', imagem.filename)
        imagem.save(temp_path)
        with open(temp_path, 'rb') as f:
            upload_response = supabase.storage.from_('uploads').upload(imagem.filename, f)
        os.remove(temp_path)
        imagem_path = supabase.storage.from_('uploads').get_public_url(imagem.filename)
    
    questao = {
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
    
    response = supabase.table('questoes').insert(questao).execute()
    return jsonify({"status": "success", "message": "Questão salva com sucesso"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    url = supabase.storage.from_('uploads').get_public_url(filename)
    return jsonify({"url": url})

@app.route('/upload_informativo', methods=['POST'])
def upload_informativo():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"}), 400
    
    temp_path = os.path.join('informativos', file.filename)
    file.save(temp_path)
    with open(temp_path, 'rb') as f:
        upload_response = supabase.storage.from_('informativos').upload(file.filename, f)
    os.remove(temp_path)
    file_url = supabase.storage.from_('informativos').get_public_url(file.filename)
    
    informativo = {"filename": file.filename, "url": file_url}
    supabase.table('informativos').insert(informativo).execute()
    
    return jsonify({"status": "success", "message": "Informativo enviado com sucesso"})

@app.route('/listar_informativos')
def listar_informativos():
    response = supabase.table('informativos').select('filename').execute()
    arquivos = [item['filename'] for item in response.data]
    return jsonify({"arquivos": arquivos})

@app.route('/informativos/<filename>')
def download_informativo(filename):
    url = supabase.storage.from_('informativos').get_public_url(filename)
    return jsonify({"url": url})

@app.route('/upload_avaliacao_fisica', methods=['POST'])
def upload_avaliacao_fisica():
    if 'file' not in request.files or 'etapa' not in request.form:
        return jsonify({"status": "error", "message": "Arquivo ou etapa não fornecido"}), 400
    file = request.files['file']
    etapa = request.form['etapa']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"}), 400
    
    filename = f"Etapa-{etapa}-{file.filename}"  # Ajustado pra evitar "_"
    temp_path = os.path.join('avaliacoes_fisicas', filename)
    file.save(temp_path)
    with open(temp_path, 'rb') as f:
        upload_response = supabase.storage.from_('avaliacoes-fisicas').upload(filename, f)
    os.remove(temp_path)
    file_url = supabase.storage.from_('avaliacoes-fisicas').get_public_url(filename)
    
    avaliacao_fisica = {"filename": filename, "etapa": etapa, "url": file_url}
    supabase.table('avaliacoes_fisicas').insert(avaliacao_fisica).execute()
    
    return jsonify({"status": "success", "message": "Avaliação física enviada com sucesso"})

@app.route('/listar_avaliacoes_fisicas')
def listar_avaliacoes_fisicas():
    response = supabase.table('avaliacoes_fisicas').select('filename').execute()
    arquivos = sorted([item['filename'] for item in response.data], key=lambda x: int(x.split('-')[1]) if x.startswith('Etapa-') else float('inf'))
    return jsonify({"arquivos": arquivos})

@app.route('/avaliacoes_fisicas/<filename>')
def download_avaliacao_fisica(filename):
    url = supabase.storage.from_('avaliacoes-fisicas').get_public_url(filename)
    return jsonify({"url": url})

# Outras rotas permanecem inalteradas
@app.route('/verificar_matricula', methods=['POST'])
def verificar_matricula():
    data = request.get_json()
    matricula = data.get('matricula')
    response = supabase.table('alunos').select('*').eq('matricula', matricula).execute()
    if response.data:
        return jsonify({"status": "success", "aluno": response.data[0]})
    return jsonify({"status": "error", "message": "Matrícula não encontrada"})

@app.route('/carregar_questoes')
def carregar_questoes():
    etapa = request.args.get('etapa')
    disciplina = request.args.get('disciplina')
    nome_avaliacao = request.args.get('nome_avaliacao')
    
    query = supabase.table('questoes').select('*').eq('etapa', etapa)
    if nome_avaliacao and disciplina:
        query = query.eq('nome_avaliacao', nome_avaliacao).eq('disciplina', disciplina)
    elif disciplina:
        query = query.eq('disciplina', disciplina)
    
    response = query.execute()
    return jsonify(response.data)

@app.route('/verificar_cpf_unidade', methods=['POST'])
def verificar_cpf_unidade():
    data = request.get_json()
    cpf = data.get('cpf')
    response = supabase.table('diretores').select('*').eq('cpf', cpf).execute()
    if response.data:
        return jsonify({"status": "success", "unidade": response.data[0]['unidade']})
    return jsonify({"status": "error", "message": "CPF não encontrado ou sem permissão"})

@app.route('/resultados_unidade')
def resultados_unidade():
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    resultados_query = supabase.table('resultados').select('*').eq('unidade', unidade)
    if etapa:
        resultados_query = resultados_query.eq('etapa', etapa)
    if turma:
        resultados_query = resultados_query.eq('turma', turma)
    resultados = resultados_query.execute().data
    
    alunos_query = supabase.table('alunos').select('*').eq('unidade', unidade)
    if etapa:
        alunos_query = alunos_query.eq('etapa', etapa)
    if turma:
        alunos_query = alunos_query.eq('turma', turma)
    alunos_unidade = alunos_query.execute().data
    
    fizeram = len(resultados)
    ausentes = len(alunos_unidade) - fizeram
    
    etapas_query = supabase.table('alunos').select('etapa').eq('unidade', unidade).execute()
    etapas = sorted(set(a['etapa'] for a in etapas_query.data))
    
    turmas_query = supabase.table('alunos').select('turma').eq('unidade', unidade)
    if etapa:
        turmas_query = turmas_query.eq('etapa', etapa)
    turmas = sorted(set(a['turma'] for a in turmas_query.execute().data))
    
    return jsonify({
        "resultados": resultados,
        "fizeram": fizeram,
        "ausentes": ausentes,
        "etapas": etapas,
        "turmas": turmas
    })

@app.route('/verificar_cpf_casa', methods=['POST'])
def verificar_cpf_casa():
    data = request.get_json()
    cpf = data.get('cpf')
    response = supabase.table('coordenadores').select('*').eq('cpf', cpf).execute()
    if response.data:
        usuario = response.data[0]
        return jsonify({"status": "success", "etapas": usuario['etapas'], "disciplinas": usuario['disciplinas']})
    return jsonify({"status": "error", "message": "CPF não encontrado ou sem permissão"})

@app.route('/resultados_casa')
def resultados_casa():
    cpf = request.args.get('cpf')
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    usuario_response = supabase.table('coordenadores').select('*').eq('cpf', cpf).execute()
    if not usuario_response.data:
        return jsonify({"resultados": [], "fizeram": 0, "ausentes": 0, "unidades": [], "etapas": [], "turmas": []})
    
    etapas_permitidas = usuario_response.data[0]['etapas'].split(',')
    resultados_query = supabase.table('resultados').select('*').in_('etapa', etapas_permitidas)
    if unidade:
        resultados_query = resultados_query.eq('unidade', unidade)
    if etapa:
        resultados_query = resultados_query.eq('etapa', etapa)
    if turma:
        resultados_query = resultados_query.eq('turma', turma)
    resultados = resultados_query.execute().data
    
    alunos_query = supabase.table('alunos').select('*').in_('etapa', etapas_permitidas)
    if unidade:
        alunos_query = alunos_query.eq('unidade', unidade)
    if etapa:
        alunos_query = alunos_query.eq('etapa', etapa)
    if turma:
        alunos_query = alunos_query.eq('turma', turma)
    alunos_casa = alunos_query.execute().data
    
    fizeram = len(resultados)
    ausentes = len(alunos_casa) - fizeram
    
    unidades = sorted(set(a['unidade'] for a in alunos_casa))
    etapas = sorted(set(a['etapa'] for a in alunos_casa))
    turmas_query = supabase.table('alunos').select('turma').in_('etapa', etapas_permitidas)
    if etapa:
        turmas_query = turmas_query.eq('etapa', etapa)
    turmas = sorted(set(a['turma'] for a in turmas_query.execute().data))
    
    return jsonify({
        "resultados": resultados,
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
    
    supabase.table('resultados').insert(resultado).execute()
    
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
    response = supabase.table('coordenadores').select('etapas').eq('cpf', cpf).execute()
    if response.data:
        etapas = response.data[0]['etapas'].split(',')
        return jsonify({"status": "success", "etapas": etapas})
    return jsonify({"status": "error", "message": "CPF não encontrado"})

@app.route('/carregar_avaliacao_completa')
def carregar_avaliacao_completa():
    etapa = request.args.get('etapa')
    nome_avaliacao = request.args.get('nome_avaliacao')
    response = supabase.table('questoes').select('*').eq('etapa', etapa).eq('nome_avaliacao', nome_avaliacao).execute()
    return jsonify(response.data)

@app.route('/listar_avaliacoes')
def listar_avaliacoes():
    response = supabase.table('questoes').select('nome_avaliacao, etapa').execute()
    avaliacoes = sorted(set(f"{q['nome_avaliacao']} - {q['etapa']}" for q in response.data))
    return jsonify({"avaliacoes": avaliacoes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)