
function validar_campo_seleccionado(){
    let mensaje = "Debe de seleccionar una calificacion";
    let campoCalificacion = document.querySelector("#id_calificacion");
    let mensajesErroneos = document.querySelectorAll("#mensaje-calificacion-invalida");
    if(campoCalificacion.value === "0"){
        if(mensajesErroneos.length == 0){
            let mensajeCampoRequerido = document.createElement("div");
            mensajeCampoRequerido.innerText = mensaje;
            mensajeCampoRequerido.setAttribute('id', 'mensaje-calificacion-invalida');
            mensajeCampoRequerido.setAttribute('class', 'invalid-feedback');
            mensajeCampoRequerido.style.display = "block";
            campoCalificacion.parentNode.appendChild(mensajeCampoRequerido);
        }
    }else{
        let mensajeInvalido = document.querySelector("#mensaje-calificacion-invalida");
        if(mensajeInvalido != null){
            campoCalificacion.parentNode.removeChild(mensajeInvalido);
        }
    }
}

document.body.querySelector("#btn-registar-evaluacion").addEventListener('click', (e) =>{
    e.preventDefault();
    let botonRegistro = document.querySelector("#btn-registar-evaluacion");
    let estadoActividad = botonRegistro.getAttribute("estado-activdad");
    let calificacion = document.querySelector("#id_calificacion");
    validar_campo_seleccionado();
    if(estadoActividad !== 'Cerrada'){
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'Lo siento, no puede evaluar una actividad mientras esta siga abierta',
        });
    }else{
        if(calificacion.value !== "0"){
            Swal.fire({
              title: '¿Estas seguro de que quieres guardar los cambios?',
              showCancelButton: true,
              confirmButtonText: `Guardar`,
              cancelButtonText: `Cancelar`,
            }).then((result) => {
              if (result.isConfirmed) {
                enviarFormulario();
              }
            })
        }
    }
})

function enviarFormulario(){
    let camposConErrores = document.body.querySelectorAll(".invalid-feedback");
    if(camposConErrores.length === 0){
        document.body.querySelector("form").submit();
    }
}
