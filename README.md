# Sistema de Gerenciamento de Ligas de Futebol ⚽

Sistema completo para gerenciar ligas amadoras de futebol, incluindo controle de jogadores, jogos, finanças e relatórios.

## 🏗️ Arquitetura

### Backend (Python + FastAPI)
- **Clean Architecture** com separação de camadas
- **Repository Pattern** para acesso aos dados
- **Dependency Injection** nativa do FastAPI
- **SQLAlchemy ORM** para banco de dados

### Frontend (TypeScript + React)
- **Feature-based Architecture** (organização por funcionalidades)
- **Custom Hooks** para lógica reutilizável
- **Service Layer** para chamadas API
- **Tailwind CSS** para estilização

## 📁 Estrutura do Projeto

```
project/
├── backend/
│   ├── app/
│   │   ├── core/              # Configurações e database
│   │   ├── domain/            # Entidades e schemas
│   │   ├── infrastructure/    # Models e repositories
│   │   ├── application/       # Services (lógica de negócio)
│   │   └── presentation/      # API routes
│   ├── tests/
│   ├── .env
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── features/          # Funcionalidades (players, games, etc)
    │   ├── shared/            # Componentes e utils compartilhados
    │   ├── App.tsx
    │   └── main.tsx
    ├── .env
    └── package.json
```

## 🚀 Instalação e Execução

### Backend

```bash
# 1. Criar ambiente virtual
cd backend
python -m venv venv

# 2. Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 5. Aplicar as migrações do banco (cria/atualiza o schema)
alembic upgrade head

# 6. Executar servidor
python app/main.py
# ou
uvicorn app.main:app --reload

# Backend rodará em: http://localhost:8000
# Documentação: http://localhost:8000/docs
```

### Frontend

```bash
# 1. Instalar dependências
cd frontend
npm install

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env se necessário

# 3. Executar em desenvolvimento
npm run dev

# Frontend rodará em: http://localhost:5173
```

## 📦 Dependências Principais

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados
- **Alembic**: Migrações de banco de dados
- **python-jose**: JWT para autenticação

### Frontend
- **React 18**: Biblioteca UI
- **TypeScript**: Tipagem estática
- **React Router**: Navegação
- **Axios**: Cliente HTTP
- **Zustand**: Gerenciamento de estado
- **React Hook Form**: Formulários
- **Tailwind CSS**: Estilização
- **Lucide React**: Ícones

## 🎯 Próximos Passos

### 1. Finalizar módulo de Jogadores
- [ ] Implementar modal de criação de jogador
- [ ] Implementar modal de edição de jogador
- [ ] Adicionar validação de formulários com Zod
- [ ] Implementar paginação na listagem

### 2. Implementar módulo de Jogos
- [ ] Criar models e schemas (Game, GamePlayer)
- [ ] Criar repository e service
- [ ] Criar endpoints da API
- [ ] Criar componentes e páginas no frontend
- [ ] Implementar registro de scouts durante o jogo

### 3. Implementar módulo de Finanças
- [ ] Criar models e schemas (Finance, MonthlyExpense)
- [ ] Criar repository e service
- [ ] Criar endpoints da API
- [ ] Criar componentes e páginas no frontend
- [ ] Implementar controle de mensalidades

### 4. Implementar módulo de Relatórios
- [ ] Criar service de geração de relatórios
- [ ] Implementar relatórios mensais financeiros
- [ ] Implementar relatórios de estatísticas
- [ ] Criar componentes de visualização
- [ ] Adicionar gráficos (Chart.js ou Recharts)

### 5. Melhorias gerais
- [ ] Implementar autenticação JWT
- [ ] Adicionar testes unitários e integração
- [ ] Implementar paginação e filtros
- [ ] Adicionar validações mais robustas
- [ ] Melhorar tratamento de erros
- [ ] Adicionar loading states
- [ ] Implementar tema dark mode
- [ ] Otimizar queries do banco
- [ ] Adicionar cache (Redis)
- [ ] Dockerizar a aplicação

## 📚 Recursos Úteis

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Frontend
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Router Documentation](https://reactrouter.com/)

## 🤝 Contribuindo

1. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
2. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
3. Push para a branch (`git push origin feature/AmazingFeature`)
4. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
