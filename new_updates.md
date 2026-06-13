FinSight-RAG/
├── core/                          ← CONFIG & SCHEMAS
│   ├── config.py                 (+ add AUTH_SECRET, TOKEN_EXPIRE settings)
│   ├── schemas.py                (+ add User, Role, Permission schemas)
│   └── security.py               ✨ NEW - JWT token generation/verification
│
├── db/                            ← DATABASE LAYER
│   ├── models.py                 (+ add User, Role, Permission, AuditLog models)
│   ├── crud.py                   (+ add user/role/permission CRUD functions)
│   └── database.py               (no changes needed)
│
├── routes/                        ← API ENDPOINTS
│   ├── __init__.py
│   ├── auth.py                   ✨ NEW - /login, /register, /refresh-token
│   ├── companies.py              (+ add @require_permission decorators)
│   ├── transcripts.py            (+ add @require_permission decorators)
│   ├── chunks.py                 (+ add @require_permission decorators)
│   └── users.py                  ✨ NEW - /users, /users/{id}, /roles
│
├── services/                      ← BUSINESS LOGIC
│   ├── auth_service.py           ✨ NEW - hash_password, verify_password, create_token
│   ├── user_service.py           ✨ NEW - user registration, profile management
│   └── permission_service.py     ✨ NEW - check_access, get_user_permissions
│
├── middleware/                    ← MIDDLEWARE
│   ├── __init__.py
│   ├── auth.py                   ✨ NEW - JWT verification middleware
│   ├── audit.py                  ✨ NEW - audit logging middleware
│   └── rate_limit.py             ✨ NEW - rate limiting middleware
│
└── main.py                        (+ add middleware, include route routers)