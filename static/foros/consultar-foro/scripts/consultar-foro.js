function validarTamanio(tamanio_minino, tamanio_maximo, texto){
    let cadena_sin_espacios_extra = texto.trim();
    return cadena_sin_espacios_extra.length >=tamanio_minino && cadena_sin_espacios_extra.length <= tamanio_maximo;
}

function validarTamanioCampo(tamanio_minimo, tamanio_maximo, id, mensajeNoValido){
    let campo = document.body.querySelector("#" + id);
    if( !validarTamanio(tamanio_minimo, tamanio_maximo, campo.value)){
        let advertenciasExistentes = document.querySelectorAll("#"+id+"-invalido-mensaje");
        if(advertenciasExistentes.length === 0){
            let advertencia = document.createElement('div');
            advertencia.innerHTML= mensajeNoValido;
            advertencia.setAttribute('id',  id +'-invalido-mensaje');
            advertencia.setAttribute('class', 'invalid-feedback');
            advertencia.style.display = "block";
            campo.parentElement.appendChild(advertencia);
        }
    }else{
        let mensajeNombreInvalido = document.querySelector("#"+ id + "-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campo.parentElement.removeChild(mensajeNombreInvalido);
        }
        campo.value = campo.value.trim();
    }
}

/**
 * Valida que el campo descripción no este vacio
 */
function validarCampoParticipacion(){
    let tamanio_maximo = 10000;
    let tamanio_minimo = 1;
    let id = "id_participacion";
    let mensajeNovalido = "Este campo es requerido";
    validarTamanioCampo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

/**
 * Valida que el campo respuesta no este vacio
 */
function validarCampoRespuesta(id){
    let tamanio_maximo = 10000;
    let tamanio_minimo = 1;
    let mensajeNoValido = "Este campo es requerido";
    validarTamanioCampo(tamanio_minimo, tamanio_maximo, id, mensajeNoValido);
}

document.querySelector('#btn-enviar-participacion').addEventListener("click", (e) =>{
    e.preventDefault();
    validarCampoParticipacion();
    console.log("entro");
    let cantidadAdvertencias = document.querySelectorAll('.invalid-feedback');
    if(cantidadAdvertencias.length === 0 ){
        Swal.fire({
              title: '¿Estas seguro de que quieres participar, no podras borrarlo?',
              showCancelButton: true,
              confirmButtonText: `Guardar`,
              cancelButtonText: `Cancelar`,
            }).then((result) => {
              if (result.isConfirmed) {
                document.forms.item(0).submit();
              }
            })
    }
})

document.querySelectorAll(".form-respuesta").forEach((e) =>{
    e.addEventListener("submit", (event) =>{
        event.preventDefault();
        let idForm = e.id;
        validarCampoRespuesta("id_respuesta-"+ idForm);
        let cantidadAdvertencias = document.querySelectorAll("#id_respuesta-" + idForm + "-invalido-mensaje");
        if(cantidadAdvertencias.length === 0 ){
             Swal.fire({
              title: '¿Estas seguro de que quieres responder, no podras borrarlo?',
              showCancelButton: true,
              confirmButtonText: `Guardar`,
              cancelButtonText: `Cancelar`,
            }).then((result) => {
              if (result.isConfirmed) {
                e.submit();
              }
            })
        }
    })
})