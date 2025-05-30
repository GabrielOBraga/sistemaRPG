
# Painel de Sessão de RPG (D&D 5e)

Este projeto é um painel web completo para o gerenciamento de sessões e personagens em mesas de RPG, especialmente Dungeons & Dragons 5ª edição. Ele permite controlar atributos, recursos diários e progresso de sessões, com persistência local via banco SQLite.

---

## 🧰 Tecnologias Utilizadas

- **Frontend:** HTML + Bootstrap 5 + JavaScript Vanilla
- **Backend:** Flask (Python 3.11+)
- **Banco de Dados:** SQLite com SQLAlchemy ORM

---

## 📦 Conteúdo do Projeto

- **Interface Responsiva:** Painel web com visual dinâmico e interativo
- **Salvamento Persistente:** Dados salvos localmente com SQLite
- **Editor de Personagens:** Criação e edição completa via formulário
- **API REST:** Para integração com JavaScript ou outras aplicações
- **Sessões de Jogo:** Histórico, exportação, descanso longo, painel de notas

---

## ✅ Requisitos

- Python 3.11+
- Navegador web moderno
- (Opcional) Ferramenta como DB Browser for SQLite

---

## 🚀 Instalação

1. Clone ou extraia este repositório
2. Crie um ambiente virtual Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute o app:
   ```bash
   python -m src.main
   ```

---

## 🌐 Acesso ao Painel

Após iniciar o app, acesse:

```
http://localhost:5000
```

---

## 🗂️ Estrutura do Projeto

```
rpg_panel/
│
├── src/
│   ├── main.py              # Arquivo principal do Flask
│   ├── models.py            # Modelos do banco e configuração do SQLite
│   ├── static/              # CSS customizado
│   └── templates/           # Templates HTML com Bootstrap
│
├── requirements.txt         # Lista de dependências
├── README.md                # Este arquivo
└── rpg_panel.db             # Banco de dados gerado após o uso
```

---

## 🎮 Funcionalidades

### Personagens
- Cadastro, edição e exclusão de personagens
- Atributos: PV, CA, Inspiração
- Slots de Magia por nível
- Pedra de Armazenamento de Magia (opcional)
- Habilidades com usos diários

### Sessão de Jogo
- Registro de número, data e nome do andar
- Histórico de sessões anteriores
- Anotações da sessão atual
- Exportação para `.json`
- Botão de **Descanso Longo** (reseta recursos de todos)

### Segurança e Confiabilidade
- Validação de nomes duplicados
- Tratamento de erros de formulário e JSON inválido
- Banco salvo sempre no mesmo diretório da aplicação (`src/rpg_panel.db`)

---

## 🧪 API REST

- `GET /api/data` — Retorna estado atual da sessão e personagens
- `POST /api/data` — Atualiza o estado do servidor com base no JSON enviado

---

## ✨ Créditos

Criado por [Seu Nome Aqui], com foco em tornar sessões de D&D mais organizadas, rápidas e visuais.

---
