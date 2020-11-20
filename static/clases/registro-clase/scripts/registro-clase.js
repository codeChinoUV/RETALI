import {validar_tamanio, validar_tamanio_campo} from "../../../scripts/validaciones.js";

function validarCampoNombre(){
    let tamanio_maximo = 120;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El nombre no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras;"
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

function validarCampoEscuela(){
    let tamanio_maximo = 100;
    let tamanio_minimo = 1;
    let id = "id_escuela";
    let mensajeNovalido = "El nombre de la escuela no puede estar vacio y debe de tener menos de "
        + tamanio_maximo.toString() + " letras;"
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

document.body.querySelector("#id_nombre").addEventListener('change', () =>{
    validarCampoNombre();
});

document.body.querySelector("#id_escuela").addEventListener('change', () =>{
    validarCampoEscuela();
});

document.body.querySelector("#btn-registrar").addEventListener('click', () =>{
    validarCampoNombre();
    validarCampoEscuela();
    let camposConErrores = document.body.querySelectorAll(".invalid-feedback");
    if(camposConErrores.length === 0){
        document.body.querySelector("form").submit();
    }
})

function mostrarImagen(src,target) {
  let fileReader=new FileReader();
  fileReader.onload = function() {
      target.src = this.result;
      target.style.visibility = "visible";
  };
  src.addEventListener("change",function() {
    fileReader.readAsDataURL(src.files[0]);
  });
}

let botonCargar = document.body.querySelector("#id_foto");
let divAPonerImagen = document.body.querySelector("#imagen-seleccionada");
mostrarImagen(botonCargar, divAPonerImagen);
