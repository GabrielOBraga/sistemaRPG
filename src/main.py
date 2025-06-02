import sys
import os
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

import re

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy.exc import SQLAlchemyError
import json
import os
from src.models import Character, Session, SessionLocal, Base, engine

# Criar a aplicação Flask
app = Flask(__name__)
app.secret_key = 'rpg_panel_secret_key'  # Necessário para flash messages

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Função para converter string de data para objeto date
def parse_date(date_str):
    """Converte string de data para objeto date ou retorna a data atual se inválido."""
    if not date_str:
        return datetime.date.today()
    
    try:
        # Tenta converter a string para objeto date
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # Se falhar, retorna a data atual
        return datetime.date.today()


@app.template_filter('regex_replace')
def regex_replace(s, find, replace):
    return re.sub(find, replace, s)


# Rota principal - exibe o painel com todos os personagens
@app.route('/')
def index():
    # Obter uma sessão do banco de dados
    db = SessionLocal()
    
    # Converter para o formato esperado pelo template
    characters_data = []

    try:
        # Buscar todos os personagens
        characters = db.query(Character).all()
        
        for char in characters:
            # Definir a cor do card com base no nome ou classe do personagem (lógica simplificada)
            card_colors = {
                'Melissa': 'info',
                'Escanor': 'warning',
                'Lord': 'primary',
                'Emberith': 'danger',
                'Duromak': 'success',
                'Milenaus': 'secondary'
            }
            
            # Obter a cor do card ou usar secondary como padrão
            first_name = char.name.split()[0] if char.name else ''
            card_color = card_colors.get(first_name, 'secondary')
            
            print(first_name)
            print(card_color)


            # Adicionar o personagem à lista
            characters_data.append({
                'id': char.id,  # Adiciona o ID para permitir edição e exclusão
                'name': char.name,
                'hp': char.hp,
                'ac': char.ac,
                'inspiration': char.inspiration,
                'slots': char.slots,
                'abilities': char.abilities,
                'notes': char.notes,
                'card_color': card_color,
                'text_color': 'white',  # Padrão para a maioria das cores
                'spellStone': char.slots.get('spellStone', None)  # Verifica se tem pedra de armazenamento
            })
                
        # Renderizar o template com os dados
        return render_template('index_dynamic.html', characters=characters_data)
    
    except Exception as e:
        # Em caso de erro, exibir mensagem e retornar template vazio
        flash(f'Erro ao carregar personagens: {str(e)}', 'danger')
        return render_template('index_dynamic.html', characters=[])
        
    
    finally:
        # Fechar a sessão do banco de dados
        db.close()

# Rota para exibir o formulário de cadastro de personagem
@app.route('/character/new')
def new_character():
    return render_template('character_form.html')

# Rota para editar um personagem existente
@app.route('/character/edit/<int:character_id>')
def edit_character(character_id):
    db = SessionLocal()
    try:
        # Buscar o personagem pelo ID
        character = db.query(Character).filter_by(id=character_id).first()
        
        if not character:
            flash('Personagem não encontrado', 'danger')
            return redirect(url_for('index'))
        
        # Renderizar o template de edição com os dados do personagem
        return render_template('character_edit.html', character=character)
    
    except Exception as e:
        flash(f'Erro ao carregar personagem: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
    finally:
        db.close()

# Rota para atualizar um personagem existente
@app.route('/character/update/<int:character_id>', methods=['POST'])
def update_character(character_id):
    db = SessionLocal()
    try:
        # Buscar o personagem pelo ID
        character = db.query(Character).filter_by(id=character_id).first()
        
        if not character:
            flash('Personagem não encontrado', 'danger')
            return redirect(url_for('index'))
        
        # Atualizar os dados do personagem
        character.name = request.form.get('name')
        character.hp = int(request.form.get('hp', 0))
        character.ac = int(request.form.get('ac', 0))
        character.inspiration = 'inspiration' in request.form
        character.notes = request.form.get('notes', '')
        
        # Processar os dados JSON
        slots_json = request.form.get('slots_json', '{}')
        abilities_json = request.form.get('abilities_json', '{}')
        spell_stone_json = request.form.get('spell_stone_json', '{}')
        
        # Converter strings JSON para dicionários Python
        character.slots = json.loads(slots_json)
        character.abilities = json.loads(abilities_json)
        
        # Verificar se o personagem tem pedra de armazenamento
        if 'has_spell_stone' in request.form and request.form.get('has_spell_stone') == 'on':
            spell_stone = json.loads(spell_stone_json)
            # Adicionar a pedra de armazenamento aos slots
            character.slots['spellStone'] = spell_stone
        
        # Salvar as alterações
        db.commit()
        
        # Exibir mensagem de sucesso
        flash(f'Personagem {character.name} atualizado com sucesso!', 'success')
        
        # Redirecionar para a página principal
        return redirect(url_for('index'))
    
    except SQLAlchemyError as e:
        # Em caso de erro de banco de dados, fazer rollback
        db.rollback()
        flash(f'Erro ao atualizar personagem: {str(e)}', 'danger')
        return redirect(url_for('edit_character', character_id=character_id))
    
    except Exception as e:
        # Em caso de outros erros
        flash(f'Erro ao processar formulário: {str(e)}', 'danger')
        return redirect(url_for('edit_character', character_id=character_id))
    
    finally:
        # Fechar a sessão do banco de dados
        db.close()

# Rota para excluir um personagem
@app.route('/character/delete/<int:character_id>', methods=['POST'])
def delete_character(character_id):
    db = SessionLocal()
    try:
        # Buscar o personagem pelo ID
        character = db.query(Character).filter_by(id=character_id).first()
        
        if not character:
            flash('Personagem não encontrado', 'danger')
            return redirect(url_for('index'))
        
        # Armazenar o nome para a mensagem
        character_name = character.name
        
        # Excluir o personagem
        db.delete(character)
        db.commit()
        
        # Exibir mensagem de sucesso
        flash(f'Personagem {character_name} excluído com sucesso!', 'success')
        
        # Redirecionar para a página principal
        return redirect(url_for('index'))
    
    except SQLAlchemyError as e:
        # Em caso de erro de banco de dados, fazer rollback
        db.rollback()
        flash(f'Erro ao excluir personagem: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
    except Exception as e:
        # Em caso de outros erros
        flash(f'Erro ao processar exclusão: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
    finally:
        # Fechar a sessão do banco de dados
        db.close()

# Rota para salvar um novo personagem
@app.route('/character/save', methods=['POST'])
def save_character():
    # Obter uma sessão do banco de dados
    db = SessionLocal()
    
    try:
        # Obter os dados do formulário
        name = request.form.get('name')
        hp = int(request.form.get('hp', 0))
        ac = int(request.form.get('ac', 0))
        inspiration = 'inspiration' in request.form
        notes = request.form.get('notes', '')
        
        # Processar os dados JSON
        slots_json = request.form.get('slots_json', '{}')
        abilities_json = request.form.get('abilities_json', '{}')
        spell_stone_json = request.form.get('spell_stone_json', '{}')
        
        # Converter strings JSON para dicionários Python
        slots = json.loads(slots_json)
        abilities = json.loads(abilities_json)
        
        # Verificar se o personagem tem pedra de armazenamento
        if 'has_spell_stone' in request.form and request.form.get('has_spell_stone') == 'on':
            spell_stone = json.loads(spell_stone_json)
            # Adicionar a pedra de armazenamento aos slots
            slots['spellStone'] = spell_stone
        
        # Criar o objeto Character
        character = Character(
            name=name,
            hp=hp,
            ac=ac,
            inspiration=inspiration,
            slots=slots,
            abilities=abilities,
            notes=notes
        )
        
        # Adicionar à sessão e salvar no banco
        db.add(character)
        db.commit()
        
        # Exibir mensagem de sucesso
        flash(f'Personagem {name} cadastrado com sucesso!', 'success')
        
        # Redirecionar para a página principal
        return redirect(url_for('index'))
    
    except SQLAlchemyError as e:
        # Em caso de erro de banco de dados, fazer rollback
        db.rollback()
        flash(f'Erro ao salvar personagem: {str(e)}', 'danger')
        return redirect(url_for('new_character'))
    
    except Exception as e:
        # Em caso de outros erros
        flash(f'Erro ao processar formulário: {str(e)}', 'danger')
        return redirect(url_for('new_character'))
    
    finally:
        # Fechar a sessão do banco de dados
        db.close()

# Rota para API de dados (para uso com JavaScript)
@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'GET':
        # Obter dados do banco
        db = SessionLocal()
        try:
            # Buscar todos os personagens
            characters = db.query(Character).all()
            
            # Criar dicionário de personagens
            characters_dict = {}
            for char in characters:
                characters_dict[char.name.lower()] = {
                    'id': char.id,  # Adicionando o ID para permitir edição
                    'hp': char.hp,
                    'ac': char.ac,
                    'inspiration': char.inspiration,
                    'slots': char.slots,
                    'abilities': char.abilities,
                    'notes': char.notes
                }
            
            # Buscar a sessão mais recente
            latest_session = db.query(Session).order_by(Session.number.desc()).first()
            
            # Buscar todas as sessões para o histórico
            all_sessions = db.query(Session).order_by(Session.number.desc()).all()
            history = []
            
            # Converter sessões para o formato esperado pelo frontend
            for session in all_sessions:
                # Não incluir a sessão atual no histórico
                if latest_session and session.id == latest_session.id:
                    continue
                
                history.append({
                    'id': session.id,
                    'number': session.number,
                    'date': session.date.isoformat() if session.date else '',
                    'floorName': session.floorName or '',
                    'notes': session.notes or ''
                })
            
            # Criar objeto de resposta
            response_data = {
                'success': True,
                'data': {
                    'session': {
                        'number': latest_session.number if latest_session else 1,
                        'date': latest_session.date.isoformat() if latest_session else datetime.date.today().isoformat(),
                        'floorName': latest_session.floorName if latest_session else '',
                        'notes': latest_session.notes if latest_session else ''
                    },
                    'characters': characters_dict,
                    'history': history
                }
            }
            
            return jsonify(response_data)
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        
        finally:
            db.close()
    
    elif request.method == 'POST':
        # Receber dados do cliente e salvar no banco
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'message': 'Dados inválidos'})
        
        db = SessionLocal()
        try:
            # Atualizar a sessão
            session_data = data.get('session', {})
            session_number = session_data.get('number', 1)
            
            # Processar a data corretamente
            date_str = session_data.get('date', '')
            session_date = parse_date(date_str)
            
            # Buscar a sessão ou criar uma nova
            session = db.query(Session).filter_by(number=session_number).first()
            if not session:
                session = Session(
                    number=session_number,
                    date=session_date,
                    floorName=session_data.get('floorName', ''),
                    notes=session_data.get('notes', '')
                )
                db.add(session)
            else:
                session.date = session_date
                session.floorName = session_data.get('floorName', session.floorName)
                session.notes = session_data.get('notes', session.notes)
            
            # Atualizar os personagens
            characters_data = data.get('characters', {})
            for char_name, char_data in characters_data.items():
                # Buscar o personagem ou criar um novo
                character = db.query(Character).filter_by(name=char_name).first()
                if not character:
                    character = Character(
                        name=char_name,
                        hp=char_data.get('hp', 0),
                        ac=char_data.get('ac', 0),
                        inspiration=char_data.get('inspiration', False),
                        slots=char_data.get('slots', {}),
                        abilities=char_data.get('abilities', {}),
                        notes=char_data.get('notes', '')
                    )
                    db.add(character)
                else:
                    character.hp = char_data.get('hp', character.hp)
                    character.ac = char_data.get('ac', character.ac)
                    character.inspiration = char_data.get('inspiration', character.inspiration)
                    character.slots = char_data.get('slots', character.slots)
                    character.abilities = char_data.get('abilities', character.abilities)
                    character.notes = char_data.get('notes', character.notes)
            
            # Atualizar o histórico de sessões
            history_data = data.get('history', [])

            for session_info in history_data:
                # Verificar se a sessão já existe
                session_number = session_info.get('number')
                session = db.query(Session).filter_by(number=session_number).first()

                if not session:
                    # Criar nova sessão de histórico
                    sessionH = Session(
                        number=session_info.get('number'),
                        date=parse_date(session_info.get('date')),
                        floorName=session_info.get('floorName'),
                        notes=session_info.get('notes')
                    )
                    db.add(sessionH)
                    db.flush()  # Flush para garantir que o ID seja gerado antes de criar o histórico
  
                else:
                    # Atualizar sessão existente
                    session.number=session_info.get('number')
                    session.date=parse_date(session_info.get('date'))
                    session.floorName=session_info.get('floorName')
                    session.notes=session_info.get('notes')

            # Salvar as alterações
            db.commit()
            
            return jsonify({'success': True, 'message': 'Dados atualizados com sucesso'})
        
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)})
        
        finally:
            db.close()

# Rota para importar dados do banco de dados de um json
@app.route('/import', methods=['GET', 'POST'])
def import_data():
    if request.method == 'GET':
        return render_template('import_api.html')
    else:
        file = request.files.get('json_file')
        if not file or not file.filename.endswith('.json'):
            flash('Selecione um arquivo JSON válido.', 'danger')
            return redirect(url_for('import_page'))
        try:
            data = json.load(file)
            # Chama a lógica de importação já existente
            db = SessionLocal()
            try:
                db.query(Character).delete()
                db.query(Session).delete()
                db.commit()

                sessions = data.get('history', [])
                session_atual = data.get('session')
                if session_atual:
                    sessions.append(session_atual)
                for session_info in sessions:
                    session = Session(
                        id=session_info.get('id', None),
                        number=session_info.get('number'),
                        date=parse_date(session_info.get('date')),
                        floorName=session_info.get('floorName', ''),
                        notes=session_info.get('notes', '')
                    )
                    db.add(session)
                db.flush()

                characters = data.get('characters', {})
                for char_name, char_data in characters.items():
                    character = Character(
                        id=char_data.get('id', None),
                        name=char_name,
                        hp=char_data.get('hp', 0),
                        ac=char_data.get('ac', 0),
                        inspiration=char_data.get('inspiration', False),
                        slots=char_data.get('slots', {}),
                        abilities=char_data.get('abilities', {}),
                        notes=char_data.get('notes', '')
                    )
                    db.add(character)
                db.commit()
                flash('Banco de dados importado com sucesso!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.rollback()
                flash(f'Erro ao importar: {str(e)}', 'danger')
                return redirect(url_for('import_page'))
            finally:
                db.close()
        except Exception as e:
            flash(f'Erro ao ler o arquivo: {str(e)}', 'danger')
            return redirect(url_for('import_page'))



# Iniciar a aplicação se este arquivo for executado diretamente
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
