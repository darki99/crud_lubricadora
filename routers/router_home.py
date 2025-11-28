from app import app
from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    jsonify
)
from mysql.connector.errors import Error
import math  # <-- necesario para los cálculos de páginas

# Importando conexión / funciones a BD
from controllers.funciones_home import *

# Rutas base de templates
PATH_URL_EMPLEADOS = "public/empleados"
PATH_URL_INVENTARIO = "public/inventario"
PATH_URL_SERVICIOS = "public/servicios"
PATH_URL_HISTORIAL = "public/historial"



# ===================== EMPLEADOS =====================

@app.route('/registrar-empleado', methods=['GET'])
def viewFormEmpleado():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_EMPLEADOS}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-empleado', methods=['POST'])
def formEmpleado():
    if 'conectado' in session:
        if 'foto_empleado' in request.files:
            foto_perfil = request.files['foto_empleado']
            resultado = procesar_form_empleado(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_empleados'))
            else:
                flash('El empleado NO fue registrado.', 'error')
                return render_template(f'{PATH_URL_EMPLEADOS}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/lista-de-empleados', methods=['GET'])
def lista_empleados():
    if 'conectado' in session:
        # -------- PAGINACIÓN --------
        page = request.args.get('page', 1, type=int)
        per_page = 8

        empleados_all = sql_lista_empleadosBD() or []
        total = len(empleados_all)

        total_pages = math.ceil(total / per_page) if total else 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        end = start + per_page
        empleados_page = empleados_all[start:end]

        return render_template(
            f'{PATH_URL_EMPLEADOS}/lista_empleados.html',
            empleados=empleados_page,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total=total
        )
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-empleado/", methods=['GET'])
@app.route("/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def detalleEmpleado(idEmpleado=None):
    if 'conectado' in session:
        if not idEmpleado:
            return redirect(url_for('inicio'))

        detalle = sql_detalles_empleadosBD(idEmpleado) or []
        return render_template(
            f'{PATH_URL_EMPLEADOS}/detalles_empleado.html',
            detalle_empleado=detalle
        )
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(
            f'{PATH_URL_EMPLEADOS}/resultado_busqueda_empleado.html',
            dataBusqueda=resultadoBusqueda
        )
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuesta = buscarEmpleadoUnico(id)
        if respuesta:
            return render_template(
                f'{PATH_URL_EMPLEADOS}/form_empleado_update.html',
                respuestaEmpleado=respuesta
            )
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))


@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))


# ===================== INVENTARIO =====================

@app.route("/inventario", methods=['GET'])
def inventario():
    if 'conectado' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 8

        productos_all = sql_lista_inventarioBD() or []
        total = len(productos_all)

        total_pages = math.ceil(total / per_page) if total > 0 else 1
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        start = (page - 1) * per_page
        end = start + per_page
        productosBD = productos_all[start:end]

        return render_template(
            f"{PATH_URL_INVENTARIO}/inventario.html",
            productosBD=productosBD,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total=total,
        )
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# ========== NUEVO PRODUCTO ==========

@app.route("/registrar-producto", methods=['GET'])
def viewFormProducto():
    """Muestra el formulario para crear un nuevo producto."""
    if 'conectado' in session:
        return render_template(f"{PATH_URL_INVENTARIO}/form_producto.html")
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/form-registrar-producto", methods=['POST'])
def formProducto():
    """Procesa el formulario de creación de producto."""
    if 'conectado' in session:
        resp = procesar_form_producto(request.form)
        if resp:
            flash('Producto registrado correctamente', 'success')
            return redirect(url_for('inventario'))
        else:
            flash('No se pudo registrar el producto.', 'error')
            return redirect(url_for('viewFormProducto'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# ========== DETALLE PRODUCTO ==========

@app.route("/detalles-producto/<int:id_producto>", methods=['GET'])
def detalleProducto(id_producto):
    if 'conectado' in session:
        detalle = sql_detalle_productoBD(id_producto) or {}
        return render_template(
            f"{PATH_URL_INVENTARIO}/detalles_producto.html",
            producto=detalle
        )
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# ========== EDITAR PRODUCTO ==========

@app.route("/editar-producto/<int:id_producto>", methods=['GET'])
def viewEditarProducto(id_producto):
    if 'conectado' in session:
        producto = buscarProductoInventarioUnico(id_producto)
        if producto:
            return render_template(
                f"{PATH_URL_INVENTARIO}/form_producto_update.html",
                producto=producto
            )
        else:
            flash('El producto no existe.', 'error')
            return redirect(url_for('inventario'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/actualizar-producto", methods=['POST'])
def actualizarProducto():
    if 'conectado' in session:
        resp = procesar_actualizacion_producto(request)
        if resp:
            flash('Producto actualizado correctamente', 'success')
        else:
            flash('No se pudo actualizar el producto.', 'error')
        return redirect(url_for('inventario'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# ========== ELIMINAR PRODUCTO ==========

@app.route("/borrar-producto/<int:id_producto>", methods=['GET'])
def borrarProducto(id_producto):
    if 'conectado' in session:
        resp = eliminarProducto(id_producto)
        if resp:
            flash('El producto fue eliminado correctamente', 'success')
        else:
            flash('No se pudo eliminar el producto.', 'error')
        return redirect(url_for('inventario'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))




# ===================== USUARIOS / REPORTES =====================

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        # -------- PAGINACIÓN --------
        page = request.args.get('page', 1, type=int)
        per_page = 8

        usuarios_all = lista_usuariosBD() or []
        total = len(usuarios_all)

        total_pages = math.ceil(total / per_page) if total else 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        end = start + per_page
        usuarios_page = usuarios_all[start:end]

        return render_template(
            'public/usuarios/lista_usuarios.html',
            resp_usuariosBD=usuarios_page,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total=total
        )
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<int:id>', methods=['GET'])
def borrarUsuario(id):
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    resp = eliminarUsuario(id)

    if resp and resp > 0:
        flash('El Usuario fue eliminado correctamente', 'success')
    else:
        flash('Error, No se pudo eliminar el Usuario. 🥺', 'error')

    return redirect(url_for('usuarios'))


@app.route("/descargar-informe-empleados/", methods=['GET'])
def descargar_informe_empleados():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    

@app.route("/descargar-informe-inventario/", methods=['GET'])
def reporteInventarioBD():
    if 'conectado' in session:
        return generarReporteExcelInventario()   # o generarReporteExcel() si usas el mismo
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    

# ===================== SERVICIOS =====================

@app.route("/servicios", methods=['GET'])
def lista_servicios():
    if 'conectado' in session:
        page = request.args.get('page', 1, type=int)
        per_page = 8

        servicios_all = sql_lista_serviciosBD() or []
        total = len(servicios_all)

        total_pages = math.ceil(total / per_page) if total else 1
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        end = start + per_page
        servicios_page = servicios_all[start:end]

        return render_template(
            f"{PATH_URL_SERVICIOS}/lista_servicios.html",
            servicios=servicios_page,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total=total
        )
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/registrar-servicio", methods=['GET'])
def viewFormServicio():
    if 'conectado' in session:
        return render_template(f"{PATH_URL_SERVICIOS}/form_servicio.html")
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/form-registrar-servicio", methods=['POST'])
def formServicio():
    if 'conectado' in session:
        resultado = procesar_form_servicio(request.form)
        if resultado:
            flash('Servicio registrado correctamente', 'success')
            return redirect(url_for('lista_servicios'))
        else:
            flash('El servicio NO fue registrado.', 'error')
            return redirect(url_for('viewFormServicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/borrar-servicio/<int:id_servicio>", methods=['GET'])
def borrarServicio(id_servicio):
    if 'conectado' in session:
        resp = eliminarServicio(id_servicio)
        if resp:
            flash('El servicio fue eliminado correctamente', 'success')
        else:
            flash('No se pudo eliminar el servicio.', 'error')
        return redirect(url_for('lista_servicios'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
# ===================== HISTORIAL SERVICIOS =====================

@app.route("/historial-servicios", methods=['GET'])
def historial_servicios():
    if 'conectado' not in session:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    page = request.args.get('page', 1, type=int)
    per_page = 10

    historial_all = sql_historial_serviciosBD() or []
    total = len(historial_all)

    total_pages = math.ceil(total / per_page) if total else 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    historial_page = historial_all[start:end]

    return render_template(
        f"{PATH_URL_HISTORIAL}/historial_servicios.html",
        historial=historial_page,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total=total
    )





