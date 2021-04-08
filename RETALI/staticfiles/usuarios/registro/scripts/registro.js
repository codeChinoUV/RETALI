let botonMostrarContrasena = document.querySelector('#mostrar_contrasenia');
let campoContrasena = document.querySelector('#id_password');
let botonMostrarRepeticionContrasena = document.querySelector('#mostrar_repeticion_contrasenia');
let campoRepeticionContrasena = document.querySelector('#id_repeticion_contrasenia');

/**
 * Cambia el tipo de input a text o password
 * @param campo El parametro a cambiar
 */
const mostrarContrasenia = (campo) => {
    if(campo.getAttribute('type')==="password"){
        campo.setAttribute('type', 'text');
    }else{
        campo.setAttribute('type', 'password');
    }
}

/**
 * Filtra solo los numeros de un input que invoco un evento
 * @param e El evento Input invocado
 */
const filtrarSoloNumeros = (e) => {
    const entrada = Array.from(e.target.value);
    const soloNumeros = entrada.map(letra => (isNaN(letra)) ? '' : letra)
    e.target.value = soloNumeros.reduce((stringPrevio, letra) => stringPrevio + letra, '');
    e.target.value = e.target.value.trim();
}

/**
 * Valida que el campo nombre no este vacio y no sobre pase el tamaño maximo
 */
const validarCampoNombre = () => {
    let tamanio_maximo = 100;
    let tamanio_minimo = 1;
    let id = "id_nombre";
    let mensajeNovalido = "El nombre no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras";
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

/**
 * Valida que el campo nombre no este vacio y no sobre pase el tamaño maximo
 */
function validarCampoApellidos(){
    let tamanio_maximo = 120;
    let tamanio_minimo = 1;
    let id = "id_apellidos";
    let mensajeNovalido = "El campo de apellidos no puede estar vacio y debe de tener menos de " + tamanio_maximo.toString() +
            " letras";
    validar_tamanio_campo(tamanio_minimo, tamanio_maximo, id, mensajeNovalido);
}

const validarCampoCorreo = () => {
    let id = "id_email"
    let emailRegex = /^[-\w.%+]{1,64}@(?:[A-Z0-9-]{1,63}\.){1,125}[A-Z]{2,63}$/i;
    let campo = document.querySelector(`#${id}`);
    const mensajeNoValido = "El correo electronico no es valido";
    if(!emailRegex.test(campo.value)){
        colocarAdvertencia(id, campo, mensajeNoValido);
    }else{
        let mensajeNombreInvalido = document.querySelector("#"+ id + "-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campo.parentElement.removeChild(mensajeNombreInvalido);
        }
        campo.value = campo.value.trim();
    }
}

const validarContraseniaContieneLetrasMinusculas = (campo) => {
    const mensajeLetra = document.querySelector('#letter');
    let letrasMinusculas = /[a-z]/g;
    if(campo.value.match(letrasMinusculas)) {
        mensajeLetra.classList.remove("invalid");
        mensajeLetra.classList.add("valid");
    } else {
        mensajeLetra.classList.remove("valid");
        mensajeLetra.classList.add("invalid");
    }
}

const validarContraseniaContieneLetrasMayusculas = (campo) =>{
    const mensajeMayusculas = document.querySelector('#capital');
    const upperCaseLetters = /[A-Z]/g;
    if(campo.value.match(upperCaseLetters)) {
        mensajeMayusculas.classList.remove("invalid");
        mensajeMayusculas.classList.add("valid");
    } else {
        mensajeMayusculas.classList.remove("valid");
        mensajeMayusculas.classList.add("invalid");
    }
}

const validarContraseniaContieneNumeros = (campo) => {
    const mensajeNumeros = document.querySelector('#number');
    const numbers = /[0-9]/g;
    if(campo.value.match(numbers)) {
        mensajeNumeros.classList.remove("invalid");
        mensajeNumeros.classList.add("valid");
    } else {
        mensajeNumeros.classList.remove("valid");
        mensajeNumeros.classList.add("invalid");
    }
}

const validarTamanioContrasenia = (campo) => {
    const mensajeTamanio = document.querySelector('#length');
    if(campo.value.length >= 8) {
        mensajeTamanio.classList.remove("invalid");
        mensajeTamanio.classList.add("valid");
    } else {
        mensajeTamanio.classList.remove("valid");
        mensajeTamanio.classList.add("invalid");
    }
}

const validarSeguridadContrasenia = () => {
    const campo = document.querySelector('#id_password');
    validarContraseniaContieneLetrasMinusculas(campo);
    validarContraseniaContieneLetrasMayusculas(campo);
    validarContraseniaContieneNumeros(campo);
    validarTamanioContrasenia(campo);
}

const validarContraseniaCoincide = () => {
    const idContrasenia = 'id_password';
    const idRepeticionContrasenia = 'id_repeticion_contrasenia';
    const campoContrasenia = document.querySelector(`#${idContrasenia}`);
    const campoRepeticionContrasenia = document.querySelector(`#${idRepeticionContrasenia}`);
    const mensajeNoValido = "Las contraseñas no coinciden";
    if(campoContrasenia.value !== campoRepeticionContrasenia.value){
        colocarAdvertencia(idRepeticionContrasenia, campoRepeticionContrasenia, mensajeNoValido);
    }else{
        let mensajeNombreInvalido = document.querySelector("#"+ idRepeticionContrasenia + "-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campoRepeticionContrasenia.parentElement.removeChild(mensajeNombreInvalido);
        }
    }
}

document.querySelector('#id_password').onfocus = function() {
  document.getElementById("message").style.display = "block";
}

document.querySelector('#id_password').onblur = function() {
  document.getElementById("message").style.display = "none";
}

document.querySelector('#id_nombre').addEventListener('input', validarCampoNombre);

document.querySelector('#id_apellidos').addEventListener('input', validarCampoApellidos);

document.querySelector('#id_email').addEventListener('input', validarCampoCorreo);

document.querySelector('#id_password').addEventListener('input', validarSeguridadContrasenia);

document.querySelector('#id_repeticion_contrasenia').addEventListener('input', validarContraseniaCoincide);

document.querySelector('#id_numero_telefonico').addEventListener('input', filtrarSoloNumeros);

botonMostrarContrasena.addEventListener('click', () => {
    mostrarContrasenia(campoContrasena);
});

 botonMostrarRepeticionContrasena.addEventListener('click', () => {
    mostrarContrasenia(campoRepeticionContrasena);
});

 document.querySelector('submit').addEventListener('submit', (e) => {
     e.preventDefault();
     const totalAdvertencias = document.querySelectorAll('.invalid-feedback');
     const totalAdvertenciasContrasenia = document.querySelectorAll('.invalid');
     if(totalAdvertencias.length === 0 && totalAdvertenciasContrasenia.length === 0) document.querySelector('form').submit();
 })