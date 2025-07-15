# Biblioteca-Flask
Sistema de biblioteca desarrollado en Flask.

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


