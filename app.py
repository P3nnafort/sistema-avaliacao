from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime

app = Flask(__name__)
CORS(app)

SUPABASE_URL = 'https://neacrwveqwijlhygscrn.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lYWNyd3ZlcXdpamxoeWdzY3JuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2ODczMTUsImV4cCI6MjA1OTI2MzMxNX0.WOcU9ef6QJClWTo6i3REz_n-DCWQYg5L3Tfn2rCTYng'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rotas de páginas
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

@app.route('/lista_presenca.html')
def serve_lista_presenca():
    return send_file('lista_presenca.html')

@app.route('/ata_ocorrencias.html')
def serve_ata_ocorrencias():
    return send_file('ata_ocorrencias.html')

@app.route('/visualizar_ocorrencias.html')
def serve_visualizar_ocorrencias():
    return send_file('visualizar_ocorrencias.html')

# Rotas de API
@app.route('/verificar_matricula', methods=['POST'])
def verificar_matricula():
    print("Rota /verificar_matricula chamada")
    try:
        data = request.get_json()
        if not data or 'matricula' not in data:
            print("Erro: Dados inválidos ou matrícula ausente")
            return jsonify({"status": "error", "message": "Matrícula não fornecida"}), 400
        
        matricula = data['matricula']
        print(f"Verificando matrícula: {matricula}")
        
        response = supabase.table('alunos').select('*').eq('matricula', matricula).execute()
        if not response.data:
            print("Matrícula não encontrada no banco")
            return jsonify({"status": "error", "message": "Matrícula não encontrada"}), 404
        
        aluno = response.data[0]
        turma_response = supabase.table('presencas').select('estado_prova').eq('turma', aluno['turma']).eq('unidade', aluno['unidade']).order('data', desc=True).limit(1).execute()
        
        if turma_response.data:
            estado = turma_response.data[0]['estado_prova']
            print(f"Estado da prova para {matricula}: {estado}")
            if estado == 'pendente':
                return jsonify({"status": "error", "message": "Esperar o aplicador iniciar a prova"})
            elif estado == 'iniciada':
                resultado_response = supabase.table('resultados').select('matricula, acertos, total, porcentagem, respostas, portugues_acertos, portugues_total, portugues_porcentagem, matematica_acertos, matematica_total, matematica_porcentagem').eq('matricula', matricula).execute()
                if resultado_response.data:
                    print(f"Resultado encontrado para {matricula}, prova ainda iniciada")
                    return jsonify({"status": "error", "message": "Aguarde a prova finalizar"})
                else:
                    print(f"Prova iniciada, permitindo continuação para {matricula}")
                    return jsonify({"status": "success", "aluno": aluno})
            elif estado == 'finalizada':
                resultado_response = supabase.table('resultados').select('matricula, acertos, total, porcentagem, respostas, portugues_acertos, portugues_total, portugues_porcentagem, matematica_acertos, matematica_total, matematica_porcentagem').eq('matricula', matricula).execute()
                if resultado_response.data:
                    resultado = resultado_response.data[0]
                    questoes_response = supabase.table('questoes').select('*').eq('etapa', aluno['etapa']).execute()
                    print(f"Prova finalizada, retornando resultado para {matricula}")
                    return jsonify({
                        "status": "finalizada",
                        "aluno": aluno,
                        "resultado": resultado,
                        "questoes": questoes_response.data
                    })
                else:
                    print(f"Prova finalizada, mas sem resultado para {matricula}")
                    return jsonify({"status": "error", "message": "Resultado não encontrado após finalização"})
        print(f"Nenhum estado de prova encontrado para {matricula}, permitindo início")
        return jsonify({"status": "success", "aluno": aluno})
    except Exception as e:
        print(f"Erro interno em /verificar_matricula: {str(e)}")
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

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

@app.route('/salvar_questao', methods=['POST'])
def salvar_questao():
    try:
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
        nivel_dificuldade = request.form['nivel_dificuldade']
        descritor = request.form['descritor']
        habilidade = request.form['habilidade']
        autor = request.form['autor']
        imagem = request.files.get('imagem')
        imagem_path = None
        
        print(f"Salvando questão - Disciplina: {disciplina}, Nível: {nivel_dificuldade}, Descritor: {descritor}, Habilidade: {habilidade}, Autor: {autor}")
        
        if imagem:
            temp_dir = 'uploads'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            temp_path = os.path.join(temp_dir, imagem.filename)
            imagem.save(temp_path)
            with open(temp_path, 'rb') as f:
                supabase.storage.from_('uploads').upload(imagem.filename, f)
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
            "nivel_dificuldade": nivel_dificuldade,
            "descritor": descritor,
            "habilidade": habilidade,
            "autor": autor,
            "imagem": imagem_path
        }
        
        response = supabase.table('questoes').insert(questao).execute()
        return jsonify({"status": "success", "message": "Questão salva com sucesso"})
    except Exception as e:
        print(f"Erro ao salvar questão: {str(e)}")
        return jsonify({"status": "error", "message": f"Erro ao salvar questão: {str(e)}"}), 500

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
    nome_avaliacao = request.args.get('nome_avaliacao')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    # Buscar resultados da unidade
    resultados_query = supabase.table('resultados').select('*').eq('unidade', unidade)
    if nome_avaliacao:
        resultados_query = resultados_query.eq('nome_avaliacao', nome_avaliacao)
    if etapa:
        resultados_query = resultados_query.eq('etapa', etapa)
    if turma:
        resultados_query = resultados_query.eq('turma', turma)
    resultados = resultados_query.execute().data
    
    # Buscar questões relacionadas aos resultados
    questoes_query = supabase.table('questoes').select('identificador, habilidade, etapa, nome_avaliacao')
    if etapa:
        questoes_query = questoes_query.eq('etapa', etapa)
    if nome_avaliacao:
        questoes_query = questoes_query.eq('nome_avaliacao', nome_avaliacao)
    questoes = questoes_query.execute().data
    
    # Buscar alunos da unidade pra calcular ausentes
    alunos_query = supabase.table('alunos').select('matricula').eq('unidade', unidade)
    if etapa:
        alunos_query = alunos_query.eq('etapa', etapa)
    if turma:
        alunos_query = alunos_query.eq('turma', turma)
    alunos = alunos_query.execute().data
    
    # Calcular participantes e ausentes
    participantes = len(resultados)
    total_alunos = len(alunos)
    ausentes = total_alunos - participantes
    
    # Calcular médias por disciplina
    portugues_total = sum(r['portugues_acertos'] for r in resultados if r['portugues_total'] > 0)
    portugues_possivel = sum(r['portugues_total'] for r in resultados if r['portugues_total'] > 0)
    matematica_total = sum(r['matematica_acertos'] for r in resultados if r['matematica_total'] > 0)
    matematica_possivel = sum(r['matematica_total'] for r in resultados if r['matematica_total'] > 0)
    
    media_portugues = (portugues_total / portugues_possivel * 100) if portugues_possivel > 0 else 0
    media_matematica = (matematica_total / matematica_possivel * 100) if matematica_possivel > 0 else 0
    
    # Buscar avaliações disponíveis
    avaliacoes_query = supabase.table('resultados').select('nome_avaliacao').eq('unidade', unidade).execute()
    avaliacoes = sorted(set(r.get('nome_avaliacao', 'Sem Avaliação') for r in avaliacoes_query.data if r.get('nome_avaliacao')))
    
    # Buscar etapas disponíveis
    etapas_query = supabase.table('resultados').select('etapa').eq('unidade', unidade).execute()
    etapas = sorted(set(r['etapa'] for r in etapas_query.data))
    
    # Buscar turmas disponíveis (filtradas por etapa se selecionada)
    turmas_query = supabase.table('resultados').select('turma').eq('unidade', unidade)
    if etapa:
        turmas_query = turmas_query.eq('etapa', etapa)
    turmas = sorted(set(r['turma'] for r in turmas_query.execute().data))
    
    return jsonify({
        "resultados": resultados,
        "questoes": questoes,
        "avaliacoes": avaliacoes,
        "etapas": etapas,
        "turmas": turmas,
        "participantes": participantes,
        "ausentes": ausentes,
        "media_portugues": media_portugues,
        "media_matematica": media_matematica
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
    nome_avaliacao = request.args.get('nome_avaliacao')
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    
    usuario_response = supabase.table('coordenadores').select('*').eq('cpf', cpf).execute()
    if not usuario_response.data:
        return jsonify({"resultados": [], "questoes": [], "avaliacoes": [], "unidades": [], "etapas": [], "turmas": [], "participantes": 0, "ausentes": 0, "media_portugues": 0, "media_matematica": 0})
    
    etapas_permitidas = usuario_response.data[0]['etapas'].split(',')
    
    # Buscar resultados
    resultados_query = supabase.table('resultados').select('*').in_('etapa', etapas_permitidas)
    if nome_avaliacao:
        resultados_query = resultados_query.eq('nome_avaliacao', nome_avaliacao)
    if unidade:
        resultados_query = resultados_query.eq('unidade', unidade)
    if etapa:
        resultados_query = resultados_query.eq('etapa', etapa)
    if turma:
        resultados_query = resultados_query.eq('turma', turma)
    resultados = resultados_query.execute().data
    
    # Buscar questões relacionadas aos resultados
    questoes_query = supabase.table('questoes').select('identificador, habilidade, etapa, nome_avaliacao').in_('etapa', etapas_permitidas)
    if nome_avaliacao:
        questoes_query = questoes_query.eq('nome_avaliacao', nome_avaliacao)
    if etapa:
        questoes_query = questoes_query.eq('etapa', etapa)
    questoes = questoes_query.execute().data
    
    # Buscar alunos pra calcular ausentes
    alunos_query = supabase.table('alunos').select('matricula').in_('etapa', etapas_permitidas)
    if unidade:
        alunos_query = alunos_query.eq('unidade', unidade)
    if etapa:
        alunos_query = alunos_query.eq('etapa', etapa)
    if turma:
        alunos_query = alunos_query.eq('turma', turma)
    alunos = alunos_query.execute().data
    
    # Calcular participantes e ausentes
    participantes = len(resultados)
    total_alunos = len(alunos)
    ausentes = total_alunos - participantes
    
    # Calcular médias por disciplina
    portugues_total = sum(r['portugues_acertos'] for r in resultados if r['portugues_total'] > 0)
    portugues_possivel = sum(r['portugues_total'] for r in resultados if r['portugues_total'] > 0)
    matematica_total = sum(r['matematica_acertos'] for r in resultados if r['matematica_total'] > 0)
    matematica_possivel = sum(r['matematica_total'] for r in resultados if r['matematica_total'] > 0)
    
    media_portugues = (portugues_total / portugues_possivel * 100) if portugues_possivel > 0 else 0
    media_matematica = (matematica_total / matematica_possivel * 100) if matematica_possivel > 0 else 0
    
    # Buscar avaliações disponíveis
    avaliacoes_query = supabase.table('resultados').select('nome_avaliacao').in_('etapa', etapas_permitidas).execute()
    avaliacoes = sorted(set(r.get('nome_avaliacao', 'Sem Avaliação') for r in avaliacoes_query.data if r.get('nome_avaliacao')))
    
    # Buscar unidades disponíveis
    unidades_query = supabase.table('resultados').select('unidade').in_('etapa', etapas_permitidas).execute()
    unidades = sorted(set(r['unidade'] for r in unidades_query.data))
    
    # Buscar etapas disponíveis
    etapas_query = supabase.table('resultados').select('etapa').in_('etapa', etapas_permitidas).execute()
    etapas = sorted(set(r['etapa'] for r in etapas_query.data))
    
    # Buscar turmas disponíveis (filtradas por etapa se selecionada)
    turmas_query = supabase.table('resultados').select('turma').in_('etapa', etapas_permitidas)
    if etapa:
        turmas_query = turmas_query.eq('etapa', etapa)
    turmas = sorted(set(r['turma'] for r in turmas_query.execute().data))
    
    return jsonify({
        "resultados": resultados,
        "questoes": questoes,
        "avaliacoes": avaliacoes,
        "unidades": unidades,
        "etapas": etapas,
        "turmas": turmas,
        "participantes": participantes,
        "ausentes": ausentes,
        "media_portugues": media_portugues,
        "media_matematica": media_matematica
    })

@app.route('/salvar_resultado', methods=['POST'])
def salvar_resultado():
    print("Rota /salvar_resultado chamada")
    try:
        data = request.get_json()
        if not data:
            print("Erro: Nenhum dado recebido na requisição")
            return jsonify({"status": "error", "message": "Nenhum dado enviado"}), 400
        
        matricula = data.get('matricula')
        nome = data.get('nome')
        unidade = data.get('unidade')
        etapa = data.get('etapa')
        turma = data.get('turma')
        respostas = data.get('respostas')
        questoes = data.get('questoes')

        if not all([matricula, nome, unidade, etapa, turma, respostas, questoes]):
            print(f"Erro: Dados incompletos - Matrícula: {matricula}, Nome: {nome}, Unidade: {unidade}, Etapa: {etapa}, Turma: {turma}")
            return jsonify({"status": "error", "message": "Dados incompletos"}), 400

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
            "matematica_porcentagem": matematica_porcentagem,
            "nome_avaliacao": questoes[0]['nome_avaliacao'] if questoes else "Sem Avaliação"
        }
        
        print(f"Salvando resultado para matrícula: {matricula}")
        supabase.table('resultados').insert(resultado).execute()
        
        print("Resultado salvo com sucesso")
        return jsonify({"status": "success", "message": "Prova finalizada, aguarde todos finalizarem."})
    except Exception as e:
        print(f"Erro interno em /salvar_resultado: {str(e)}")
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

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

@app.route('/upload_informativo', methods=['POST'])
def upload_informativo():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"}), 400
    
    temp_dir = 'informativos'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)
    with open(temp_path, 'rb') as f:
        supabase.storage.from_('informativos').upload(file.filename, f)
    os.remove(temp_path)
    file_url = supabase.storage.from_('informativos').get_public_url(file.filename)
    
    informativo = {"filename": file.filename, "url": file_url}
    supabase.table('informativos').insert(informativo).execute()
    
    return jsonify({"status": "success", "message": "Informativo enviado com sucesso"})

@app.route('/listar_informativos')
def listar_informativos():
    response = supabase.table('informativos').select('filename, url').execute()
    arquivos = [{"filename": item['filename'], "url": item['url']} for item in response.data]
    return jsonify({"arquivos": arquivos})

@app.route('/upload_avaliacao_fisica', methods=['POST'])
def upload_avaliacao_fisica():
    if 'file' not in request.files or 'etapa' not in request.form:
        return jsonify({"status": "error", "message": "Arquivo ou etapa não fornecido"}), 400
    file = request.files['file']
    etapa = request.form['etapa']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"}), 400
    
    filename = f"Etapa-{etapa}-{file.filename}"
    temp_dir = 'avaliacoes_fisicas'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_path = os.path.join(temp_dir, filename)
    file.save(temp_path)
    with open(temp_path, 'rb') as f:
        supabase.storage.from_('avaliacoes-fisicas').upload(filename, f)
    os.remove(temp_path)
    file_url = supabase.storage.from_('avaliacoes-fisicas').get_public_url(filename)
    
    avaliacao_fisica = {"filename": filename, "etapa": etapa, "url": file_url}
    supabase.table('avaliacoes_fisicas').insert(avaliacao_fisica).execute()
    
    return jsonify({"status": "success", "message": "Avaliação física enviada com sucesso"})

@app.route('/listar_avaliacoes_fisicas')
def listar_avaliacoes_fisicas():
    response = supabase.table('avaliacoes_fisicas').select('filename, url').execute()
    arquivos = sorted(
        [{"filename": item['filename'], "url": item['url']} for item in response.data],
        key=lambda x: int(x['filename'].split('-')[1]) if x['filename'].startswith('Etapa-') else float('inf')
    )
    return jsonify({"arquivos": arquivos})

@app.route('/lista_presenca', methods=['POST'])
def lista_presenca():
    data = request.get_json()
    senha = data.get('senha')
    print(f"Senha recebida: {senha}")
    try:
        turma, unidade_id = senha.split('_')
        unidade_id = int(unidade_id)
        print(f"Turma: {turma}, Unidade ID: {unidade_id}")
    except ValueError:
        print("Erro: Formato de senha inválido")
        return jsonify({"status": "error", "message": "Senha inválida. Use o formato TURMA_UNIDADEID (ex.: 600_1)"})

    unidade_response = supabase.table('unidades').select('nome').eq('id', unidade_id).execute()
    if not unidade_response.data:
        print(f"Unidade ID {unidade_id} não encontrada")
        return jsonify({"status": "error", "message": "Unidade não encontrada"})

    unidade_nome = unidade_response.data[0]['nome']
    print(f"Unidade encontrada: {unidade_nome}")
    response = supabase.table('alunos').select('nome, matricula, unidade, etapa, turma').eq('turma', turma).eq('unidade', unidade_nome).execute()
    print(f"Alunos encontrados: {len(response.data) if response.data else 0}")
    if response.data:
        today = datetime.now().strftime('%Y-%m-%d')
        existing = supabase.table('presencas').select('id').eq('turma', turma).eq('unidade', unidade_nome).gte('data', f"{today} 00:00:00").lte('data', f"{today} 23:59:59").execute()
        print(f"Presenças existentes hoje: {len(existing.data) if existing.data else 0}")
        if not existing.data:
            presencas = [{"turma": turma, "matricula": aluno['matricula'], "unidade": unidade_nome, "presenca": "A", "data": "now()", "estado_prova": "pendente"} for aluno in response.data]
            print(f"Inserindo {len(presencas)} presenças")
            supabase.table('presencas').insert(presencas).execute()
        return jsonify({"status": "success", "alunos": response.data})
    return jsonify({"status": "error", "message": "Turma ou unidade não encontrada"})

@app.route('/salvar_presenca', methods=['POST'])
def salvar_presenca():
    print("Rota /salvar_presenca chamada")
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")
        if not data:
            print("Erro: Nenhum dado recebido na requisição")
            return jsonify({"status": "error", "message": "Nenhum dado enviado"}), 400
        
        turma = data.get('turma')
        unidade = data.get('unidade')
        presencas = data.get('presencas', [])
        estado = data.get('estado')
        
        if not turma or not unidade or not estado:
            print(f"Erro: Dados incompletos - Turma: {turma}, Unidade: {unidade}, Estado: {estado}")
            return jsonify({"status": "error", "message": "Dados incompletos (turma, unidade ou estado faltando)"}), 400

        print(f"Salvando presenças - Turma: {turma}, Unidade: {unidade}, Estado: {estado}, Presenças: {len(presencas)}")
        
        today = datetime.now().strftime('%Y-%m-%d')
        for presenca in presencas:
            matricula = presenca.get('matricula')
            presenca_valor = presenca.get('presenca')
            if not matricula or not presenca_valor:
                print(f"Erro: Presença inválida - Matrícula: {matricula}, Presença: {presenca_valor}")
                return jsonify({"status": "error", "message": "Dados de presença inválidos"}), 400
            print(f"Atualizando matrícula: {matricula} com presenca: {presenca_valor}")
            supabase.table('presencas').update({"presenca": presenca_valor, "estado_prova": estado}).eq('turma', turma).eq('unidade', unidade).eq('matricula', matricula).gte('data', f"{today} 00:00:00").lte('data', f"{today} 23:59:59").execute()
        
        if estado == "finalizada" and not presencas:
            print(f"Finalizando prova sem presenças")
            supabase.table('presencas').update({"estado_prova": estado}).eq('turma', turma).eq('unidade', unidade).gte('data', f"{today} 00:00:00").lte('data', f"{today} 23:59:59").execute()
        
        print("Presenças salvas com sucesso")
        return jsonify({"status": "success", "message": f"Presença salva e prova {estado}"})
    except Exception as e:
        print(f"Erro interno ao salvar presenças: {str(e)}")
        return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

@app.route('/salvar_ocorrencia', methods=['POST'])
def salvar_ocorrencia():
    data = request.get_json()
    turma = data.get('turma')
    unidade = data.get('unidade')
    texto = data.get('texto', "Sem ocorrência")
    print(f"Salvando ocorrência - Turma: {turma}, Unidade: {unidade}")
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"ATA de Ocorrências - Turma: {turma}")
    c.drawString(100, 730, f"Unidade: {unidade}")
    c.drawString(100, 710, f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 690, "Ocorrência:")
    texto_lines = texto.split('\n')
    y = 670
    for line in texto_lines:
        c.drawString(100, y, line)
        y -= 20
    c.showPage()
    c.save()
    buffer.seek(0)
    
    pdf_filename = f"ocorrencia_{turma}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    supabase.storage.from_('ocorrencias').upload(pdf_filename, buffer.read())
    pdf_url = supabase.storage.from_('ocorrencias').get_public_url(pdf_filename)
    
    ocorrencia = {"turma": turma, "unidade": unidade, "data": "now()", "texto": texto, "pdf_url": pdf_url}
    supabase.table('ocorrencias').insert(ocorrencia).execute()
    
    return jsonify({"status": "success", "message": "Ocorrência salva com sucesso"})

@app.route('/listar_ocorrencias')
def listar_ocorrencias():
    unidade = request.args.get('unidade')
    etapa = request.args.get('etapa')
    turma = request.args.get('turma')
    tipo = request.args.get('tipo')
    
    query = supabase.table('ocorrencias').select('turma, unidade, data, pdf_url')
    
    if tipo == "unidade" and unidade:
        query = query.eq('unidade', unidade)
    if etapa:
        query = query.eq('etapa', etapa)
    if turma:
        query = query.eq('turma', turma)
    
    response = query.execute()
    return jsonify({"ocorrencias": response.data})

@app.route('/visualizar_avaliacao_restrita.html')
def serve_visualizar_avaliacao_restrita():
    return send_file('visualizar_avaliacao_restrita.html')

@app.route('/listar_avaliacoes_restritas')
def listar_avaliacoes_restritas():
    cpf = request.args.get('cpf')
    if not cpf:
        return jsonify({"status": "error", "message": "CPF não fornecido"}), 400
    
    # Verificar as etapas permitidas do usuário
    response = supabase.table('coordenadores').select('etapas').eq('cpf', cpf).execute()
    if not response.data:
        return jsonify({"status": "error", "message": "CPF não encontrado ou sem permissão"}), 404
    
    etapas_permitidas = response.data[0]['etapas'].split(',')
    
    # Listar avaliações apenas para as etapas permitidas
    response = supabase.table('questoes').select('nome_avaliacao, etapa').in_('etapa', etapas_permitidas).execute()
    avaliacoes = sorted(set(f"{q['nome_avaliacao']} - {q['etapa']}" for q in response.data))
    return jsonify({"avaliacoes": avaliacoes})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)