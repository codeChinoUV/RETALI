import { validar_tamanio} from "../../../scripts/validaciones.js";

function validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNoValido){
    let campo = document.body.querySelector("#" + id);
    if( !validar_tamanio(tamanio_minimo, tamanio_maximo, campo.value)){
        let advertencia = document.createElement('div');
        advertencia.innerHTML= mensajeNoValido;
        advertencia.setAttribute('id',  id +'-invalido-mensaje');
        advertencia.setAttribute('class', 'invalid-feedback');
        advertencia.style.display = "block";
        campo.parentElement.appendChild(advertencia);
    }else{
        let mensajeNombreInvalido = document.querySelector("#"+ id + "-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campo.parentElement.removeChild(mensajeNombreInvalido);
        }
        campo.value = campo.value.trim();
    }
}

document.body.querySelector("#id_nombre").addEventListener('change', () =>{
    let tamanio_maximo = 120;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El nombre no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras;"
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
});

document.body.querySelector("#id_escuela").addEventListener('change', () =>{
    let tamanio_maximo = 100;
    let tamanio_minimo = 1;
    let id = "id_escuela";
    let mensajeNovalido = "El nombre de la escuela no puede estar vacio y debe de tener menos de "
        + tamanio_maximo.toString() + " letras;"
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
});

function mostrarImagen(src,target) {
  var fr=new FileReader();
  // when image is loaded, set the src of the image where you want to display it
  fr.onload = function(e) { target.style.backgroundImage = "url("+ this.result + ")"; };
  src.addEventListener("change",function() {
    // fill fr with image data
    fr.readAsDataURL(src.files[0]);
  });
}

let botonCargar = document.body.querySelector("#id_foto");
let divAPonerImagen = document.body.querySelector("#imagen-seleccionada");
mostrarImagen(botonCargar, divAPonerImagen);
