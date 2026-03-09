# Projeto Diario Escolar (FastAPI + Vue 3)

Este projeto foi reorganizado em 2 partes:

- `backend`: API em FastAPI com persistencia em SQLite
- `frontend`: interface web em Vue 3

## Estrutura

- `backend/app/main.py`: endpoints da API
- `backend/app/models.py`: tabelas do banco
- `backend/app/schemas.py`: formatos de entrada e saida
- `backend/app/database.py`: conexao com SQLite
- `frontend/src/App.vue`: tela principal

## Como rodar

### 1) Backend

```powershell
cd C:\Users\tiago\OneDrive\Documentos\projeto\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponivel em: http://127.0.0.1:8000
Documentacao interativa: http://127.0.0.1:8000/docs

### 2) Frontend

Em outro terminal:

```powershell
cd C:\Users\tiago\OneDrive\Documentos\projeto\frontend
npm install
npm run dev
```

App web em: http://127.0.0.1:5173

## Persistencia

Os dados ficam salvos no arquivo `backend/escola.db`.
Se voce fechar o app e abrir de novo, os dados continuam la.
