function validar_tamanio(tamanio_minino, tamanio_maximo, texto){
    let cadena_sin_espacios_extra = texto.trim();
    return cadena_sin_espacios_extra.length >=tamanio_minino && cadena_sin_espacios_extra.length <= tamanio_maximo;
}

function validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNoValido){
    let campo = document.body.querySelector("#" + id);
    if( !validar_tamanio(tamanio_minimo, tamanio_maximo, campo.value)){
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

function validarCampoNombre(){
    let tamanio_maximo = 120;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El nombre no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras";
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

function validarFotoSeleccionada(){
    let mensajeNoValido = "Debe de seleccionar  una imagen para su clase";
    let campo = document.querySelector("#id_foto")
    let advertenciasExistentes = document.querySelectorAll("#foto-invalido-mensaje");
    if(campo.files.length === 0){
        if(advertenciasExistentes.length === 0){
            let advertencia = document.createElement('div');
            advertencia.innerHTML= mensajeNoValido;
            advertencia.setAttribute('id',  'foto-invalido-mensaje');
            advertencia.setAttribute('class', 'invalid-feedback');
            advertencia.style.display = "block";
            campo.parentElement.parentElement.appendChild(advertencia);
        }
    }else{
        let mensajeNombreInvalido = document.querySelector("#foto-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campo.parentElement.parentElement.removeChild(mensajeNombreInvalido);
        }
    }
}

document.body.querySelector("#id_nombre").addEventListener('change', () =>{
    validarCampoNombre();
});

document.body.querySelector("#id_escuela").addEventListener('change', () =>{
    validarCampoEscuela();
});

document.body.querySelector("#id_foto").addEventListener('change', validarFotoSeleccionada);

document.body.querySelector("#btn-registrar").addEventListener('click', () =>{
    validarCampoNombre();
    validarCampoEscuela();
    validarFotoSeleccionada();
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
