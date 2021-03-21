/**
 * Valida que el campo nombre no este vacio y no sobre pase el tamaño maximo
 */
function validarCampoNombre(){
    let tamanio_maximo = 80;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El nombre no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras";
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

/**
 * Calida que el campo descripción no este vacio
 */
function validarCampoDescripcion(){
    let tamanio_maximo = 10000;
    let tamanio_minimo = 1;
    let id = "id_descripcion";
    let mensajeNovalido = "La descripción no puede estar vacia";
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

/**
 * Valida que haya una fecha de inicio seleccionada
 */
function validarFechaInicioSeleccionada(){
    let mensaje = "Debe de seleccionar una fecha de apertura";
    let campoFechaInicio = document.querySelector("#id_fecha_inicio");
    let mensajesErroneos = document.querySelectorAll("#mensaje-fecha-inicio-invalida");
    if(campoFechaInicio.value === null || campoFechaInicio.value === ''){
        if(mensajesErroneos.length == 0){
            let mensajeCampoRequerido = document.createElement("div");
            mensajeCampoRequerido.innerText = mensaje;
            mensajeCampoRequerido.setAttribute('id', 'mensaje-fecha-inicio-invalida');
            mensajeCampoRequerido.setAttribute('class', 'invalid-feedback');
            mensajeCampoRequerido.style.display = "block";
            campoFechaInicio.parentNode.appendChild(mensajeCampoRequerido);
        }
    }else{
        let mensajeInvalido = document.querySelector("#mensaje-fecha-inicio-invalida");
        if(mensajeInvalido != null){
            campoFechaInicio.parentNode.removeChild(mensajeInvalido);
        }
    }
}

/**
 * Valida que haua una fecha de cierre seleccionada
 */
function validarFechaCierreSeleccionada(){
    let mensaje = "Debe de seleccionar una fecha de cierre";
    let campoFechaCierre = document.querySelector("#id_fecha_cierre");
    let mensajesErroneos = document.querySelectorAll("#mensaje-fecha-cierre-invalida");
    if(campoFechaCierre.value === null || campoFechaCierre.value === ''){
        if(mensajesErroneos.length == 0){
            let mensajeCampoRequerido = document.createElement("div");
            mensajeCampoRequerido.innerText = mensaje;
            mensajeCampoRequerido.setAttribute('id', 'mensaje-fecha-cierre-invalida');
            mensajeCampoRequerido.setAttribute('class', 'invalid-feedback');
            mensajeCampoRequerido.style.display = "block";
            campoFechaCierre.parentNode.appendChild(mensajeCampoRequerido);
        }
    }else{
        let mensajeInvalido = document.querySelector("#mensaje-fecha-cierre-invalida");
        if(mensajeInvalido != null){
            campoFechaCierre.parentNode.removeChild(mensajeInvalido);
        }
    }
}

/*document.querySelector("input[type='submit']").addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".invalid-feedback").forEach((e) => {
        e.remove();
    })
    validarCampoNombre();
    validarCampoDescripcion();
    validarFechaInicioSeleccionada();
    validarFechaCierreSeleccionada();
    let cantidadAdvertencias = document.querySelectorAll('.invalid-feedback');
    if(cantidadAdvertencias.length === 0){
        Swal.fire({
              title: '¿Estas seguro de que quieres registrar el foro?',
              showCancelButton: true,
              confirmButtonText: `Guardar`,
              cancelButtonText: `Cancelar`,
            }).then((result) => {
              if (result.isConfirmed) {
                document.forms.item(0).submit();
              }
            })
    }
})*/