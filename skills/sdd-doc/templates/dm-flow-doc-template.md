<!-- markdownlint-disable MD033 MD041 MD042 -->

# [Nombre del DM / Título del Flujo]

> Documentación técnica para desarrolladores. Foco: cadena de servicios, Data Manager, y lógica backend. Mantener conciso, profesional, y basado en evidencia de código. Minimizar detalles de UI visual.

[1-2 párrafos de introducción: alcance del flujo, qué DM lo procesa, qué datos maneja.]

---

## 1. Resumen ejecutivo

| Item                    | Detalle                                    |
|-------------------------|--------------------------------------------|
| DM principal            | [El DM que ejecuta la operación real]      |
| Topología               | [Package-backed / App-local / App-only]    |
| Método principal        | [dm.method(params, body)]                  |
| Lógica principal        | [Qué datos se transforman o procesan]      |
| Estado                  | Verificado / Parcial                       |
| Última actualización    | [YYYY-MM-DD]                               |

---

## 2. Origen de la vista

| Campo                  | Evidencia                                   |
|------------------------|---------------------------------------------|
| Pantalla de entrada    | [nombre visible]                            |
| Ruta interna           | [/route-name]                               |
| Host page              | [app/pages/page/page.js L###]               |
| Evento disparador      | [on-action-button → handler(detail)]        |
| Navegación             | [navigate → /destination-route]             |

---

## 3. Clasificación de componentes

En Cells, los componentes pueden venir de `node_modules`, del código local, o de la plataforma directa. Clasificar cada pieza:

| Tag                    | Rol              | Origen              | Paquete / Ruta                         |
|------------------------|------------------|----------------------|----------------------------------------|
| [cells-co-*-ui]        | UI Component     | [node_modules]       | [@cvid-lit-component/...]              |
| [cells-co-*-dm-lit]    | DM               | [node_modules]       | [@cvid-lit-component/...]              |
| [host-page]            | Orquestador      | app-local            | [app/pages/.../page.js]                |

> **Topología**: [Package-backed / App-local DM / App-only] — [justificación breve].

---

## 4. Perfil técnico del DM

| Aspecto                | Evidencia                                   |
|------------------------|---------------------------------------------|
| Custom element         | [tag-name]                                  |
| Archivo fuente         | [path]                                      |
| Versión                | [x.y.z]                                     |
| Properties clave       | [propA, propB]                              |
| Métodos públicos       | [method1(), method2()]                      |
| Eventos emitidos       | [on-response-*, on-post-*]                  |
| Dependencias           | [BGDM / BGADP / Provider]                  |

### Métodos y datos

| Método / Propiedad     | Propósito                    | Modifica estado |
|------------------------|------------------------------|-----------------|
| [method]               | [descripción]                | sí / no         |

```mermaid
classDiagram
  class [DmName] {
    +[method](payload) void
    -validatePayload(input) Object
  }
  class [Provider] {
    +[apiMethod](params, body) Promise
  }
  [DmName] --> [Provider] : invoca
```

---

## 5. Cadena de llamadas a servicios

### Orden y mapeo de parámetros

| #  | Servicio / Endpoint        | Método | Request params clave                  | Response usada downstream              |
|----|---------------------------|--------|---------------------------------------|-----------------------------------------|
| 1  | [/api/endpoint]           | [POST] | [param1, param2]                      | [responseField1, responseField2]        |
| 2  | [/api/endpoint/{id}]      | [GET]  | [responseField1 ← del paso 1]        | [field3, field4]                        |

### Flujo de parámetros entre servicios

```mermaid
sequenceDiagram
    participant HostPage as Host Page
    participant DM
    participant SvcA as Servicio A
    participant SvcB as Servicio B

    HostPage->>DM: Asigna props + invoca método
    DM->>SvcA: POST {params}
    SvcA-->>DM: {responseFields}
    Note over DM: Mapea response → siguiente request
    DM->>SvcB: GET /{responseField}
    SvcB-->>DM: {resultado}
    DM-->>HostPage: Emite evento de resultado
```

---

## 6. Payload

### Request (entrada)

| Campo    | Tipo         | Origen                    | Requerido |
|----------|--------------|---------------------------|-----------|
| [campo]  | [tipo]       | [canal / formulario / DM] | sí / no   |

### Response (salida)

| Campo    | Tipo         | Destino                   |
|----------|--------------|---------------------------|
| [campo]  | [tipo]       | [canal / navegación / UI] |

---

## 7. Canales

### Consumidos (entrada)

| Canal                  | Datos leídos              | Uso en el DM                          |
|------------------------|---------------------------|---------------------------------------|
| [canal]                | [{ field1, field2 }]      | [asignado a prop X]                   |

### Publicados (salida)

| Canal                  | Payload                   | Cuándo se publica                     |
|------------------------|---------------------------|---------------------------------------|
| [canal]                | [{ field1, field2 }]      | [tras éxito / al navegar]             |

---

## 8. Navegación downstream

```
/ruta-actual (host-page)
│
├── [Acción A] → /ruta-destino-a
│                  └── happy path → /ruta-final
│                  └── error → /ruta-error
│
└── [Error técnico] → /ruta-error
```

---

## 9. Reutilización del DM

| Página / Flujo  | Método / indicador usado         | Diferencia clave                       |
|-----------------|----------------------------------|----------------------------------------|
| [page]          | [method / indicator]             | [qué cambia respecto al flujo actual]  |

---

## 10. Errores técnicos

| Código | Handler              | Comportamiento                                |
|--------|----------------------|-----------------------------------------------|
| [code] | [handlerName()]      | [retry → logDown / modal → redirect]          |

---

## 11. Hallazgos críticos

| ID   | Severidad  | Descripción                              | Archivo L###             |
|------|------------|------------------------------------------|--------------------------|
| CF-1 | 🔴 Alta    | [hallazgo]                               | [file.js L###]           |
| CF-2 | 🟡 Media   | [hallazgo]                               | [file.js L###]           |

---

## 12. Conclusión

[1-2 párrafos: qué DM ejecuta la operación, qué fue verificado, qué queda pendiente.]

---

## 13. Gaps o preguntas abiertas

- [rama que no quedó clara]
- [mapeo de API sin evidencia]

<!-- markdownlint-enable MD033 MD041 MD042 -->
