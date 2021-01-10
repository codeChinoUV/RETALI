let zonaArchivos = document.querySelector("#archivos-adjuntos");
let archivosSeleccionados = new DataTransfer();
let inputElement = document.querySelector("#drop-zone-input");
const dropZoneElement = inputElement.closest(".drop-zone");

function agregarEventosDropzone(zonaAgregarEventosDrag){

  zonaAgregarEventosDrag.addEventListener("click", (e) => {
    inputElement.click();
  });

  zonaAgregarEventosDrag.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZoneElement.classList.add("drop-zone--over");
  });

  zonaAgregarEventosDrag.addEventListener("drop", (e) => {
    e.preventDefault();

    if (e.dataTransfer.files.length) {
      let nodoPadreZonaDrag = zonaAgregarEventosDrag.parentNode;
      nodoPadreZonaDrag.removeChild(zonaAgregarEventosDrag);
      for(let i = 0; i < e.dataTransfer.files.length; i++){
        archivosSeleccionados.items.add(e.dataTransfer.files[i]);
        let nuevaZona = crearNuevaZonaDrop();
        nodoPadreZonaDrag.appendChild(nuevaZona);
        nuevaZona.setAttribute('position', i.toString());
        nuevaZona.classList.add('archivo');
        updateThumbnail(nuevaZona, e.dataTransfer.files[i]);
      }
      inputElement.files = archivosSeleccionados.files;
    }
    colocarNuevoZonaDrop();
  });

  inputElement.addEventListener("change", (e) => {
    if (inputElement.files.length) {
      let nodoPadreZonaDrag = zonaAgregarEventosDrag.parentNode;
      nodoPadreZonaDrag.removeChild(zonaAgregarEventosDrag);
      for(let i = 0; i < inputElement.files.length; i++){
        archivosSeleccionados.items.add(inputElement.files[i]);
        let nuevaZona = crearNuevaZonaDrop();
        nuevaZona.setAttribute('position', i.toString());
        nuevaZona.classList.add('archivo');
        nuevaZona.addEventListener("click", (e) =>{
          eliminarArchivo(e.target, parseInt(e.target.getAttribute("position")));
        })
        nodoPadreZonaDrag.appendChild(nuevaZona);
        updateThumbnail(nuevaZona, inputElement.files[i]);
      }
      inputElement.files = archivosSeleccionados.files;
    }
    colocarNuevoZonaDrop();
  });

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
          eliminarArchivo(e.target, parseInt(e.target.getAttribute("position")));
        })
        zonaArchivos.appendChild(nuevaZona);
        updateThumbnail(nuevaZona, archivos.files[i]);
      }
  }
  colocarNuevoZonaDrop();
}

agregarEventosDropzone(dropZoneElement);