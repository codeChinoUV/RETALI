

document.querySelector("#btn-unirse-clase").addEventListener("click", (e) =>{
    e.preventDefault();
    let seccionUnirseAClase = document.querySelector("#unirse-a-clase");
    if(seccionUnirseAClase.style.display === "block"){
        seccionUnirseAClase.style.display = "none";
    }else{
        seccionUnirseAClase.style.display = "block";
    }
})

document.querySelector("#btn-cancelar-buscar").addEventListener("click", () => {
  let seccionUnirseAClase = document.querySelector("#unirse-a-clase");
  seccionUnirseAClase.style.display = "none";
})

document.querySelector("#form-buscar-clase").addEventListener("submit", (e) =>{
    e.preventDefault();
    let botonEnviar = document.querySelector("#btn-buscar");
    botonEnviar.disabled = true;
    let codigoClase = document.getElementById("codigo-clase").value;
    if(codigoClase.trim() !== ''){
        let solicitudObtenerClase = new XMLHttpRequest();
        solicitudObtenerClase.open('GET', 'obtener_informacion_clase/' + codigoClase, true);
        solicitudObtenerClase.send();
        solicitudObtenerClase.onreadystatechange = function (){
            if(this.readyState === 4 && this.status === 200){
                respuesta = JSON.parse(this.responseText);
                if(respuesta["error"]){
                    Swal.fire({
                    icon: 'error',
                    title: 'No existe',
                    text: respuesta["error"],
                  })
                    ocultarSeccionDatosClase();
                }else{
                    colocarInformacionClase(respuesta, codigoClase);
                    mostrarSeccionDatosClase();
                }
                botonEnviar.disabled = false;
            }
        }
    }
    botonEnviar.disabled = false;
} )

function mostrarSeccionDatosClase(){
    document.querySelector("#informacion-clase").style.display = "flex";
    document.querySelector("#seccion-solicitar-unirse").style.display = "flex";
}

function ocultarSeccionDatosClase(){
    document.querySelector("#informacion-clase").style.display = "none";
    document.querySelector("#seccion-solicitar-unirse").style.display = "none";
}

function colocarInformacionClase(informacion, codigo_clase){
    document.querySelector("#imagen-clase").src = informacion["foto"];
    document.querySelector("#nombre-clase").innerHTML = informacion["nombre"];
    document.querySelector("#nombre-escuela").innerHTML = informacion["escuela"];
    document.querySelector("#nombre-maestro").innerHTML = informacion["maestro"];
    if(respuesta["foto_maestro"] !== ''){
        document.querySelector("#imagen-maestro").src = informacion["foto_maestro"];
    }
    document.querySelector("#btn-solicitar-unirse").setAttribute('codigo', codigo_clase);
}

document.querySelector("#btn-solicitar-unirse").addEventListener("click", (e) =>{
    e.preventDefault();
    let codigo = e.target.getAttribute('codigo');
    e.target.disabled = true;
    if(codigo !== undefined || codigo !== ''){
        let solicitudObtenerClase = new XMLHttpRequest();
        solicitudObtenerClase.open('GET', 'unirse_a_clase/' + codigo, true);
        solicitudObtenerClase.send();
        solicitudObtenerClase.onreadystatechange = function (){
            if (solicitudObtenerClase.readyState === 4 && solicitudObtenerClase.status === 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'No se logro establecer conexión con el servidor, cheque su conexión a internet',
                })
                e.target.disabled = false;
            }
            if(this.readyState === 4 && this.status === 200){
                respuesta = JSON.parse(this.responseText);
                if(respuesta["error"]){
                    Swal.fire({
                    icon: 'error',
                    title: 'Algo salio mal...',
                    text: respuesta["error"],
                  })
                }else{
                    Swal.fire({
                    icon: 'success',
                    title: '¡Genial!',
                    text: 'Se ha enviado tu solicitud correctamente, ahora solo es necesario que tu maestro te acepte',
                    willClose: redireccionarPaginaInicio
                  })
                }
                e.target.disabled = false;
            }
        }
    }
})

function redireccionarPaginaInicio(){
    window.location.href = document.querySelector("#btn-solicitar-unirse").href;
}