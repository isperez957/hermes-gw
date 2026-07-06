# Hermes Gateway — TODOs

## 1. User Auth

- [ ] Migrar de JWT hardcoded (`dev-secret-change-me`) a OAuth2/OIDC
  - Evaluar: Auth0, Clerk, AWS Cognito, Supabase Auth
  - Criterio: que soporte social login (Google, GitHub) + magic link
- [ ] Tabla de usuarios en BD (RDS o DynamoDB)
  - `id`, `email`, `name`, `profile`, `role`, `created_at`, `last_login`
- [ ] Roles: `admin` (gestión), `user` (chat solamente)
- [ ] Passwordless login (magic link por email)
- [ ] Session management server-side (refresh tokens, revocación)
- [ ] Rate limiting por usuario (no solo por IP)
- [ ] Audit log: quién hizo qué y cuándo

---

## 2. Scale Number of Users

- [ ] Migrar GatewayManager de procesos locales a Pods/containers independientes
  - Evaluar: ECS Fargate vs EKS vs quedarse en EC2 con Docker
  - Cada gateway = 1 contenedor con resource limits (CPU/mem)
- [ ] Connection pooling para gateways idle
  - Gateway pool pre-calentado (N gateways listos, asignar bajo demanda)
  - Lazy spawn con warm-up para el resto
- [ ] Auto-scaling
  - EC2: CloudWatch alarm → auto-scaling group (CPU > 70%)
  - ECS: Service auto-scaling por número de requests
  - EKS: HPA + Karpenter
- [ ] Load testing
  - Artillery o k6: 50, 100, 500 usuarios concurrentes
  - Medir: latencia p50/p95/p99, throughput, errores
- [ ] Multi-region (si aplica)
  - Usuarios EU → eu-west-1, usuarios LATAM → us-east-1
  - Latencia <100ms para el primer token

---

## 3. Input Filters — GDPR + Prompt Complexity

### GDPR / PII Detection

- [ ] Integrar Microsoft Presidio
  - Detección de PII: nombres, emails, teléfonos, DNI/NIF, IBAN, direcciones
  - Anonimizar antes de enviar al LLM (DeepSeek no tiene servidores en EU)
  - Re-identificar en la respuesta (si es necesario)
- [ ] Política de retención de datos
  - Los datos personales nunca salen de AWS eu-west-1
  - Logs sin PII (redactados)
  - Borrado de sesiones bajo demanda del usuario
- [ ] Consentimiento explícito
  - Banner en el frontend: "Tus datos se procesan en AWS Irlanda"
  - Opción de no enviar datos al modelo externo (usar Bedrock en su lugar)
- [ ] Data Processing Agreement (DPA) para clientes enterprise

### Prompt Complexity / Time Estimation

- [ ] Analizador de complejidad del prompt antes de enviar
  - Número de tools que se van a invocar (estimar por keywords)
  - Longitud del prompt + contexto → estimar tokens
  - Tiempo estimado de respuesta: corto (<10s), medio (10-60s), largo (>60s)
- [ ] Mostrar estimación en el frontend: "Esta consulta puede tardar ~45s"
- [ ] Timeout por tipo de consulta
  - Simple (sin tools): 30s
  - Medio (1-3 tools): 90s
  - Complejo (multi-step): 180s
- [ ] Rate limiting por complejidad
  - Máximo N consultas complejas por minuto/usuario
  - Cola de prioridad: consultas simples primero

---

## 4. Language & UI Improvements

### Multi-language

- [ ] i18n en el frontend (ES, EN inicialmente)
  - React-i18next o similar
  - Detectar idioma del navegador
- [ ] El modelo responde en el idioma del prompt (ya lo hace)
  - Forzar idioma de respuesta vía system prompt: `Respond always in {user_lang}`

### Model Selection in UI

- [ ] Dropdown en el frontend para elegir modelo
  - Opciones: DeepSeek V4 Flash, DeepSeek V4 Pro, GPT-4o Mini, Claude Haiku
  - El backend resuelve qué provider usar
- [ ] Indicador de coste estimado por modelo: "~$0.02 esta consulta con Flash"
- [ ] Guardar preferencia de modelo por usuario

### User Info in UI

- [ ] Avatar + nombre en la esquina superior derecha
- [ ] Indicador de sesiones activas: "3 gateways activos"
- [ ] Última conexión
- [ ] Créditos/uso restante (si se implementa billing)

---

## 5. Endurance / Resiliencia

- [ ] Health checks mejorados
  - Gateway: no solo `/health`, también `/health/detailed` (tools cargadas, modelo online)
  - Orchestrator: health de todos los gateways agregado
- [ ] Circuit breaker por gateway
  - Si un gateway falla 3 veces en 5 minutos → marcarlo como degraded
  - Auto-recuperación tras 2 minutos
- [ ] Graceful degradation
  - Si DeepSeek está caído → fallback a GPT-4o Mini
  - Si todas las APIs caen → mensaje amigable: "Servicio temporalmente no disponible"
- [ ] Retry con exponential backoff
  - Timeouts de red → 3 reintentos (1s, 2s, 4s)
  - Errores 5xx del provider → reintentar una vez
- [ ] Rate limit handling
  - Detectar 429 del provider → backoff + notificar al usuario
- [ ] Monitoreo
  - CloudWatch metrics: latencia, errores, gateways activos
  - Dashboard en CloudWatch o Grafana
  - Alertas: >5% errores, gateway pool agotado, disco >80%
- [ ] Backup automático
  - state.db de cada perfil → S3 cada 6 horas
  - EBS snapshot diario
- [ ] Disaster recovery
  - Runbook documentado: qué hacer si EC2 muere, si EBS se corrompe
  - Tiempo objetivo de recuperación (RTO): <30 min

---

## 6. More Skills

- [ ] Skills de productividad
  - Google Workspace (Gmail, Calendar, Drive) — ya existe parcialmente
  - Notion — ya existe
  - Slack / Teams
- [ ] Skills de desarrollo
  - GitHub advanced: code review, PR management, CI/CD triggers
  - Jira / Linear integration
- [ ] Skills de datos
  - SQL client (consultas a RDS/Redshift)
  - Generación de gráficos (matplotlib/vega-lite) → PNG/SVG
- [ ] Skills de documento
  - PDF generation (reportlab/weasyprint)
  - Excel generation (openpyxl)
- [ ] Skills financieros (expandir los existentes para incluir más mercados y fuentes de datos)
  - SEC EDGAR filings
  - CNMV filings (España)
  - Yahoo Finance → Bloomberg/Reuters si hay presupuesto
- [ ] Marketplace de skills
  - Los usuarios pueden activar/desactivar skills desde el UI
  - Skills comunitarias (contribuciones externas)

---

## 7. Testing Set of Prompts

- [ ] Test suite automatizado con prompts representativos

### Categorías de tests

| Categoría | Prompt ejemplo | Expected |
|-----------|---------------|----------|
| **Saludo simple** | "Hola" | Respuesta en <3s, sin tools |
| **Pregunta factual** | "¿Cuál es el PIB de España en 2025?" | 1-2 tools, respuesta en <15s |
| **Análisis financiero** | "Analiza Telefónica vs Vodafone" | 3-5 tools, respuesta en <45s |
| **Multi-step complejo** | "Crea un portfolio diversificado para un perfil moderado con 50K€" | 5-10 tools, respuesta en <90s |
| **Error handling** | Prompt vacío o con caracteres especiales | Error manejado, sin crash |
| **Idioma** | "Quelle est la capital de France?" | Respuesta en francés |
| **PII detection** | "Mi email es isaac@gmail.com y mi DNI es 12345678X" | PII anonimizado antes de enviar al LLM |
| **Timeout** | Prompt que fuerza 15+ tool calls | Timeout tras 3 min, respuesta parcial |
| **Concurrencia** | 10 usuarios simultáneos con prompts financieros | Sin errores, <2s de degradación |

- [ ] CI/CD pipeline de tests
  - GitHub Actions nightly: correr 20 prompts y validar
  - Métricas: latencia, tasa de éxito, tools invocadas
- [ ] Regression testing
  - Antes de cada deploy, correr 5 prompts críticos
  - Bloquear deploy si la tasa de éxito < 90%
- [ ] Dataset de prompts reales
  - Registrar prompts de usuarios (anonimizados) para mejorar el test set
  - Feedback loop: "¿Fue útil esta respuesta?" → entrenar el test set
