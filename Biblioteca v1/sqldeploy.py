import sqlite3
from werkzeug.security import generate_password_hash
from contextlib import contextmanager

# *** SQLite3 implementación ***
# /Users/mxuser1/Desktop/Dev/Biblioteca v1/biblioteca.db


@contextmanager
def connect_db():
    # Conexión a la base de datos.
    conn = sqlite3.connect('biblioteca.db')
    try:
        yield conn  # Ejecutar query.
        conn.commit()
    finally:
        print("Connection closed")
        conn.close()  # Cerrar conexión si hay o no errores,


# -----> METODOS PARA LIBROS

def actualizar_libro_db(titulo, autor, editorial, año, isbn):
    with connect_db() as conn:
        # Creating a cursor object
        cursor = conn.cursor()
        data = (titulo, autor, editorial, año)
        cursor.execute(f'''UPDATE libros
                       SET titulo = ?,
                       autor = ?,
                       editorial = ?,
                       año_publicacion = ?
                       WHERE
                       isbn ="{isbn}"''', data)
        print("update exitoso")


def agregar_libro_db(titulo, autor, isbn, editorial, publicacion):
    with connect_db() as conn:
        cursor = conn.cursor()
        data = (titulo, autor, isbn, editorial, publicacion)

        cursor.execute('''INSERT INTO libros
                    (titulo, autor, isbn, editorial, año_publicacion)
                    VALUES (?, ?, ?, ?, ?)''', data)


def borrar_libro_db(isbn):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE from libros
                               WHERE
                               isbn = ?''', (isbn,)).fetchone()
        print("libro borrado")


# -----> METODOS PARA ADMINISTRADOR

def borrar_admin_db(id_admin):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE from admin_users
                               WHERE
                               id_admin = ?''', (id_admin,)).fetchone()
        print("admin borrado")


def nuevo_admin_db(nombre, admin_user, password, rol):
    with connect_db() as conn:
        # Creating a cursor object
        cursor = conn.cursor()

        # Hash password from form.
        hashed_pwd = generate_password_hash(password,
                                            method='pbkdf2:sha256',
                                            salt_length=16)

        data = (nombre, admin_user, hashed_pwd, rol)

        cursor.execute('''INSERT INTO admin_users
                  (nombre_admin, admin_user, password, id_rol)
                 VALUES (?, ?, ?, ?)''', data)

        print("Admin added :D!")


def actualizar_admin_db(nombre, username, id_admin):
    data = (nombre, username)
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''UPDATE admin_users
                       SET nombre_admin = ?,
                       admin_user = ?
                       WHERE
                       id_admin ="{id_admin}"''', data)
        print(f"{nombre} actualizado")


def admin_full_info(nombre, user, password, rol, id_admin):
    with connect_db() as conn:
        cursor = conn.cursor()
        hashed_pwd = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16)
        data = (nombre, user, hashed_pwd, rol)
        cursor.execute(f'''UPDATE admin_users
                       SET nombre_admin = ?,
                       admin_user = ?,
                       password = ?,
                       id_rol = ?
                       WHERE
                       id_admin ="{id_admin}"''', data)
        return "exito"


def admin_info_same_pwd(nombre, user, rol, id_admin):
    with connect_db() as conn:
        cursor = conn.cursor()
        data = (nombre, user, rol)
        cursor.execute(f'''UPDATE admin_users
                       SET nombre_admin = ?,
                       admin_user = ?,
                       id_rol = ?
                       WHERE
                       id_admin ="{id_admin}"''', data)
        return "exito"


def detalles_admin(admin):
    with connect_db() as conn:
        cursor = conn.cursor()
        detalles = cursor.execute('''SELECT t1.id_admin, t1.nombre_admin,
                          t1.admin_user,t2.admin_rol
                          FROM admin_users AS t1
                          INNER JOIN admin_roles AS t2
                          ON t1.id_rol = t2.id_rol
                          WHERE t1.nombre_admin= ?''', (admin,)).fetchone()
        return detalles


# -----> METODOS PARA USUARIOS

def actualizar_usuario(nombre, edad, telefono, email, id_usuario):
    # Connecting to sqlite
    with connect_db() as conn:
        # Creating a cursor object
        cursor = conn.cursor()
        data = (nombre, edad, telefono, email)
        cursor.execute(f'''UPDATE usuarios
                                            SET nombre_usuario = ?,
                                            edad = ?,
                                            phone = ?,
                                            email = ?
                                            WHERE
                                            id_usuario = {id_usuario}''', data)
        print("updated")


def agregar_usuario_db(nombre, edad, phone, email):
    with connect_db() as conn:
        cursor = conn.cursor()
        # Query to INSERT records.
        data = (nombre, edad, phone, email)

        cursor.execute('''INSERT INTO usuarios
                    (nombre_usuario, edad, phone, email)
                    VALUES (?, ?, ?, ?)''', data)
        # sqlite3.IntegrityError: when there is a duplicated id
        return "Done, user added!"


def borrar_usuario_db(id_usuario):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE from usuarios
                               WHERE
                               id_usuario = ?''', (id_usuario,)).fetchone()
        print("User deleted")


# -----> METODOS PARA PRESTAMOS

def prestamos_db(id_usuario, isbn,
                 fecha_prestamo, fecha_devolucion):
    with connect_db() as conn:
        cursor = conn.cursor()

        # Creating a cursor object
        cursor = conn.cursor()

        data = (id_usuario, isbn, fecha_prestamo, fecha_devolucion)

        cursor.execute('''INSERT INTO prestamos
                    (id_usuario, isbn,
                    fecha_prestamo, fecha_devolucion)
                    VALUES (?, ?, ?, ?)''', data)

        print("Done!")


def devolucion_db(id_usuario, isbn):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE from prestamos
                               where
                               id_usuario = ?
                               AND isbn = ? ''', (id_usuario, isbn))
        print("delete executed")


# -----> METODO PARA MOSTRAR LA INFORMACION DE CADA TABLA.

def datos_tabla_db(table):
    if table != 'prestamos':
        with connect_db() as conn:
            cursor = conn.cursor()
            data = cursor.execute(f'''SELECT * FROM {table}''').fetchall()
    else:
        with connect_db() as conn:
            cursor = conn.cursor()
            sql = '''SELECT t1.id_prestamo, t1.isbn,
                          t3.titulo,t2.id_usuario, t2.nombre_usuario,
                          t1.fecha_prestamo, t1.fecha_devolucion
                          FROM prestamos AS t1
                          INNER JOIN usuarios AS t2
                          ON t1.id_usuario = t2.id_usuario
                          INNER JOIN libros AS t3
                          ON t1.isbn = t3.isbn'''
            data = cursor.execute(sql).fetchall()
    return data
