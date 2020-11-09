let botonMostrarContrasena = document.querySelector('#showPassword');
let campoContrasena = document.querySelector('#password');

botonMostrarContrasena.addEventListener('click', () => {
    if(campoContrasena.getAttribute('type')==="password"){
        campoContrasena.setAttribute('type', 'text');
    }else{
        campoContrasena.setAttribute('type', 'password');
    }
})