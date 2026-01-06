# API con Litestar y PostgreSQL

API REST para gestión de biblioteca que permite administrar usuarios, libros y préstamos. Incluye autenticación JWT y documentación interactiva (Swagger/Scalar).

## Requisitos

- [uv](https://github.com/astral-sh/uv)
- PostgreSQL

## Inicio rápido

```bash
uv sync                      # Instala las dependencias
cp .env.example .env         # Configura las variables de entorno (ajusta según sea necesario)
uv run alembic upgrade head  # Aplica las migraciones de la base de datos
uv run litestar --reload     # Inicia el servidor de desarrollo
# Accede a http://localhost:8000/schema para ver la documentación de la API
```

## Nota Windows / WSL (importante)

Si estás en Windows y el proyecto vive en una ruta tipo `C:\...` (o en WSL bajo `/mnt/c/...`), evita mezclar la creación/uso del `.venv` entre Windows y WSL.

- Si tu `.venv` fue creado en Windows (carpeta `.venv/Scripts/...`), ejecuta los comandos de `uv` (migraciones/servidor) desde PowerShell.
- Si quieres trabajar 100% en WSL, crea el `.venv` desde WSL (y no uses el `.venv` de Windows).

## Variables de entorno

Crea un archivo `.env` basado en `.env.example`:

- `DEBUG`: Modo debug (True/False)
- `JWT_SECRET_KEY`: Clave secreta para tokens JWT
- `DATABASE_URL`: URL de conexión a PostgreSQL (formato: `postgresql+psycopg://usuario:contraseña@host:puerto/nombre_bd`). Recuerda crear la base de datos antes de ejecutar la aplicación con `createdb nombre_bd`.

## Cargar datos iniciales (Req. 8)

El proyecto incluye un respaldo con datos de ejemplo en [initial_data.sql](initial_data.sql). Para cargarlo (después de aplicar migraciones):

```bash
psql -d <nombre_bd> -f initial_data.sql
```

Con esto tendrás usuarios, libros, categorías, préstamos y reseñas listos para probar la API. El login se realiza en `POST /auth/login`.

Alternativa (sin cargar dataset): puedes crear un usuario inicial con el script:

```bash
uv run python scripts/bootstrap_user.py
```

Si tu PostgreSQL corre en WSL, este comando normalmente se ejecuta en WSL. Si corre en Windows, ejecútalo en PowerShell.

También puedes generar tu propio respaldo desde tu BD real con:

```bash
pg_dump -Ox <nombre_bd> > initial_data.sql
```

## Cumplimiento de requerimientos (1–8)

Estado a nivel de backend (API + migraciones):

| Req | Estado | Notas |
| --- | ------ | ----- |
| 1 | OK | Category + M2M con Book + CRUD `/categories` |
| 2 | OK | Review + CRUD `/reviews` + validaciones rating 1..5 y max 3 por user+book |
| 3 | OK | Book: `stock/description/language/publisher` + validaciones (idiomas permitidos, stock > 0 al crear, no negativo al actualizar) |
| 4 | OK | User: `email/phone/address/is_active` + email válido + `is_active` no editable por DTO |
| 5 | OK | Loan: `due_date/fine_amount/status` + enum + `due_date = loan_dt + 14` en creación |
| 6 | OK | Métodos avanzados en BookRepository + endpoints nuevos en `/books/*` |
| 7 | OK | Métodos avanzados en LoanRepository + endpoints nuevos en `/loans/*` |
| 8 | OK | Archivo `initial_data.sql` con categorías/libros/usuarios/préstamos/reseñas |

## Endpoints añadidos (resumen)

- Categorías: `GET/POST/PATCH/DELETE /categories`
- Reseñas: `GET/POST/PATCH/DELETE /reviews`
- Books (Req.6):
  - `GET /books/available`
  - `GET /books/by-category/{category_id}`
  - `GET /books/most-reviewed?limit=10`
  - `PATCH /books/{id}/stock` body `{ "quantity": -1 }`
  - `GET /books/search-by-author?author=...`
- Loans (Req.7):
  - `GET /loans/active`
  - `GET /loans/overdue`
  - `GET /loans/user/{user_id}`
  - `GET /loans/{id}/fine`
  - `POST /loans/{id}/return`

## Estructura del proyecto

```
app/
├── controllers/     # Endpoints de la API (auth, book, loan, user)
├── dtos/            # Data Transfer Objects
├── repositories/    # Capa de acceso a datos
├── models.py        # Modelos SQLAlchemy (User, Book, Loan)
├── db.py            # Configuración de base de datos
├── config.py        # Configuración de la aplicación
└── security.py      # Autenticación y seguridad
migrations/          # Migraciones de Alembic
```

## Crear una copia privada de este repositorio

Para crear una copia privada de este repositorio en tu propia cuenta de GitHub, conservando el historial de commits, sigue estos pasos:

- Primero, crea un repositorio privado en tu cuenta de GitHub. Guarda la URL del nuevo repositorio.
- Luego, ejecuta los siguientes comandos en tu terminal, reemplazando `<URL_DE_TU_REPOSITORIO_PRIVADO>` con la URL de tu nuevo repositorio privado:

  ```bash
  git clone https://github.com/dialvarezs/learning-vue-bd2-2025 # Clona el repositorio
  cd learning-vue-bd2-2025
  git remote remove origin                                      # Elimina el origen remoto existente
  git remote add origin <URL_DE_TU_REPOSITORIO_PRIVADO>         # Agrega el nuevo origen remoto
  git push -u origin main                                       # Sube la rama principal al
  ```
