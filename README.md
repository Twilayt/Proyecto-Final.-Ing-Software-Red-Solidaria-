# RedSolidaria

RedSolidaria es un prototipo académico de API web para registrar personas donantes y administrar su disponibilidad de alimentos o recursos. Esta segunda entrega implementa el módulo de identidad y donantes definido durante la planificación inicial.

## Resultado implementado

- Registro de cuentas de usuario.
- Autenticación con JWT y expiración configurable.
- Contraseñas protegidas con Argon2.
- Roles `admin` y `user`.
- Registro y consulta de perfiles de donantes.
- Aprobación o rechazo de perfiles por administradores.
- Persistencia mediante SQLAlchemy: SQLite local o PostgreSQL por `DATABASE_URL`.
- Validación de datos, CORS restringido y encabezados HTTP defensivos.
- 16 pruebas automatizadas con 93.07 % de cobertura.
- CI/CD con GitHub Actions y despliegue de pruebas mediante un Deploy Hook de Render.
- Escaneo automatizado con OWASP ZAP.
- Integración con SonarQube y puerta de calidad.

## Inicio rápido

Requiere Python 3.12.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --env-file .env
```

Después abre:

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- Salud: <http://127.0.0.1:8000/health>

Para ejecutar las pruebas:

```powershell
python -m pytest
```

La ejecución falla automáticamente si la cobertura baja del 80 %.

## Rutas principales

| Método | Ruta | Acceso | Propósito |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Público | Registrar una cuenta de usuario |
| `POST` | `/api/v1/auth/token` | Público | Obtener el JWT |
| `GET` | `/api/v1/auth/me` | Autenticado | Consultar la identidad actual |
| `POST` | `/api/v1/donors` | Autenticado | Registrar un perfil de donante |
| `GET` | `/api/v1/donors/me` | Autenticado | Listar perfiles propios |
| `GET` | `/api/v1/donors` | Administrador | Listar y filtrar todos los perfiles |
| `PATCH` | `/api/v1/donors/{id}/status` | Administrador | Aprobar o rechazar un perfil |
| `DELETE` | `/api/v1/donors/{id}` | Propietario o administrador | Eliminar un perfil |

## Evidencias

Los resultados reproducibles se guardan en `reports/evidencias/`:

- `pruebas-unitarias/`: JUnit, cobertura XML y resumen verificado.
- `owasp-zap/`: ubicación para los reportes HTML, JSON y Markdown de ZAP.
- `sonarqube/`: formato para registrar las métricas del panel.

La guía completa de instalación, GitHub, Render, ZAP, SonarQube y entrega se encuentra en [GUIA_EJECUCION.md](GUIA_EJECUCION.md).

## Estructura

```text
app/                    Código de la API
tests/                  Pruebas unitarias e integración
.github/workflows/      CI/CD, ZAP y SonarQube
scripts/                Ayudas para Windows y puertas de calidad
reports/evidencias/     Resultados y formatos de evidencia
docs/                   Informes académicos
```

## Fuentes técnicas

- [FastAPI JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Pytest](https://docs.pytest.org/en/stable/getting-started.html)
- [GitHub Actions](https://docs.github.com/en/actions)
- [OWASP ZAP Docker](https://www.zaproxy.org/docs/docker/)
- [Cobertura Python en SonarQube](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/python-test-coverage)
- [Despliegue FastAPI en Render](https://render.com/docs/deploy-fastapi)

