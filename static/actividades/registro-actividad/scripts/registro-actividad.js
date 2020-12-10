const configuracion_fecha_inicio = {
    enableTime: true,
    dateFormat: "d/m/y H:i",
    minDate: "today",
    defaultDate: new Date()
}

const configuracion_fecha_cierre = {
    enableTime: true,
    dateFormat: "d/m/y H:i",
    minDate: "today",
    maxDate: new Date().fp_incr(365)
}

flatpickr("#id_fecha_inicio", configuracion_fecha_inicio);
flatpickr("#id_fecha_cierre", configuracion_fecha_cierre);