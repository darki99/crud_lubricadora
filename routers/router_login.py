from app import app
from flask import render_template, request, flash, redirect, url_for, session

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para verificar y generar contraseña
from werkzeug.security import check_password_hash, generate_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *

PATH_URL_LOGIN = "public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil', methods=['GET'])
def perfil():
    if 'conectado' in session:
        return render_template('public/perfil/perfil.html', info_perfil_session=info_perfil_session())
    else:
        return redirect(url_for('inicio'))


# ---------- VISTAS DE LOGIN / REGISTRO ----------

# Crear cuenta de usuario (vista)
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html')


# Recuperar cuenta de usuario (vista)
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# ---------- REGISTRO EN BD (TABLA clientes) ----------

@app.route('/saved-register', methods=['POST'])
def cpanelResgisterUserBD():
    if request.method == 'POST' and 'name_surname' in request.form and 'pass_user' in request.form:
        nombre = request.form['name_surname'].strip()
        email_user = request.form['email_user'].strip()
        pass_user = request.form['pass_user'].strip()

        # Si en el formulario tienes un campo teléfono, úsalo:
        telefono = request.form.get('telefono', '').strip()

        if not nombre or not email_user or not pass_user:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('cpanelRegisterUser'))

        try:
            conexion_MySQLdb = connectionBD()
            cursor = conexion_MySQLdb.cursor(dictionary=True)

            # 1) Validar si ya existe un cliente con ese email
            cursor.execute(
                "SELECT id FROM clientes WHERE email = %s",
                (email_user,)
            )
            existe = cursor.fetchone()
            if existe:
                flash('Ya existe una cuenta con ese correo.', 'error')
                cursor.close()
                conexion_MySQLdb.close()
                return redirect(url_for('cpanelRegisterUser'))

            # 2) Generar hash de la contraseña
            password_hash = generate_password_hash(pass_user)

            # 3) Insertar en la tabla clientes
            cursor.execute(
                """
                INSERT INTO clientes (nombre, telefono, email, password_hash, estado)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nombre, telefono, email_user, password_hash, 'A')
            )
            conexion_MySQLdb.commit()

            cursor.close()
            conexion_MySQLdb.close()

            flash('La cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))

        except Exception as e:
            # Puedes imprimir el error en consola para depurar
            print("Error al registrar cliente:", e)
            try:
                conexion_MySQLdb.rollback()
            except Exception:
                pass
            flash('Ocurrió un problema al crear la cuenta.', 'error')
            return redirect(url_for('cpanelRegisterUser'))

    else:
        flash('El método HTTP es incorrecto.', 'error')
        return redirect(url_for('inicio'))


# ---------- ACTUALIZAR PERFIL ----------

@app.route("/actualizar-datos-perfil", methods=['POST'])
def actualizarPerfil():
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash('La contraseña actual está incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 2:
                flash('Ambas claves deben ser iguales, por favor verifique.', 'error')
                return redirect(url_for('perfil'))
            elif respuesta == 3:
                flash('La clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil'))
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# ---------- LOGIN ----------

@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))

    if request.method == 'POST' and 'email_user' in request.form and 'pass_user' in request.form:

        email_user = request.form['email_user'].strip()
        pass_user = request.form['pass_user'].strip()

        # Conexión a BD
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)

        # Usamos la tabla "clientes" y la columna "email"
        cursor.execute(
            "SELECT * FROM clientes WHERE email = %s",
            (email_user,)
        )
        account = cursor.fetchone()
        cursor.close()
        conexion_MySQLdb.close()

        if account:
            # Validamos contra la columna password_hash
            if check_password_hash(account['password_hash'], pass_user):
                # Crear datos de sesión
                session['conectado'] = True
                session['id'] = account['id']
                session['name_surname'] = account['nombre']
                session['email_user'] = account['email']

                flash('La sesión fue correcta.', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Datos incorrectos, por favor revise.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('El usuario no existe, por favor verifique.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')

    # Si es GET o faltan campos
    return render_template(f'{PATH_URL_LOGIN}/base_login.html')


# ---------- CERRAR SESIÓN ----------

@app.route('/closed-session', methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email_user', None)
            flash('Tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Recuerde que debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
