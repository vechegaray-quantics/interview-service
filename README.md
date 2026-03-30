# Interview Service

Microservicio HTTP (FastAPI) que orquesta entrevistas estructuradas de una campaña. Su responsabilidad principal es:

1. **Iniciar y gestionar la sesión de entrevista**.
2. **Recibir respuestas del entrevistado** y avanzar pregunta a pregunta.
3. **Construir y devolver un reporte final**.
4. **Sincronizar estado** con otros microservicios (`invitation-service` y `campaign-service`).

---

## 1) Contrato público (API que expone este microservicio)

Base path: `/public/v1/interviews`

### 1.1 `POST /public/v1/interviews/start`
Inicia (o recupera, idempotente) una sesión de entrevista a partir de un `inviteToken`.

**Request body**
```json
{
  "inviteToken": "tok_demo_001"
}
```

**Reglas**
- `inviteToken` es requerido y debe tener al menos 4 caracteres.
- Si ya existe una sesión activa para la invitación, devuelve esa misma sesión (idempotencia).

**Response 200**
```json
{
  "sessionId": "sess_ab12cd34ef56",
  "campaignId": "camp_demo_interview",
  "campaignName": "Diagnóstico Comercial Q2",
  "assistantMessage": "¿Cuál es el principal desafío que enfrentas hoy en este proceso?",
  "sessionCompleted": false
}
```

**Errores típicos**
- `404` si el token de invitación no existe.
- `502` si falla `invitation-service` o `campaign-service`.
- `500` si la campaña viene sin preguntas válidas.

---

### 1.2 `GET /public/v1/interviews/{session_id}`
Consulta el estado actual de una sesión.

**Path params**
- `session_id`: ID de sesión (`sess_...`).

**Response 200**
```json
{
  "sessionId": "sess_ab12cd34ef56",
  "campaignId": "camp_demo_interview",
  "campaignName": "Diagnóstico Comercial Q2",
  "assistantMessage": "¿Ese problema está cuantificado?",
  "sessionCompleted": false
}
```

**Errores típicos**
- `404` si la sesión no existe.
- `502` si falla consulta a `campaign-service`.

---

### 1.3 `POST /public/v1/interviews/{session_id}/messages`
Recibe una respuesta del usuario y devuelve el siguiente turno del asistente.

**Request body**
```json
{
  "message": "Tenemos retrasos frecuentes en la operación."
}
```

**Reglas**
- `message` es requerido y debe tener al menos 1 carácter.
- Solo acepta mensajes si la sesión está `in_progress`.
- Cuando responde la última pregunta, deja la sesión lista para finalizar.

**Response 200 (cuando aún faltan preguntas)**
```json
{
  "assistantMessage": "¿Cuál crees que es la principal causa del problema?",
  "sessionCompleted": false
}
```

**Response 200 (cuando ya respondió la última)**
```json
{
  "assistantMessage": "Gracias. La entrevista quedó lista para finalizar.",
  "sessionCompleted": true
}
```

**Errores típicos**
- `404` si la sesión no existe.
- `409` si la sesión ya fue completada.
- `409` si la sesión ya está lista para finalizar (sin más preguntas).
- `502` si falla `campaign-service`.

---

### 1.4 `POST /public/v1/interviews/{session_id}/finalize`
Finaliza la entrevista y devuelve el reporte.

**Request body**
```json
{
  "includeTranscript": true
}
```

- `includeTranscript` es opcional (default `false`).
- Si el reporte ya existe, devuelve el mismo reporte (idempotencia).

**Response 200**
```json
{
  "report": {
    "metadata": {
      "sessionId": "sess_ab12cd34ef56",
      "version": "v1",
      "generatedAt": "2026-03-30T00:00:00+00:00",
      "campaignId": "camp_demo_interview",
      "campaignName": "Diagnóstico Comercial Q2",
      "model": "stub-v2-structured"
    },
    "summary": "Se completó una entrevista para la campaña Diagnóstico Comercial Q2 con 4 respuesta(s) estructuradas.",
    "mainProblem": "Problema principal",
    "observedSymptoms": [
      "Impacta todos los días",
      "Creemos que es falta de coordinación"
    ],
    "knownImpact": [
      "Esperamos reducir tiempos"
    ],
    "openQuestions": [],
    "suggestedNextSteps": [
      "Validar los hallazgos con los stakeholders principales.",
      "Priorizar acciones sobre el problema principal identificado."
    ],
    "transcript": [
      { "role": "assistant", "content": "..." },
      { "role": "user", "content": "..." }
    ]
  }
}
```

**Errores típicos**
- `404` si la sesión no existe.
- `409` si todavía no terminó de responder todas las preguntas.
- `502` si falla sincronización con `invitation-service`.

---

### 1.5 Endpoints de salud

#### `GET /`
#### `GET /health`
Ambos devuelven:

```json
{
  "ok": true,
  "service": "Interview Service",
  "environment": "dev",
  "version": "0.1.0"
}
```

---

## 2) Contratos de entrada desde otros microservicios (lo que este servicio **recibe**)

Este servicio no solo recibe requests del front/BFF; también depende de contratos HTTP internos.

### 2.1 Desde `invitation-service`

#### `GET /internal/v1/invitations/by-token/{inviteToken}`
Header requerido:
- `X-Internal-Service-Token: <internal_service_token>`

**Payload esperado (mínimo):**
```json
{
  "invitationId": "inv_...",
  "campaignId": "camp_...",
  "tenantId": "tenant_..."
}
```

> Campos adicionales son tolerados, pero esos 3 son indispensables para el flujo.

#### `POST /internal/v1/invitations/{invitationId}/complete`
Header requerido:
- `X-Internal-Service-Token: <internal_service_token>`

Sin body. Se usa para marcar la invitación como completada una vez generado el reporte.

---

### 2.2 Desde `campaign-service`

#### `GET /v1/campaigns/{campaignId}`
Header requerido:
- `X-Tenant-Id: <tenantId>`

**Payload esperado (mínimo):**
```json
{
  "campaignId": "camp_demo_interview",
  "campaignName": "Diagnóstico Comercial Q2",
  "questions": [
    {
      "id": "main_problem",
      "text": "¿Cuál es el principal desafío...?",
      "objective": "Entender el problema principal."
    }
  ]
}
```

**Normalización que aplica este servicio**
- Si una pregunta no tiene `id`, genera `q_{index}`.
- Si `objective` viene vacío, usa `text` como objetivo.
- Descarta preguntas cuyo `text` quede vacío.
- Si no queda ninguna pregunta válida, falla con `500`.

---

## 3) Contrato de salida hacia otros microservicios (lo que este servicio **entrega**)

### 3.1 A `invitation-service`
Al finalizar (o refinalizar) una sesión, invoca:

`POST /internal/v1/invitations/{invitationId}/complete`

Objetivo: sincronizar que la invitación quedó completada.

### 3.2 A consumidores de la API pública
Entrega:
- Estado de sesión y próximo mensaje del asistente.
- Resultado de cada turno (`assistantMessage`, `sessionCompleted`).
- Reporte estructurado final con metadatos y conclusiones.

---

## 4) Modelo del reporte final (contrato estable sugerido)

Objeto `report`:

- `metadata.sessionId: string`
- `metadata.version: string` (actual: `v1`)
- `metadata.generatedAt: string` (ISO-8601 UTC)
- `metadata.campaignId: string`
- `metadata.campaignName: string`
- `metadata.model: string`
- `summary: string`
- `mainProblem: string`
- `observedSymptoms: string[]`
- `knownImpact: string[]`
- `openQuestions: string[]`
- `suggestedNextSteps: string[]`
- `transcript: Array<{ role: string, content: string }>` (vacío si `includeTranscript=false`)

---

## 5) Variables de entorno relevantes

- `APP_ENV`
- `DATABASE_URL`
- `INTERNAL_SERVICE_TOKEN`
- `CAMPAIGN_SERVICE_BASE_URL`
- `INVITATION_SERVICE_BASE_URL`
- `CORS_ALLOWED_ORIGINS`
- `OPENAI_MODEL` *(de momento no impacta el flujo actual del reporte stub)*

---

## 6) Resumen operativo rápido

1. Cliente llama `/start` con `inviteToken`.
2. Servicio valida token en `invitation-service` y trae preguntas desde `campaign-service`.
3. Cliente envía respuestas por `/messages`.
4. Al completar preguntas, cliente llama `/finalize`.
5. Servicio genera `report`, persiste, responde el reporte y marca invitación completada en `invitation-service`.

