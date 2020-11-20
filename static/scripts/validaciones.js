function validar_tamanio(tamanio_minino, tamanio_maximo, texto){
    let cadena_sin_espacios_extra = texto.trim();
    return cadena_sin_espacios_extra.length >=tamanio_minino && cadena_sin_espacios_extra.length <= tamanio_maximo;
}

export {validar_tamanio}