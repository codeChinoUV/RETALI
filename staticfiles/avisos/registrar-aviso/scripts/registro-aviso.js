import { validar_tamanio_campo } from "../../../scripts/validaciones.js";

/**
 * Valida que el campo nombre no este vacio y no sobre pase el tamaño maximo
 */
const validarCampoNombre = () => {
    let tamanio_maximo = 100;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El titulo del aviso no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
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
    let mensajeNovalido = "El aviso no puede estar vacio";
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

document.querySelector("form").addEventListener("submit", (e) => {
    e.preventDefault();
    validarCampoNombre();
    validarCampoDescripcion();
    let cantidadAdvertencias = document.querySelectorAll('.invalid-feedback');
    if(cantidadAdvertencias.length === 0){
        Swal.fire({
              title: '¿Estas seguro de que quieres crear el aviso, no lo podras borrar?',
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