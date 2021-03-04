const validar_tamanio = (tamanio_minino, tamanio_maximo, texto) =>{
    let cadena_sin_espacios_extra = texto.trim();
    return cadena_sin_espacios_extra.length >=tamanio_minino && cadena_sin_espacios_extra.length <= tamanio_maximo;
}

const colocarAdvertencia = (id, campo, mensajeNoValido) =>{
    let advertenciasExistentes = document.querySelectorAll("#"+id+"-invalido-mensaje");
        if(advertenciasExistentes.length === 0){
            let advertencia = document.createElement('div');
            advertencia.innerHTML= mensajeNoValido;
            advertencia.setAttribute('id',  id +'-invalido-mensaje');
            advertencia.setAttribute('class', 'invalid-feedback');
            advertencia.style.display = "block";
            campo.parentElement.appendChild(advertencia);
        }
}

const validar_tamanio_campo = (tamanio_minimo, tamanio_maximo, id, mensajeNoValido) =>{
    let campo = document.body.querySelector("#" + id);
    if( !validar_tamanio(tamanio_minimo, tamanio_maximo, campo.value)){
        colocarAdvertencia(id, campo, mensajeNoValido);
    }else{
        let mensajeNombreInvalido = document.querySelector("#"+ id + "-invalido-mensaje");
        if(mensajeNombreInvalido != null){
            campo.parentElement.removeChild(mensajeNombreInvalido);
        }
        campo.value = campo.value.trim();
    }
}