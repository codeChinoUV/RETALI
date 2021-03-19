let zonaArchivos = document.querySelector("#archivos-adjuntos");
let archivosSeleccionados = new DataTransfer();
let inputElement = document.querySelector("#drop-zone-input");
var dropZoneElement = inputElement.closest(".drop-zone");
let seEstaCargando = false;

function agregarEventosDropzone(zonaAgregarEventosDrag){

  zonaAgregarEventosDrag.addEventListener("click", agregarClickListenerDropZone);
  zonaAgregarEventosDrag.addEventListener("dragover", dragOver);
  zonaAgregarEventosDrag.addEventListener("drop", procesarAgregarArchivosDrag);
  inputElement.addEventListener("change", procesarAgregarArchivosChange);

  function agregarClickListenerDropZone(e){
    if(!seEstaCargando){
      inputElement.click();
    }
  }

  function dragOver(e){
    e.preventDefault();
    dropZoneElement = inputElement.closest(".drop-zone");
    dropZoneElement.classList.add("drop-zone--over");
  }

  function crearArchivosVisualizacion(archivosAgregar, archivosSeleccionados, zonaEventos){
      let nodoPadreZonaDrag = zonaEventos.parentNode;
      nodoPadreZonaDrag.removeChild(zonaEventos);
      for(let i = 0; i < archivosAgregar.files.length; i++) {
        if (validarTamanioArchivo(archivosAgregar.files[i])) {
          archivosSeleccionados.items.add(archivosAgregar.files[i]);
          let nuevaZona = crearNuevaZonaDrop();
          nodoPadreZonaDrag.appendChild(nuevaZona);
          nuevaZona.setAttribute('position', i.toString());
          nuevaZona.addEventListener("click", (e) => {
            if (!seEstaCargando) {
              eliminarArchivo(e.target, parseInt(e.target.getAttribute("position")));
            }
          })
          nuevaZona.classList.add('archivo');
          updateThumbnail(nuevaZona, archivosAgregar.files[i]);
        }
      }
  }

  function procesarAgregarArchivosDrag(e){
    e.preventDefault();
    if (e.dataTransfer.files.length && validarCantidadArchivos(e.dataTransfer, archivosSeleccionados) &&
    !seEstaCargando) {
      crearArchivosVisualizacion(e.dataTransfer, archivosSeleccionados, zonaAgregarEventosDrag);
      colocarNuevoZonaDrop();
      inputElement.files = archivosSeleccionados.files;
    }
  }

  function procesarAgregarArchivosChange(e){
    if (inputElement.files.length && validarCantidadArchivos(inputElement, archivosSeleccionados) && !seEstaCargando) {
      inputElement = document.querySelector("#drop-zone-input");
      crearArchivosVisualizacion(inputElement, archivosSeleccionados, zonaAgregarEventosDrag);
      colocarNuevoZonaDrop();
      inputElement.files = archivosSeleccionados.files;
    }
  }

  ["dragleave", "dragend"].forEach((type) => {
    zonaAgregarEventosDrag.addEventListener(type, (e) => {
      zonaAgregarEventosDrag.classList.remove("drop-zone--over");
    });
  });

}

  function crearNuevaZonaDrop(){
    let nuevoDiv = document.createElement("div");
    nuevoDiv.classList.add("drop-zone");
    let textoInserteArchivo = document.createElement("span");
    textoInserteArchivo.classList.add("drop-zone__prompt");
    textoInserteArchivo.innerText = "Suelta los archivos o da click aquí";
    nuevoDiv.appendChild(textoInserteArchivo);
    return nuevoDiv;
  }

  function colocarNuevoZonaDrop(){
    let nuevoDivDrop = crearNuevaZonaDrop();
    inputElement = document.createElement("input");
    inputElement.type = "file";
    inputElement.id = "drop-zone-input";
    inputElement.multiple = true;
    inputElement.name = "archivos";
    nuevoDivDrop.appendChild(inputElement);
    zonaArchivos.appendChild(nuevoDivDrop);
    agregarEventosDropzone(nuevoDivDrop);
  }


/**
 * Updates the thumbnail on a drop zone element.
 *
 * @param {HTMLElement} dropZoneElement
 * @param {File} file
 */
function updateThumbnail(dropZoneElement, file) {
  let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

  // First time - remove the prompt
  if (dropZoneElement.querySelector(".drop-zone__prompt")) {
    dropZoneElement.querySelector(".drop-zone__prompt").remove();
  }

  // First time - there is no thumbnail element, so lets create it
  if (!thumbnailElement) {
    thumbnailElement = document.createElement("div");
    thumbnailElement.classList.add("drop-zone__thumb");
    dropZoneElement.appendChild(thumbnailElement);
  }
  if(file.name.length > 20){
    thumbnailElement.dataset.label = "..." + file.name.slice(-20);
  }else{
    thumbnailElement.dataset.label = file.name;
  }


  // Show thumbnail for image files
  if (file.type.startsWith("image/")) {
    const reader = new FileReader();

    reader.readAsDataURL(file);
    reader.onload = () => {
      thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
    };
  } else {
    thumbnailElement.style.backgroundImage = null;
    thumbnailElement.classList.add("file");
  }
}

/**
 * Elimina un archivo de la lista de archivos
 * @param nodo El nodo del archivo a eliminar
 * @param posicion La posicion del archivo a eliminar
 */
function eliminarArchivo(nodo, posicion){
  let nodoPadre = nodo.parentNode;
  nodoPadre.innerHTML = '';
  archivosSeleccionados.items.remove(posicion);
  inputElement.files = archivosSeleccionados.files;
  volverACrearElementos(archivosSeleccionados);
}

/**
 *  Crea en la pantalla los elementos que se pasen en archivos
 * @param archivos Los archivos que se mostraran en la pantalla
 */

function volverACrearElementos(archivos){
  if(archivos.items.length > 0){
      for(let i = 0; i < archivos.items.length; i++){
        let nuevaZona = crearNuevaZonaDrop();
        nuevaZona.setAttribute('position', i.toString());
        nuevaZona.classList.add('archivo');
        nuevaZona.addEventListener("click", (e) =>{
          if(!seEstaCargando){
            eliminarArchivo(e.target, parseInt(e.target.getAttribute("position")));
          }
        })
        zonaArchivos.appendChild(nuevaZona);
        updateThumbnail(nuevaZona, archivos.files[i]);
      }
  }
  colocarNuevoZonaDrop();
}

/**
 * Valida que la cantidad de archivos no supere los 5
 * @param archivosNuevos Los archivos a agregar
 * @param archivosViejos Los archivos previamente agregados
 * @returns {boolean} True si no supera el maximo o False si no
 */
function validarCantidadArchivos(archivosNuevos, archivosViejos){
  let cantidadDeArchivosPermitidos = true;
  const CANTIDAD_MAXIMA_ARCHIVOS = 5;
  if((archivosNuevos.files.length + archivosViejos.files.length) > CANTIDAD_MAXIMA_ARCHIVOS ){
    Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'Lo siento, No puedes adjuntar mas de 5 archivos',
        })
    cantidadDeArchivosPermitidos = false;
  }
  return cantidadDeArchivosPermitidos;
}

/**
 * Valida si el tamaño de un archivo no supera los 50 MB
 * @param archivo el archivo a validar su tamaño
 * @returns {boolean} true si el tamaño es valido o false si no
 */
function validarTamanioArchivo(archivo) {
  let tamanioValido = true;
  const TAMANIO_MAXIMO_ARCHIVO = 51200; //50 MB
  const MEGABYTE = 1024;
  let tamanioArchivo = Math.round((archivo.size)/MEGABYTE);
  if(tamanioArchivo > TAMANIO_MAXIMO_ARCHIVO){
    Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'Lo siento el archivo ' + archivo.name + ' es demasiado grande y no se agregara',
        })
    tamanioValido = false;
  }
  return tamanioValido;
}

agregarEventosDropzone(dropZoneElement);

const entregaActividadForm = document.querySelector("#entregaForm");
const progressBarFill = document.querySelector("#progressBar > .progressbar-fill");
const progressBarText = progressBarFill.querySelector(".progressbar-text");
const seccionBarraCarga = document.querySelector("#progeso-subida");
const botonEntrega = document.querySelector("button[type='submit']");

entregaActividadForm.addEventListener("submit", (e)=> {
  e.preventDefault();
  let entregaPrevia = botonEntrega.getAttribute('entrega-previa');
  if(entregaPrevia === 'si'){
    Swal.fire({
      title: 'Los archivos adjuntados previamente se borraran, ¿Estas seguro de que quieres guardar los cambios?',
      showCancelButton: true,
      confirmButtonText: `Guardar`,
      cancelButtonText: `Cancelar`,
    }).then((result) => {
      if (result.isConfirmed) {
        enviarFormulario(e);
      }
    })
  }else{
    Swal.fire({
      title: '¿Seguro que desea guardar su entrega? Podra editarla mientras esta siga abierta',
      showCancelButton: true,
      confirmButtonText: `Guardar`,
      cancelButtonText: `Cancelar`,
    }).then((result) => {
      if (result.isConfirmed) {
        enviarFormulario(e);
      }
    })
  }
});

/*
  Crea un form data a partir de la información de los inputs
 */
function crearFormData(){
  let formdata = new FormData();
  let textarea = document.querySelector("textarea[name='comentarios']");
  formdata.append(textarea.name, textarea.value);
  document.querySelectorAll("input").forEach((e) => {
    if(e.type === "file"){
      for(let i = 0; i < e.files.length; i++){
        formdata.append(e.name + "[" + i + "]", e.files[i], e.files[i].name);
      }
    }else{
      formdata.append(e.name, e.value);
    }
  });
  return formdata;
}

function enviarFormulario(e){
  seEstaCargando = true;
  let comentariosEntrega = document.querySelector("textarea[name='comentarios']");
  comentariosEntrega.disabled = true;
  let request = new XMLHttpRequest();
    request.open("POST","", true);
    request.upload.addEventListener("progress", (e) =>{
      let porcentaje = e.lengthComputable ? (e.loaded / e.total) * 100 : 0;
      progressBarFill.style.width = porcentaje.toFixed(2) + "%";
      progressBarText.textContent = porcentaje.toFixed(2) + "%";
    });
    let csrftoken = getCookie('csrftoken');
    request.setRequestHeader("csrfmiddlewaretoken", csrftoken);
    if(inputElement.files.length > 0){
      seccionBarraCarga.style.display = "block";
    }
    let datos = crearFormData();
    request.send(datos);
    request.onreadystatechange = function (aeEvt){
      seEstaCargando = false;
      comentariosEntrega.disabled = false;
      seccionBarraCarga.style.display = "none";
      if (request.readyState === 4 && request.status === 0) {
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: 'No se logro establecer conexión con el servidor, cheque su conexión a internet',
        })
        seEstaCargando = false;
        comentariosEntrega.disabled = false;
      }
      if(request.status === 500){
        Swal.fire({
            icon: 'error',
            title: 'Algo salio mal...',
            text: 'No se registro su entrega',
          })
      }else if(request.status === 400 && request.readyState === 2) {
        const error = JSON.parse(request.responseText);
        Swal.fire({
          icon: 'error',
          title: 'Lo siento...',
          text: ['error'],
        })
      }else if(request.status === 200 && request.readyState === 2){
        Swal.fire({
          icon: 'success',
          title: '¡Genial!',
          text: 'Su actividad se ha guardado correctamente',
          willClose: redireccionarActividades
        })

      }
    }
}

function redireccionarActividades(){
  const linkActual = document.querySelector("#link-redireccion");
  console.log(linkActual.href);
  window.location.href = linkActual.href;
}

/**
 *  Extrae una determinada Cookie
 * @param cname El nombre de la cookie a obtener
 * @returns {string} El valor de la cookie
 */
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) === 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}