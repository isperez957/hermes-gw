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

### Output Guardrails — Formatting & Presentation

- [ ] Formateo automático de tablas markdown → HTML renderizado
  - Detectar tablas en el output del LLM (regex `| ... |`)
  - Parsear a HTML `<table>` con clases CSS
  - Columnas numéricas alineadas a la derecha
  - Columnas de texto alineadas a la izquierda
- [ ] Colores condicionales en tablas financieras
  - Valores positivos → verde
  - Valores negativos → rojo
  - Variaciones > 5% → negrita
  - Rules configurables por tipo de dato (%, €, $, bps)
- [ ] Strip de markdown roto o incompleto
  - Tablas mal formadas (columnas desiguales) → reparar o convertir a lista
  - Código sin cerrar (\`\`\`) → auto-cerrar
  - Links rotos → mostrar URL sin formatear
- [ ] Formateo de números
  - Monedas: 1234567.89 → 1.234.567,89 € (locale ES)
  - Porcentajes: 0.0523 → +5,23%
  - Notación científica → decimal
  - Grandes números: 1500000000 → 1.500M / 1,5B
- [ ] Truncado inteligente de outputs largos
  - Respuestas > 500 líneas → "Mostrar más" colapsable
  - Tablas > 20 filas → paginación (20 por página)
- [ ] Sanitización de output antes del render
  - Escapar HTML malicioso (XSS)
  - Scripts injectados → stripped
  - Emojis/unicode válidos → mantener, secuencias peligrosas → stripped
- [ ] Modo "raw" toggle
  - Botón para ver el markdown original sin procesar
  - Útil para debugging o copiar a otro sistema
- [ ] Resaltado de datos clave
  - Tickers de bolsa → clickable (lleva a Yahoo Finance)
  - Cifras importantes → badge o highlight sutil
  - Fechas → tooltip con formato relativo ("hace 3 días")
- [ ] Post-procesado server-side en el orchestrator
  - El LLM devuelve markdown → el backend lo formatea antes del SSE
  - Cache del formateo: misma respuesta no se reformatea dos veces

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

### Session & Conversation Management

- [ ] Lista de conversaciones en sidebar (ya funciona vía `/api/sessions`)
  - Scroll infinito / paginación
  - Search/filtro por título o fecha
- [ ] Borrar conversaciones (individual + bulk)
  - Soft delete: archivar primero, borrado real tras 30 días
  - Confirmación: "¿Seguro que quieres borrar esta conversación?"
  - Ya existen los endpoints: `DELETE /api/sessions/{id}` + `POST /api/sessions/bulk-delete`
- [ ] Renombrar conversaciones (doble click en el título)
- [ ] Pin/star conversaciones importantes
- [ ] Exportar conversación a Markdown, PDF o JSON
  - Ya existe `GET /api/sessions/{id}/export` → JSONL
- [ ] Compartir conversación (link público de solo lectura, opcional)
- [ ] Estadísticas de uso personal: chats/día, tools usadas, tokens consumidos

### File Upload & Analysis

- [ ] Drag & drop de archivos en el chat
  - Tipos: PDF, Excel (.xlsx), CSV, imágenes (.png/.jpg), Word (.docx)
  - Límite: 10MB por archivo, máx 5 archivos simultáneos
- [ ] Procesamiento server-side
  - PDF: extraer texto con `marker-pdf` o `pymupdf` (skills existentes)
  - Excel/CSV: parsear con pandas, mostrar preview de 10 filas
  - Imágenes: enviar al modelo con visión (si el modelo lo soporta)
- [ ] Análisis del contenido del archivo
  - "Analiza este PDF de resultados trimestrales de Inditex"
  - "Dame un resumen de este Excel de gastos"
  - "¿Qué dice esta factura?"
- [ ] Seguridad
  - Scan de virus (ClamAV en el backend)
  - Archivos NO se guardan permanentemente — se borran tras la sesión
  - Nunca enviar archivos con PII a modelos externos sin anonimizar

### Email Integration

- [ ] Enviar conversación por email
  - "Envíame este análisis a isaac@gmail.com"
  - Formato: Markdown renderizado en el cuerpo, JSON adjunto
- [ ] Resumen diario/semanal por email
  - "Cada lunes a las 9am, envíame un resumen de mercados"
  - Usar cron jobs de Hermes + skill de email (himalaya)
- [ ] Alertas por email
  - "Avísame si el IBEX 35 cae más del 3% en un día"
  - "Avísame cuando Inditex publique resultados"
- [ ] Email → chat (responder desde el email)
  - "Reenvíame este email y respóndelo por mí"

### Write Access & Export

- [ ] Guardar respuestas en Obsidian/Notion
  - "Guarda este análisis en mi vault de Obsidian"
  - "Crea una página en Notion con este portfolio"
- [ ] Exportar datos a Google Sheets
  - "Pon esta tabla de cotizaciones en mi Google Sheet de seguimiento"
- [ ] Generar documentos
  - PowerPoint con análisis financiero (skill ya existente)
  - PDF con informe de cartera (weasyprint/reportlab)
  - Excel con datos de mercado (openpyxl)
- [ ] Acciones con confirmación
  - Toda operación de escritura requiere confirmación explícita del usuario
  - Audit log de qué se escribió, dónde y cuándo

### Generic UX Improvements

- [ ] Dark/light mode (detectar preferencia del sistema)
- [ ] Atajos de teclado
  - `Ctrl+Enter` → enviar mensaje
  - `Ctrl+K` → buscar conversaciones
  - `Ctrl+N` → nueva conversación
  - `Esc` → cancelar respuesta en curso
- [ ] Markdown rendering en las respuestas
  - Tablas, listas, código, links
  - Sintaxis highlighting para bloques de código
- [ ] Thumbs up/down en respuestas (feedback loop)
- [ ] Streaming indicator
  - "Pensando..." / "Buscando datos..." / "Escribiendo..."
  - Progress bar o dots animados mientras se ejecutan tools
- [ ] Tool visibility
  - Mostrar qué tools está usando el agente (collapsible)
  - "Buscando cotización de SAN.MC en Yahoo Finance..."
  - "Consultando base de datos SQLite..."
- [ ] Copiar mensaje al portapapeles (botón en cada respuesta)
- [ ] Regenerar respuesta (mismo prompt, nueva respuesta)
- [ ] Editar mensaje enviado y reenviar
- [ ] Soporte mobile-first / responsive
- [ ] PWA (instalable como app en iOS/Android)
- [ ] Notificaciones push cuando termina una consulta larga

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

---

## 8. Observability & Audit

### Prompt & Response Logging

- [ ] Log estructurado de cada interacción
  - `timestamp`, `user_id`, `session_id`, `model`
  - `prompt_text`, `prompt_tokens`, `output_tokens`
  - `tools_invoked` (lista), `tool_call_count`, `tool_duration_ms`
  - `total_duration_ms`, `status` (success / error / timeout)
  - `error_type`, `error_message` (si falla)
  - `input_has_pii` (booleano, tras pasar Presidio)
- [ ] Almacenamiento
  - Opción A: CloudWatch Logs (estructurado JSON, barato, ya integrado)
  - Opción B: S3 + Athena (consultas SQL, más flexible)
  - Opción C: Elasticsearch/OpenSearch (dashboards ricos, más caro)
- [ ] Retención configurable
  - Logs detallados: 90 días
  - Métricas agregadas: 2 años
  - GDPR: derecho al olvido → borrar logs de un usuario bajo demanda

### Dashboards de observabilidad

- [ ] Dashboard de tráfico
  - Requests/minuto, requests/hora, requests/día
  - Breakdown por usuario, por modelo, por perfil de riesgo
  - Pico de uso (hora del día, día de la semana)
- [ ] Dashboard de latencia
  - p50, p95, p99 por modelo y por tipo de consulta
  - Time-to-first-token (TTFT)
  - Tiempo en tools vs tiempo en generación de texto
  - Correlación: más tools = más latencia
- [ ] Dashboard de errores
  - Tasa de error por modelo, por tipo (timeout, API error, tool crash)
  - Errores 429 (rate limit) del provider
  - Gateway spawn failures
- [ ] Dashboard de costes
  - Tokens consumidos por usuario/día/semana
  - Coste estimado en USD (según pricing del modelo)
  - Proyección mensual vs presupuesto
- [ ] Dashboard de calidad
  - Thumbs up/down ratio por modelo y por tipo de consulta
  - Tasa de abandono (usuario cierra antes de que termine)
  - Prompts repetidos (usuario no quedó satisfecho y pregunta otra vez)

### Auditoría de prompts

- [ ] Panel de administrador para revisar prompts
  - Búsqueda full-text por palabra clave
  - Filtro por usuario, fecha, modelo, status
  - Ver prompt original + respuesta completa
- [ ] Detección de anomalías
  - Prompts que inyectan instrucciones maliciosas (jailbreak, prompt injection)
  - Usuario que de repente triplica su consumo de tokens
  - Patrones de abuso: mismo prompt 50 veces, scraping
- [ ] Alertas de auditoría
  - Prompt con PII no detectado por Presidio → alerta al admin
  - Intento de jailbreak detectado → flag + log
  - Usuario excede su cuota de tokens → notificar
- [ ] Compliance
  - Export de auditoría para certificación (ISO 27001, SOC 2)
  - Registro de quién accedió al panel de auditoría y qué hizo
  - Inmutabilidad: logs no se pueden modificar ni borrar (S3 Object Lock)

### Tracing distribuido

- [ ] Trace ID único por request (end-to-end)
  - CloudFront → ALB → Orchestrator → Gateway → LLM API → tools → respuesta
  - Cada paso registra su duración y status
- [ ] OpenTelemetry instrumentation
  - Auto-instrumentación en FastAPI (orchestrator)
  - Manual spans en GatewayManager (spawn, health check, proxy)
  - Export a AWS X-Ray o Grafana Tempo
- [ ] Waterfall view
  - "Esta consulta tardó 45s: 2s auth, 5s gateway spawn, 30s LLM, 8s tools"

### Alertas

- [ ] Canales de alerta
  - Email (admin@)
  - Slack / Discord / Teams
  - PagerDuty para críticas
- [ ] Reglas de alerta
  - Tasa de error > 5% en ventana de 5 minutos
  - Latencia p95 > 120s en ventana de 15 minutos
  - Gateway pool a 80% de capacidad
  - Disco > 85%
  - Provider API no responde (DeepSeek down)
  - Coste diario > presupuesto × 1.5
- [ ] Silenciamiento
  - Mantenimiento programado → silence window
  - Alerta repetida → agrupar, no spamear
