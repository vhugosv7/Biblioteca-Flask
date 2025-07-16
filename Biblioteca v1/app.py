from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import pandas as pd
from werkzeug.security import check_password_hash
from sqldeploy import connect_db, actualizar_libro_db, actualizar_usuario, \
    agregar_usuario_db, agregar_libro_db, datos_tabla_db, \
    prestamos_db, nuevo_admin_db, devolucion_db, \
    borrar_libro_db, borrar_usuario_db, detalles_admin, actualizar_admin_db, \
    borrar_admin_db, admin_full_info, admin_info_same_pwd

app = Flask(__name__)



#  Evitar sesiones largas y eliminar sesion cuando el sistema es reiniciado
app.secret_key = os.urandom(24)
app.config['SESSION_PERMANENT'] = False
allowed_rol = [1, 2]  # superadmin and admin roles


@app.route('/logout')
def logout():
    # Eliminar sesion
    session.clear()
    # Redireccionar a login.
    return redirect(url_for('login'))


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        with connect_db() as conn:
            cursor = conn.cursor()
            user = cursor.execute(
                '''SELECT id_admin, nombre_admin, password,id_rol FROM
                admin_users WHERE
                admin_user = ?''', (usuario,)).fetchone()

        if user:
            # Asignar valores a la variable 'user'
            user_id, admin, stored_hash, id_rol = user
            #  Verificar si la contraseña coincide
            if check_password_hash(stored_hash, password):
                session['user_id'] = user_id
                session['username'] = usuario
                session['admin'] = admin
                session['id_rol'] = id_rol
                # Variable para saber si hay una sesion iniciada.
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                return render_template('login.html',
                                       error='''contraseña invalida,
                                       intente otra vez!''')
        else:
            # Mensaje si el usuario no encontrado
            return render_template('login.html',
                                   error_user='Usuario no encontrado !')
    return render_template('login.html')


@app.route("/biblioteca")
def index():
    #  Pagina principal
    if session.items():
        print("session started", session['admin'])
        return render_template('index.html',
                               rol=session['id_rol'],
                               usuario=session['admin'])
    else:
        # Evitar acceso si no hay una sesion iniciada.
        print("no session - index route")
        return redirect(url_for('login'))


@app.route("/buscar", methods=['GET', 'POST'])
def buscar_libros():
    consulta = request.args.get('busqueda')
    #  Dataframe para filtrar lo que hay en consulta
    df = pd.DataFrame(datos_tabla_db('libros'))
    resultado = df[df[1].str.contains(
        consulta, case=False, na=False)]
    # Dataframe a lista
    resultado = resultado.values.tolist()

    return render_template('libros.html', libros=resultado,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route("/buscar-usuario", methods=['GET', 'POST'])
def buscar_usuarios():
    consulta = request.args.get('busqueda')
    #  Dataframe para filtrar lo que hay en consulta
    df = pd.DataFrame(datos_tabla_db('usuarios'))
    resultado = df[df[1].str.contains(
        consulta, case=False, na=False)]
    resultado = resultado.values.tolist()

    return render_template('usuarios.html', usuarios=resultado,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route("/buscar-prestamo", methods=['GET', 'POST'])
def buscar_prestamos():
    consulta = request.args.get('busqueda')
    #  Dataframe para filtrar lo que hay en consulta
    df = pd.DataFrame(datos_tabla_db('prestamos'))
    resultado = df[df[1].str.contains(
        consulta, case=False, na=False)]
    resultado = resultado.values.tolist()

    return render_template('libros.html', prestamos=resultado,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route('/<admin>', methods=['GET', 'POST'])
def perfil_usuario(admin):
    # Si la variable 'session' esta vacia.
    if not session.keys():
        return redirect(url_for('logout'))

    elif session['admin'] == admin:
        #  Si hay una sesion iniciada.
        detalles = detalles_admin(admin)

    else:
        # Evitar acceso a otros perfiles.
        return redirect(url_for('perfil_usuario', admin=session['admin']))
    return render_template('perfil.html', detalles=detalles,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route('/<admin>/editar', methods=['GET', 'POST'])
def perfil_usuario_editar(admin):
    # Si no hay una sesion iniciada.
    if not session.keys() and not session.get('logged_in'):
        return redirect(url_for('logout'))

    elif session['admin'] == admin:
        # Mostrar detalles del admin.
        detalles = detalles_admin(admin)
        return render_template('editar-perfil.html',
                               usuario=admin,
                               rol=session['id_rol'], detalles=detalles)
    else:
        # Evitar acceso a otros perfiles,
        # devolver informacion solo de la sesion iniciada.
        return redirect(url_for('perfil_usuario', admin=session['admin']))


@app.route('/cambios-guardados/admin', methods=['GET', 'POST'])
def actualizar_admin_info():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))

    elif request.method == 'POST':
        #  Informacion del admin en un diccionario
        admin_info = request.form.to_dict()
        #  Metodo para actualizar en la base de datos.
        actualizar_admin_db(admin_info['nombre_editar'],
                            admin_info['usuario_editar'],
                            admin_info['id_admin'])
        #  Asignar el nuevo nombre a la sesion ya iniciada.
        session['admin'] = admin_info['nombre_editar']
        print("cambios guardados", session['admin'])

    else:
        #  Mostrar detalles de la sesion
        return redirect(url_for('perfil_usuario', admin=session['admin']))

    # Default return
    return redirect(url_for('perfil_usuario', admin=session['admin']))


@app.route("/libros", methods=['GET', 'POST'])
def manejar_libros():
    # Si hay una sesion iniciada.
    if session.items() and session['logged_in']:
        try:
            if request.method == 'POST':
                data = request.form.to_dict()
                try:
                    # Metodo para agregar libro con los datos de 'data'
                    agregar_libro_db(data['titulo'],
                                     data['autor'], str(data['isbn']),
                                     data['editorial'], data['año'])

                    #  Mensaje si el libro se agregó.
                    return render_template('success.html',
                                           success='''Registro
                                        compleatado!
                                        ''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])

                # Evitar libros con el mismo ISBN.
                except sqlite3.IntegrityError:
                    return render_template('error.html', duplicated_isbn=f'''
                                           El libro
                                           con el ISBN
                                           {(data['isbn'])} ya
                                           se encuentra registrado''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])

            # Mostrar lista de libros guardados en la base.
            elif request.method == 'GET':
                return render_template('libros.html',
                                       libros=datos_tabla_db("libros"),
                                       rol=session['id_rol'],
                                       usuario=session['admin'])
        #  Si no hay una sesion iniciada.
        except KeyError:
            return redirect(url_for('login'))

    else:
        #  Si no hay una sesion iniciada.
        print("no session - libros view")
        return redirect(url_for('login'))


@app.route("/usuarios", methods=['GET', 'POST'])
def manejar_usuarios():
    if session.items() and session['logged_in']:
        if request.method == 'POST':
            data = request.form.to_dict()
            try:
                # metodo para agregar usuarios
                agregar_usuario_db(data['nombre'],
                                   int(data['edad_usuario']),
                                   data['phone_usuario'],
                                   data['email'])
                return render_template('success.html',
                                       rol=session['id_rol'],
                                       usuario=session['admin'],
                                       success='''Registro
                                       compleatado!''')

            # Evitar usuarios duplicados
            except sqlite3.IntegrityError:
                return render_template('error.html',
                                       rol=session['id_rol'],
                                       usuario=session['admin'],
                                       duplicated=f'''El ID
                                       {(data['id_usuario'])} ya
                                       se ha asignado a alguien más,
                                       intentalo nuevamente''')

        #  Mostrar la lista con los usuarios guardados en la base.
        elif request.method == 'GET':
            return render_template('usuarios.html',
                                   usuarios=datos_tabla_db('usuarios'),
                                   rol=session['id_rol'],
                                   usuario=session['admin'])

    else:
        #  Redirigir al login si no hay sesion iniciada.
        print("no session - usuarios view")
        return redirect(url_for('login'))


@app.route("/prestamos", methods=['GET', 'POST'])
def gestionar_prestamos():
    #  Si el rol de admin es admin o superadmin.
    if not session.get('logged_in'):
        #  Mensaje si no hay sesion iniciada.
        print("no session - prestamos view")
        return redirect(url_for('login'))

    elif session.get('logged_in') and session.items():
        if request.method == 'POST':
            data = request.form.to_dict()
            id_usuario = data['id_usuario']
            isbn = str(data['isbn'])
            fecha_prestamo = data['fecha_prestamo']
            fecha_devolucion = data['fecha_devolucion']

            with connect_db() as conn:
                cursor = conn.cursor()
                data_find = cursor.execute(f'''SELECT * FROM prestamos where
                        isbn="{isbn}"''').fetchall()

                # Si el libro esta prestado a alguien más
                # evitar prestarlo a otro usuario.
                if len(data_find) == 1:
                    return render_template('error.html',
                                           error_msg='''Este
                                           libro ya se encuentra
                                           prestado por alguien más!''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])
                else:
                    # Si el libro no esta prestado, hacer el prestamo
                    prestamos_db(id_usuario, isbn,
                                 fecha_prestamo, fecha_devolucion)
                    # Mensaje mostrado al realizar el prestamo.
                    return render_template('success.html',
                                           msg_prestamo='''Prestamo
                                           realizado con exito!''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])

        #  Mostrar detalles del prestamo.
        return render_template('prestamos.html',
                               prestamos=datos_tabla_db('prestamos'),
                               usuarios=datos_tabla_db('usuarios'),
                               libros=datos_tabla_db('libros'),
                               rol=session['id_rol'],
                               usuario=session['admin'])


@app.route("/devolucion", methods=['GET', 'POST'])
def gestionar_devolucion():
    #  Acceso solo para admin y superadmin roles.
    if not session.get('logged_in'):
        #  Mensaje si no hay sesion iniciada.
        print("no session - devolucion view")
        return redirect(url_for('login'))

    elif session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            data = request.form.to_dict()
            id_usuario = int(data['id_usuario'])
            isbn = str(data['isbn'])

            with connect_db() as conn:
                cursor = conn.cursor()
                data_find = cursor.execute('''SELECT * FROM
                                       prestamos where
                                       id_usuario = ? AND isbn = ?''',
                                           (id_usuario, isbn)).fetchall()

                if len(data_find) == 1:
                    # Revisar si hay prestamo asignado al usuario y ISBN.
                    devolucion_db(id_usuario, isbn)
                    return render_template('success.html', devolucion_msg='''
                                           Devolucion
                                       realizada con exito!''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])
                else:
                    return render_template('error.html', no_book='''Prestamo no
                                    encontrado,
                                    intentalo nuevamente!''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])

        # Listado de prestamos.
        return render_template('prestamos.html', rol=session['id_rol'])
    else:
        #  Usario viewer no tine acceso, regresar al login.
        print("no tiene acceso - devolucion view")
        return redirect(url_for('index'))


# -----> VISTAS PARA SUPERADMIN

@app.route("/new-admin", methods=['GET', 'POST'])
def add_admin():
    if not session.get('logged_in'):
        #  Mensaje si no hay sesion iniciada.
        print("no session - new admin view")
        return redirect(url_for('login'))

    elif session['id_rol'] == 1 and session.items():
        roles = {
            1: "superadmin",
            2: "admin",
            3: "viewer"
        }
        if request.method == 'POST':
            #  Metodo para agregar admin a la base de datos.
            data = request.form.to_dict()
            with connect_db() as conn:
                cursor = conn.cursor()
                # Evitar admin con el mismo username.
                duplicado = cursor.execute('''SELECT * FROM admin_users
                                           where
                                           admin_user = ?
                                           ''', (data['user'],)).fetchone()

                if duplicado:
                    return render_template('error.html',
                                           error_msg=f'''El username
                                           {data['user']} ya esta
                                           asignado al alguién más,
                                           intenta con otro diferente !''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])
                else:
                    nuevo_admin_db(data['nombre'], data['user'],
                                   data['password'], data['role_admin'])
            return redirect(url_for('add_admin'))
    # Evitar acceso al viewer y admin a añadir usuarios
    elif session['id_rol'] == 3 or session['id_rol'] == 2:
        return redirect(url_for('index'))

    #  Mostrar lista completa de administradores.
    return render_template('new-admin.html', usuario=session['admin'],
                           roles=roles,
                           rol=session['id_rol'],
                           admins=datos_tabla_db('admin_users'))


@app.route("/libros-borrar", methods=['GET', 'POST'])
def borrar_libro():
    if session['id_rol'] == 1 and session.items():
        if request.method == 'POST':
            isbn = request.form['isbn']
            with connect_db() as conn:
                cursor = conn.cursor()
                libro_prestamos = cursor.execute('''select id_prestamo from
                                                 prestamos where
                                                 isbn = ?''',
                                                 (isbn,)).fetchone()

                #  Evitar borrar un libro si es que está prestado a alguien.
                if libro_prestamos:
                    return render_template('error.html', error_msg=f'''El libro
                                           con el ISBN {isbn} no
                                           puede borrarse
                                           porque se encuentra
                                           prestado a alguién.''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])
                #  Borrar libro del sistema.
                else:
                    borrar_libro_db(isbn)
                    return redirect(url_for('manejar_libros'))
    #  Evitar acceso a roles que no sean superadmin
    elif session['id_rol'] == 2 or session['id_rol'] == 3:
        return redirect(url_for('index'))
    else:
        #  No hay una sesion iniciada.
        print("no session o no super admin- borrar libro")
        return redirect(url_for('login'))

    return redirect(url_for('manejar_libros'))


@app.route("/admin-borrar", methods=['GET', 'POST'])
def borrar_admin():
    if session['id_rol'] == 1 and session.items():
        admin = request.form.to_dict()
        #  Borrar admin de la base de datos usando su id como parametro.
        borrar_admin_db(int(admin['id_admin']))
        return redirect(url_for('add_admin'))
    else:
        return redirect(url_for('login'))


@app.route("/usuarios-borrar/<tabla>", methods=['GET', 'POST'])
def borrar_usuarios(tabla):
    print(tabla)
    # Solo el "SUPERADMIN" puede borrar usuarios de la base.
    if not session.get('logged_in'):
        #  Mensaje si no hay sesion iniciada.
        print("no session - borrar usuarios link pegado")
        return redirect(url_for('login'))

    elif session['id_rol'] == 1 and session.items():
        if request.method == 'POST':
            id_usuario = request.form['id_usuario']
            print("Usuario a borrar: ", id_usuario)
            with connect_db() as conn:
                cursor = conn.cursor()
                usuario_prestamos = cursor.execute('''select
                                                   id_prestamo from
                                                 prestamos where
                                                 id_usuario = ?''',
                                                   (id_usuario,)).fetchone()

                #  Evitar eliminar usuarios si tienen un prestamo activo.
                if usuario_prestamos:
                    return render_template('error.html', error_msg=f'''El
                                           usuario
                                           {id_usuario} no
                                           puede borrarse
                                           porque ha realizado un prestamo.''',
                                           rol=session['id_rol'],
                                           usuario=session['admin'])
                else:
                    #  Borrar del sistema si el usuario
                    #  no tiene prestamos pendientes.
                    borrar_usuario_db(id_usuario)
                    return redirect(url_for('manejar_usuarios'))
        else:
            return redirect(url_for('manejar_usuarios'))
    else:
        #  Evitar acceso si no es SUPERADMIN o si noay sesion iniciada
        print("no session / no super admin- borrar usuario")
        return redirect(url_for('login'))


# -----> VISTAS PARA SUPERADMIN Y ADMIN

@app.route("/usuarios-editar/<tabla>", methods=['GET', 'POST'])
def editar_usuario(tabla):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    elif session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            print(tabla)
            usuario = request.form.to_dict()
            with connect_db() as conn:
                cursor = conn.cursor()
                #  Detalles del usuario para usar en formulario.
                actualizar = cursor.execute('''SELECT * from usuarios
                                        WHERE
                                        id_usuario = ?''', (
                                            usuario['id_usuario'],)).fetchone()
        else:
            return redirect(url_for('manejar_usuarios'))

    return render_template('update-usuarios.html', info_usuario=actualizar,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route("/usuarios-update", methods=['GET', 'POST'])
def editar_usuario_db():
    if session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            usuario_info = request.form.to_dict()
            #  Actualizar la nueva informacion proveniente del formulario en
            #  la funcion editar usuario(tabla).
            actualizar_usuario(usuario_info['nombre'],
                               usuario_info['edad_usuario'],
                               usuario_info['phone_usuario'],
                               usuario_info['email'],
                               usuario_info['id_usuario'])
    return redirect(url_for('manejar_usuarios'))


@app.route("/actualizar-libros-view", methods=['GET', 'POST'])
def actualizar_libros_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    elif session.get('logged_in'):
        if session['id_rol'] in allowed_rol and session.get('logged_in'):
            if request.method == 'POST':
                isbn = request.form['isbn']
                with connect_db() as conn:
                    cursor = conn.cursor()
                    #  Mostrar la informacion del libro con el ISBN ingresado.
                    libro_data = cursor.execute('''SELECT * from libros
                                        WHERE
                                        isbn = ?''', (isbn,)).fetchone()
                #  evitar acceso sin sesion
            else:
                return redirect(url_for('login'))

    return render_template('update-libros.html',
                           libro_data=libro_data,
                           rol=session['id_rol'],
                           usuario=session['admin'])


@app.route("/actualizar-libros", methods=['GET', 'POST'])
def actualizar_libro():
    if session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            update = request.form.to_dict()
            #  Actualizar informacion del libro con los datos
            #  en actualizar_libros_view().
            actualizar_libro_db(update['titulo'], update['autor'],
                                update['editorial'],
                                update['año'], update['isbn'])
    else:
        #  Si no hay sesion o el rol no esta autorizado.
        login()
    return redirect(url_for('manejar_libros'))


@app.route("/actualizar-admin-info", methods=['GET', 'POST'])
def actualizar_admin_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    elif session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            id_admin = request.form['id_admin']
            with connect_db() as conn:
                cursor = conn.cursor()
                #  Informacion detallada del admin para actualizar.
                admin_info = cursor.execute('''SELECT * from admin_users
                                        WHERE
                                        id_admin = ?''', (id_admin,)
                                            ).fetchone()
                roles = cursor.execute('''
                                       Select * from admin_roles''').fetchall()
        else:
            # Evitar error, regresar a la pagina principal
            return redirect(url_for('index'))
    else:
        # Evitar acceso a viewer
        return redirect(url_for('index'))

    return render_template('update-admin.html',
                           admin_info=admin_info,
                           rol=session['id_rol'],
                           usuario=session['admin'], roles=roles)


@app.route("/actualizar-admin", methods=['GET', 'POST'])
def actualizar_admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    elif session['id_rol'] in allowed_rol and session.items():
        if request.method == 'POST':
            update = request.form.to_dict()
            #  Si el admin desea actualizar tambien su contraseña.
            if len(update.keys()) == 5:
                print("nueva contraseña")
                #  Usar informacion de actualizar_admin_view()
                admin_full_info(update['nombre'], update['user'],
                                update['password'], update['rol_admin'],
                                update['id_admin'])
                return render_template('success.html', success='''Informacion
                                       actualizada''', rol=session['id_rol'],
                                       usuario=session['admin'])
            else:
                #  Usar informacion de actualizar_admin_view()
                #  sin cambiar contraseña.
                admin_info_same_pwd(update['nombre'], update['user'],
                                    update['rol_admin'],
                                    update['id_admin'])

                return render_template('success.html', success='''Informacion
                                       actualizada''', rol=session['id_rol'],
                                       usuario=session['admin'])
        else:
            # Evitar error, regresar a la pagina principal
            return redirect(url_for('index'))
    else:
        login()
    return redirect(url_for('add_admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
