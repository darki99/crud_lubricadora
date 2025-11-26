// ===============================================
// Filtro genérico en FRONT (para cualquier tabla)
// ===============================================
function filtrarTablaFront(tableId, inputId) {
  const input = document.getElementById(inputId);
  const filtro = (input.value || "").toLowerCase();

  const tabla = document.getElementById(tableId);
  const filas = tabla.getElementsByTagName("tr");

  // i = 1 → saltar el header
  for (let i = 1; i < filas.length; i++) {
    const celdas = filas[i].getElementsByTagName("td");
    let coincide = false;

    // recorrer todas las columnas menos la última (Acción)
    for (let j = 0; j < celdas.length - 1; j++) {
      const texto = celdas[j].textContent || celdas[j].innerText;
      if (texto.toLowerCase().includes(filtro)) {
        coincide = true;
        break;
      }
    }

    filas[i].style.display = coincide ? "" : "none";
  }
}


// ===============================================
// BUSCADOR PRINCIPAL PARA TODAS LAS TABLAS
// ===============================================
async function buscadorTable(tableId) {

  // 1) EMPLEADOS → sigue usando /buscando-empleado
  if (tableId === "tbl_empleados") {
    let input = document.getElementById("search");
    let busqueda = (input.value || "").toUpperCase();
    let url = "/buscando-empleado";

    const dataPeticion = { busqueda };
    const headers = {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    };

    try {
      const response = await axios.post(url, dataPeticion, { headers });
      if (!response.status) {
        console.log(`HTTP error! status: ${response.status} 😭`);
      }

      if (response.data.fin === 0) {
        $(`#${tableId} tbody`).html(`
          <tr>
            <td colspan="6" style="text-align:center;color: red;font-weight: bold;">
              No resultados para la búsqueda:
              <strong style="text-align:center;color: #222;">${busqueda}</strong>
            </td>
          </tr>
        `);
        return;
      }

      if (response.data) {
        let miData = response.data;
        $(`#${tableId} tbody`).html("");
        $(`#${tableId} tbody`).append(miData);
      }
    } catch (error) {
      console.error(error);
    }

    return; // muy importante: salir aquí
  }

  // 2) INVENTARIO → filtro solo en la tabla actual
  if (tableId === "tbl_inventario") {
    filtrarTablaFront("tbl_inventario", "search_inventario");
    return;
  }

  // 3) USUARIOS → filtro solo en la tabla actual
  if (tableId === "tbl_usuarios") {
    filtrarTablaFront("tbl_usuarios", "search_usuarios");
    return;
  }

  // 4) SERVICIOS → filtro solo en la tabla actual
  if (tableId === "tbl_servicios") {
    filtrarTablaFront("tbl_servicios", "search_servicios");
    return;
  }
}
