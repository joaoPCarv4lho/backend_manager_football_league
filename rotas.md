**Rotas de Auth**

- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- PATCH /api/v1/auth/me/plan

> As rotas de Players, Games e Finances exigem token JWT (header `Authorization: Bearer <token>`).


**Rotas de Reports (plano Pro)**

- GET /api/v1/reports/scouts
- GET /api/v1/reports/awards
- GET /api/v1/reports/financial/{year}

> Exclusivas do plano Pro: retornam 403 para usuários do plano Básico.


**Rotas de Player**

- POST /api/v1/players/
- GET /api/v1/players/
- GET /api/v1/players/player_id
- PATCH /api/v1/players/player_id
- PATCH /api/v1/players/player_id/scout
- DELETE /api/v1/players/player_id
- GET /api/v1/players/player_id/stats
- GET /api/v1/players/rankings/top-scorers
- GET /api/v1/players/rankings/top-assists


**Rotas de Games**

- POST /api/v1/games/
- GET /api/v1/games/
- GET /api/v1/games/game_id
- PATCH /api/v1/games/game_id
- PATCH /api/v1/games/game_id/score
- DELETE /api/v1/games/game_id
- POST /api/v1/games/game_id/players
- GET /api/v1/games/game_id/stats