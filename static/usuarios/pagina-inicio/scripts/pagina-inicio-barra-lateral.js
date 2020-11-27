const botonContraer = document.querySelector('#boton-menu');
const menu = document.querySelector('#menu-lateral');
botonContraer.addEventListener('click', () =>{
    menu.classList.toggle("menu-expandido");
    menu.classList.toggle("menu-contraido");
    document.querySelector('body').classList.toggle('body-expandido');
});