# Biblioteca-Flask
Sistema de biblioteca desarrollado en Flask para gestionar prestamos, añadir usuarios, libros asi como tambien gestionar el acceso a administradores.<br>
Visitar aqui: https://biblioteca-flask-rqgj.onrender.com
## Pantalla principal
<img width="1615" height="730" alt="image" src="https://github.com/user-attachments/assets/f4067260-4ba7-4e7f-ad00-f72d241d7a47" />


### credenciales para acceder:

| username  | contraseña    | Rol        |
|-----------|---------------|------------|
| carlosv   | secretpass123 | superadmin |
| will_7    | password123   | admin      |
| danielson | n3wp4$$       | viewer     |
| testview  | t3$tp4ssw0rd  | viewer     |

## Estructura de Base de datos

Tablas que conforman la base de datos de 'Biblioteca.db'


|admin_roles ||
|-------------|----|
| <strong>Columna</strong> |<strong>Tipo de variable</strong>|
| id_rol    | INT |
| admin_rol        | VARCHAR(30) |

<br>

|admin_users ||
|----------|----------|
| <strong>Columna</strong> |<strong>Tipo de variable</strong>|
| id_admin   | INT AUTO_INCREMENT |
| nombre_admin   | TEXT |
| admin_user   | VARCHAR(15)|
| password   | TEXT|
| id_rol   | INT |

<br>

|libros ||
|----------|----------|
| <strong>Columna</strong> |<strong>Tipo de variable</strong>|
| ISBN   | VARCHAR(50)|
| titulo   | VARCHAR(150)|
| autor   | VARCHAR(150)|
| editorial   | VARCHAR(150)|
| año_publicacion   | INT |

<br>

|prestamos ||
|----------|----------|
| <strong>Columna</strong> |<strong>Tipo de variable</strong>|
| id_prestamo   | INT AUTO_INCREMENT|
| id_usuario  | INT|
| ISBN   | VARCHAR(50)|
| fecha_prestamo   | VARCHAR(100)|
| fecha_devolucion   | VARCHAR(100 |

<br>

|usuarios ||
|----------|----------|
| <strong>Columna</strong> |<strong>Tipo de variable</strong>|
| id_usuario   | INT AUTO_INCREMENT|
| nombre_usuario  | VARCHAR(50)|
| edad   | INT)|
| phone   | VARCHAR(100)|
| email   | VARCHAR(100 |



## 🚀 Características

- Implementacion de SQLite
- Jinja2 templates
- Hash password
- Sistema de login
- Acceso por roles (superadmin, admin y viewer)




## 🗂️ Estructura del proyecto

```text
Biblioteca- Flask/
├── Biblioteca v1/                 # Carpeta del proyecto
│   ├── app.py                     # Aplicaion princial
│   ├── biblioteca.db              # Base de datos para el proyecto
│   ├── requirements.txt           # Requerimientos necesarios para ejecutar la aplicación.
│   ├── static/                    # Imagenes
│     ├── static/                  # Hoja de estilos CSS
│   └── templates/                 # Jinja2 HTML templates
├── README.md                      # Descripcion del proyecto


```

### Contenido de los archivos

**sqldeploy.py** - Archivo que contiene los metodos para realizar conexion a la base datos, asi como tambien metodos para actualizar, editar y borrar usuarios,libros o prestamos.

**app.py** - Archivo que incluye las vistas de la aplicación (incluyendo el login).


### Renombrar base de datos

La base datos necesaria para este proyecto a sido incluida con el nombre de 'Biblioteca.db', para remplazar esta base, ir al archivo *sqldeploy.py* y modificar la siguiente linea:


```@contextmanager
def connect_db():
    # Conexión a la base de datos.
    conn = sqlite3.connect('biblioteca.db') # Ingresar el nuevo nombre o ruta de la base de datos.
```

# Instalación

# Clonar repositorio
git clone https://github.com/vhugosv7/Biblioteca-Flask.git <br>
cd Biblioteca-Flask

# Crear un entorno virtual
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r Biblioteca v1/ requirements.txt

# Ejecutar aplicacion
Biblioteca v1/app.py

