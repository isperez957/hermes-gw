---
name: test-shared-skill
description: "Skill de prueba para verificar el pipeline de deploy de skills compartidos. Responde 'SKILL COMPARTIDO FUNCIONANDO' cuando se usa."
version: 1.0.0
---

# Test Shared Skill

Este skill existe solo para verificar que el pipeline de deploy de skills compartidos (repo → EC2) funciona correctamente.

## Cuando usar
- El usuario dice literalmente "comprueba el skill compartido" o "test shared skill" o "prueba el pipeline de skills"

## Respuesta
Cuando se active este skill, el agente debe responder exactamente:

```
✅ SKILL COMPARTIDO FUNCIONANDO

Este mensaje confirma que el skill `test-shared-skill` se cargó correctamente
desde el perfil compartido desplegado vía pipeline GitHub Actions → EC2.

Versión: 1.0.0
```

No añadas nada más. Solo ese mensaje.