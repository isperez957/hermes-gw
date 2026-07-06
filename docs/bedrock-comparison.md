# Hermes Gateway vs AWS Bedrock — Mapeo y Comparativa

## 1. Mapeo de Componentes

| Hermes Gateway (actual) | AWS Bedrock (equivalente) | Notas |
|---|---|---|
| **Hermes Agent** (CLI, subprocess) | **Bedrock Agent** (managed service) | Bedrock gestiona el ciclo de vida automáticamente |
| **LLM: DeepSeek v4** | **Claude 3.5 Sonnet / Haiku** | Solo modelos del catálogo Bedrock; no puedes usar DeepSeek, OpenAI, etc. |
| **Skills** (`SKILL.md` en filesystem) | **Knowledge Bases** (S3 + embeddings + OpenSearch) | Bedrock indexa docs en S3 automáticamente; menos dinámico que editar un .md |
| **MCP servers** (Python, stdio) | **Action Groups** (Lambda functions + API Schema) | Lambdas con OpenAPI spec; sin estado persistente |
| **gateway_manager.py** (spawn/kill/reap) | **Bedrock Agent lifecycle** (automático) | No hay que gestionar procesos; Bedrock escala solo |
| **config.yaml** (model, reasoning) | **Agent configuration** (Bedrock console / CFN) | Misma idea: modelo, temperatura, instrucciones |
| **Sesiones** (`state.db` SQLite) | **DynamoDB** (session memory) | Bedrock Agents tienen memoria de sesión built-in (30 días) |
| **SSE streaming** (FastAPI → CloudFront) | **Bedrock streaming** (invoke_agent con streaming) | Ambos soportan streaming; Bedrock vía API Gateway WebSocket |
| **JWT auth** (users: isaac/miguel/pablo) | **Cognito / API Gateway authorizer** | Cognito es más complejo pero más seguro; JWT manual es más simple |
| **FastAPI orchestrator** (Docker) | **API Gateway + Lambda** (serverless) | Sin contenedores que mantener, sin disco que llenar |
| **EC2 (t3.medium, 50GB)** | **Sin servidores** (todo gestionado) | Pagas por uso, no por máquina |
| **CloudFront + S3** (frontend) | **Igual o Amplify** | La parte frontend no cambia; Amplify simplifica el deploy |
| **Shared skills vía GitHub CI** | **S3 sync vía CI** | Mismo pipeline, cambia destino: EC2 → S3 (Knowledge Base) |
| **Docker image prune** (problema disco) | **No aplica** | Sin discos que limpiar |

---

## 2. Diagrama Comparativo

```
═══ HERMES GATEWAY ═══                  ═══ AWS BEDROCK ═══

EC2 (Docker)                            ─ (sin servidor)
├── FastAPI orchestrator                │
├── gateway_manager.py                  │
├── Hermes Agent (subprocess)           ├── Bedrock Agent (managed)
│   ├── SKILL.md (filesystem)           │   ├── Knowledge Base (S3 + OpenSearch)
│   ├── MCP (stdio subprocess)          │   ├── Action Groups (Lambda)
│   └── state.db (SQLite)               │   └── Session memory (DynamoDB)
└── /opt/hermes-gw/ (scripts, DB)       │
                                        ├── API Gateway (REST/WS)
Claude/DeepSeek/OpenAI/etc.             └── Claude (solo modelos Bedrock)
(cualquier proveedor)
```

---

## 3. Ventajas y Desventajas

### Hermes Gateway (actual)

| ✅ Ventajas | ❌ Desventajas |
|---|---|
| **Cualquier modelo**: DeepSeek, OpenAI, Anthropic, local... | EC2 que mantener: parches, disco, Docker, reinicios |
| **Skills ultra-dinámicos**: editas un .md y el agente lo carga al instante | El disco se llena (39GB de imágenes Docker) |
| **MCP flexible**: cualquier binario Python/Node en el container | Los gateways se mueren solos (idle timeout, memory) |
| **Coste predecible**: ~$30/mes la EC2 t3.medium | DNS a veces falla en el container |
| **Control total**: puedes parchear Hermes Agent, tocar el modelo | CloudFront limita SSE a 60s (necesitas keepalives) |
| **Multi-tenant simple**: perfiles en filesystem | Single point of failure (una EC2) |
| **Sin vendor lock-in** | Tú gestionas auth, sesiones, escalado |

### AWS Bedrock

| ✅ Ventajas | ❌ Desventajas |
|---|---|
| **Cero mantenimiento**: sin EC2, sin Docker, sin disco | **Solo Claude** (y algunos Titan, Llama... nada de DeepSeek ni OpenAI) |
| **Escalado automático**: Bedrock Agents escala solo | **Más caro a escala**: ~$0.003/1K tokens input + ~$0.015/1K output (Claude Sonnet) |
| **RAG nativo**: Knowledge Bases con embeddings automáticos | Skills menos dinámicos: hay que re-indexar el KB al cambiar docs |
| **Seguridad AWS nativa**: IAM, VPC, CloudTrail, KMS | Action Groups = Lambdas (15 min timeout, cold start) |
| **Streaming nativo**: sin problemas de HTTP/2 ni keepalives | Curva de aprendizaje: CloudFormation, IAM, API Gateway |
| **Memoria de sesión built-in**: 30 días por sesión | Vendor lock-in total |
| **Cumplimiento normativo**: SOC2, HIPAA, etc. | No puedes instalar `yfinance`, `pandas` ni librerías arbitrarias en el agente |

---

## 4. ¿Cuándo usar cada uno?

| Escenario | Recomendación |
|---|---|
| Prototipo rápido, máximo control | **Hermes Gateway** (ya lo tienes) |
| Skills que cambian constantemente | **Hermes Gateway** (editar .md es instantáneo) |
| Necesitas DeepSeek, OpenAI o modelos específicos | **Hermes Gateway** (Bedrock solo tiene su catálogo) |
| Herramientas Python complejas (yfinance, pandas, SQL) | **Hermes Gateway** (MCP con cualquier binario) |
| Producción con requisitos de compliance | **Bedrock** (SOC2, HIPAA, IAM) |
| Escala impredecible o variable | **Bedrock** (auto-scaling) |
| Equipo pequeño sin DevOps | **Bedrock** (cero mantenimiento) |
| Quieres precios predecibles (<$100/mes) | **Hermes Gateway** (~$30/mes fijo) |
| Multi-tenant con aislamiento fuerte | **Bedrock** (agent per tenant con IAM isolation) |

---

## 5. Costes Estimados (uso moderado: ~500 consultas/día)

| Concepto | Hermes Gateway | AWS Bedrock |
|---|---|---|
| Infraestructura | $30/mes (EC2 t3.medium) | $0 (serverless) |
| LLM tokens | ~$200/mes (DeepSeek API) | ~$400/mes (Claude Sonnet) |
| Almacenamiento | Incluido en EC2 | ~$5/mes (S3 + DynamoDB) |
| **Total mensual** | **~$230/mes** | **~$405/mes** |

Bedrock es ~75% más caro en tokens, pero ahorras el DevOps.
