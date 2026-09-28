// ===============================
// Fulbito - Organizador de equipos
// ===============================

// ---------- DATOS ----------

// Cada jugador: { nombre, ritmo, pase, regate, defensa, juega }
let jugadores = [];

// Cada equipo: { nombre, jugadores: [nombres de los jugadores] }
let equipos = [];

// Cada partido: { fecha, local, visitante, golesLocal, golesVisitante }
let partidos = [];

// Combinaciones de equipos que ya se mostraron, para no repetirlas
let combinacionesVistas = [];

let formatoActual = 5;

const ATRIBUTOS = ["ritmo", "pase", "regate", "defensa"];
const NOMBRES_ATRIBUTOS = { ritmo: "Ritmo", pase: "Pase", regate: "Regate", defensa: "Defensa" };


// ---------- GUARDAR Y CARGAR (en el navegador) ----------

function guardar() {
  const datos = { jugadores, equipos, partidos, combinacionesVistas, formatoActual };
  try {
    localStorage.setItem("fulbito", JSON.stringify(datos));
  } catch (error) {
    // Si el navegador no deja guardar, la página sigue andando igual
  }
}

function cargar() {
  try {
    const texto = localStorage.getItem("fulbito");
    if (texto) {
      const datos = JSON.parse(texto);
      jugadores = datos.jugadores || [];
      equipos = datos.equipos || [];
      partidos = datos.partidos || [];
      combinacionesVistas = datos.combinacionesVistas || [];
      formatoActual = datos.formatoActual || 5;
    }
  } catch (error) {
    // Si no se puede leer, arrancamos vacío
  }
}


// ---------- UTILIDADES ----------

// Evita que un nombre con símbolos raros rompa la página
function escapar(texto) {
  return String(texto)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function mismoNombre(a, b) {
  return a.trim().toLowerCase() === b.trim().toLowerCase();
}

function buscarJugador(nombre) {
  return jugadores.find(j => mismoNombre(j.nombre, nombre));
}

function redondear(numero) {
  return numero.toFixed(1);
}

function mostrarMensaje(id, texto, tipo) {
  const elemento = document.getElementById(id);
  elemento.textContent = texto;
  elemento.className = "mensaje " + (tipo || "");
}


// ---------- MEDIAS ----------

// Media de un jugador: promedio de sus 4 atributos
function mediaJugador(jugador) {
  return (jugador.ritmo + jugador.pase + jugador.regate + jugador.defensa) / 4;
}

// Media de un grupo de nombres. Sin atributo: media general
function mediaGrupo(nombres, atributo) {
  if (nombres.length === 0) return 0;
  let suma = 0;
  for (const nombre of nombres) {
    const jugador = buscarJugador(nombre);
    if (atributo) {
      suma += jugador[atributo];
    } else {
      suma += mediaJugador(jugador);
    }
  }
  return suma / nombres.length;
}

// Diferencia entre el equipo con mejor media y el de peor media
function diferenciaDeMedias(grupos) {
  const medias = grupos.map(grupo => mediaGrupo(grupo));
  return Math.max(...medias) - Math.min(...medias);
}

// Lo mismo, pero más rápido: usa las medias ya calculadas en "mediasGuardadas".
// Se usa mientras se buscan equipos, que prueba miles de combinaciones.
let mediasGuardadas = {};

function diferenciaRapida(grupos) {
  let mayor = -Infinity;
  let menor = Infinity;
  for (const grupo of grupos) {
    let suma = 0;
    for (const nombre of grupo) suma += mediasGuardadas[nombre];
    const media = suma / grupo.length;
    if (media > mayor) mayor = media;
    if (media < menor) menor = media;
  }
  return mayor - menor;
}


// ---------- JUGADORES ----------

function guardarJugador(evento) {
  evento.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const valores = {};
  for (const atributo of ATRIBUTOS) {
    valores[atributo] = Number(document.getElementById(atributo).value);
  }

  if (nombre === "") {
    mostrarMensaje("mensajeJugador", "Poné un nombre.", "error");
    return;
  }
  for (const atributo of ATRIBUTOS) {
    const valor = valores[atributo];
    if (!Number.isInteger(valor) || valor < 1 || valor > 99) {
      mostrarMensaje("mensajeJugador", NOMBRES_ATRIBUTOS[atributo] + " tiene que ser un número entero del 1 al 99.", "error");
      return;
    }
  }

  const existente = buscarJugador(nombre);
  if (existente) {
    // Si ya existe, actualizamos sus atributos
    for (const atributo of ATRIBUTOS) {
      existente[atributo] = valores[atributo];
    }
    mostrarMensaje("mensajeJugador", "Actualizado: " + existente.nombre + ", media " + redondear(mediaJugador(existente)) + ".", "ok");
  } else {
    const nuevo = { nombre: nombre, juega: true };
    for (const atributo of ATRIBUTOS) {
      nuevo[atributo] = valores[atributo];
    }
    jugadores.push(nuevo);
    mostrarMensaje("mensajeJugador", "Listo: " + nombre + ", media " + redondear(mediaJugador(nuevo)) + ".", "ok");
  }

  document.getElementById("formJugador").reset();
  document.getElementById("nombre").focus();
  guardar();
  mostrarTodo();
}

// Pone los datos de un jugador en el formulario para cambiarlos
function editarJugador(indice) {
  const jugador = jugadores[indice];
  document.getElementById("nombre").value = jugador.nombre;
  for (const atributo of ATRIBUTOS) {
    document.getElementById(atributo).value = jugador[atributo];
  }
  mostrarMensaje("mensajeJugador", "Cambiá los números y tocá Guardar jugador.", "");
  document.getElementById("ritmo").focus();
}

function borrarJugador(indice) {
  const jugador = jugadores[indice];
  const estaEnUnEquipo = equipos.some(equipo => equipo.jugadores.some(n => mismoNombre(n, jugador.nombre)));
  if (estaEnUnEquipo) {
    mostrarMensaje("mensajeJugador", jugador.nombre + " está en un equipo. Sacalo del equipo o armá equipos nuevos antes de borrarlo.", "error");
    return;
  }
  if (!confirm("¿Borrar a " + jugador.nombre + "?")) return;
  jugadores.splice(indice, 1);
  guardar();
  mostrarTodo();
}

function cambiarJuega(indice, valor) {
  jugadores[indice].juega = valor;
  guardar();
}

function mostrarJugadores() {
  const tabla = document.getElementById("tablaJugadores");

  if (jugadores.length === 0) {
    tabla.innerHTML = '<tr><td colspan="8">Todavía no cargaste jugadores.</td></tr>';
    return;
  }

  let html = "";
  jugadores.forEach((jugador, i) => {
    html += `
      <tr>
        <td><input type="checkbox" ${jugador.juega ? "checked" : ""} onchange="cambiarJuega(${i}, this.checked)"></td>
        <td class="nombre">${escapar(jugador.nombre)}</td>
        <td>${jugador.ritmo}</td>
        <td>${jugador.pase}</td>
        <td>${jugador.regate}</td>
        <td>${jugador.defensa}</td>
        <td><b>${redondear(mediaJugador(jugador))}</b></td>
        <td>
          <button class="chico secundario" onclick="editarJugador(${i})">Editar</button>
          <button class="chico peligro" onclick="borrarJugador(${i})">Borrar</button>
        </td>
      </tr>`;
  });
  tabla.innerHTML = html;
}


// ---------- ARMAR EQUIPOS PAREJOS ----------

// Mezcla una lista al azar
function mezclar(lista) {
  const copia = [...lista];
  for (let i = copia.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copia[i], copia[j]] = [copia[j], copia[i]];
  }
  return copia;
}

// Reparte los nombres en grupos, de a uno por equipo (como cuando se "pisa")
function repartirAlAzar(nombres, cantidad) {
  const grupos = [];
  for (let i = 0; i < cantidad; i++) grupos.push([]);
  mezclar(nombres).forEach((nombre, i) => grupos[i % cantidad].push(nombre));
  return grupos;
}

// Prueba cambiar jugadores de a dos entre equipos mientras las medias se acerquen
function mejorarConIntercambios(grupos) {
  let huboMejora = true;
  while (huboMejora) {
    huboMejora = false;
    for (let a = 0; a < grupos.length; a++) {
      for (let b = a + 1; b < grupos.length; b++) {
        for (let i = 0; i < grupos[a].length; i++) {
          for (let j = 0; j < grupos[b].length; j++) {
            const antes = diferenciaRapida(grupos);
            // Intercambiamos
            [grupos[a][i], grupos[b][j]] = [grupos[b][j], grupos[a][i]];
            const despues = diferenciaRapida(grupos);
            if (despues < antes - 0.0001) {
              huboMejora = true;
            } else {
              // No mejoró: lo volvemos atrás
              [grupos[a][i], grupos[b][j]] = [grupos[b][j], grupos[a][i]];
            }
          }
        }
      }
    }
  }
}

// Cambia dos jugadores al azar de dos equipos distintos
function intercambioAlAzar(grupos) {
  const a = Math.floor(Math.random() * grupos.length);
  let b = Math.floor(Math.random() * (grupos.length - 1));
  if (b >= a) b++;
  const i = Math.floor(Math.random() * grupos[a].length);
  const j = Math.floor(Math.random() * grupos[b].length);
  [grupos[a][i], grupos[b][j]] = [grupos[b][j], grupos[a][i]];
}

// Texto que identifica una combinación sin importar el orden
function claveDe(grupos) {
  return grupos
    .map(grupo => grupo.map(n => n.toLowerCase()).sort().join(","))
    .sort()
    .join(" | ");
}

// Busca la combinación más pareja que todavía no se haya mostrado
function buscarEquiposParejos(nombres, cantidad) {
  let mejor = null;
  let mejorDiferencia = Infinity;
  const intentos = nombres.length > 30 ? 15 : 60;

  mediasGuardadas = {};
  for (const nombre of nombres) {
    mediasGuardadas[nombre] = mediaJugador(buscarJugador(nombre));
  }

  for (let intento = 0; intento < intentos; intento++) {
    const grupos = repartirAlAzar(nombres, cantidad);
    mejorarConIntercambios(grupos);

    // Si esta ya salió antes, la movemos un poco hasta encontrar una nueva
    let vueltas = 0;
    while (combinacionesVistas.includes(claveDe(grupos)) && vueltas < 50) {
      intercambioAlAzar(grupos);
      vueltas++;
    }
    if (combinacionesVistas.includes(claveDe(grupos))) continue;

    const diferencia = diferenciaRapida(grupos);
    if (diferencia < mejorDiferencia) {
      mejor = grupos;
      mejorDiferencia = diferencia;
    }
  }
  return mejor;
}

function armarEquipos(esOtraCombinacion) {
  const formato = Number(document.getElementById("formato").value);
  const cantidad = Number(document.getElementById("cantidadEquipos").value);
  const nombres = jugadores.filter(j => j.juega).map(j => j.nombre);

  if (!Number.isInteger(cantidad) || cantidad < 2) {
    mostrarMensaje("mensajeEquipos", "Tienen que ser al menos 2 equipos.", "error");
    return;
  }

  const necesarios = formato * cantidad;
  if (nombres.length < necesarios) {
    const faltan = necesarios - nombres.length;
    mostrarMensaje("mensajeEquipos",
      "Faltan " + faltan + " jugador(es): para " + cantidad + " equipos de F" + formato +
      " se necesitan " + necesarios + " y juegan " + nombres.length + ". No inventamos jugadores.", "error");
    return;
  }

  if (partidos.length > 0 && !confirm("Hay un torneo armado. Si cambiás los equipos se borra el torneo. ¿Seguir?")) {
    return;
  }

  // "Armar" empieza de cero; "Otra combinación" no repite las ya mostradas
  if (!esOtraCombinacion || equipos.length === 0) {
    combinacionesVistas = [];
  } else {
    combinacionesVistas.push(claveDe(equipos.map(e => e.jugadores)));
  }

  const grupos = buscarEquiposParejos(nombres, cantidad);
  if (grupos === null) {
    mostrarMensaje("mensajeEquipos", "No hay otra combinación distinta de las que ya viste.", "error");
    return;
  }

  // Ordenamos cada equipo de mejor a peor jugador
  for (const grupo of grupos) {
    grupo.sort((x, y) => mediaJugador(buscarJugador(y)) - mediaJugador(buscarJugador(x)));
  }

  equipos = grupos.map((grupo, i) => ({ nombre: "Equipo " + (i + 1), jugadores: grupo }));
  formatoActual = formato;
  partidos = [];

  const sobran = nombres.length - necesarios;
  let texto = "¡Equipos armados!";
  if (sobran > 0) texto += " Sobran " + sobran + " jugador(es) para F" + formato + ": quedan como suplentes.";
  mostrarMensaje("mensajeEquipos", texto, "ok");
  mostrarMensaje("mensajeTorneo", "", "");

  guardar();
  mostrarTodo();
}


// ---------- MODIFICAR EQUIPOS A MANO ----------

function moverJugador(equipoOrigen, posicion, equipoDestino) {
  equipoDestino = Number(equipoDestino);
  if (equipoDestino === equipoOrigen) return;

  if (equipos[equipoOrigen].jugadores.length === 1) {
    mostrarMensaje("mensajeEquipos", "No podés dejar un equipo sin jugadores.", "error");
    mostrarEquipos();
    return;
  }

  const nombre = equipos[equipoOrigen].jugadores.splice(posicion, 1)[0];
  equipos[equipoDestino].jugadores.push(nombre);
  mostrarMensaje("mensajeEquipos", nombre + " pasó a " + equipos[equipoDestino].nombre + ".", "ok");
  guardar();
  mostrarTodo();
}

function renombrarEquipo(indice) {
  const viejo = equipos[indice].nombre;
  const nuevo = prompt("Nombre nuevo para " + viejo + ":", viejo);
  if (nuevo === null || nuevo.trim() === "") return;

  const repetido = equipos.some((e, i) => i !== indice && mismoNombre(e.nombre, nuevo));
  if (repetido) {
    mostrarMensaje("mensajeEquipos", "Ya hay un equipo con ese nombre.", "error");
    return;
  }

  equipos[indice].nombre = nuevo.trim();
  // También lo cambiamos en el fixture
  for (const partido of partidos) {
    if (partido.local === viejo) partido.local = nuevo.trim();
    if (partido.visitante === viejo) partido.visitante = nuevo.trim();
  }
  guardar();
  mostrarTodo();
}

function mostrarEquipos() {
  const contenedor = document.getElementById("equipos");
  const resumen = document.getElementById("resumenEquipos");

  if (equipos.length === 0) {
    contenedor.innerHTML = "<p>Todavía no armaste equipos.</p>";
    resumen.textContent = "";
    return;
  }

  let html = "";
  equipos.forEach((equipo, e) => {
    const medias = ATRIBUTOS
      .map(a => NOMBRES_ATRIBUTOS[a] + " " + redondear(mediaGrupo(equipo.jugadores, a)))
      .join(" · ");

    let aviso = "";
    if (equipo.jugadores.length < formatoActual) {
      aviso = `<p class="mensaje error">Tiene ${equipo.jugadores.length} y F${formatoActual} pide ${formatoActual}.</p>`;
    }

    html += `
      <div class="equipo">
        <h3>
          <span>${escapar(equipo.nombre)} — ${redondear(mediaGrupo(equipo.jugadores))}</span>
          <button class="chico secundario" onclick="renombrarEquipo(${e})">Renombrar</button>
        </h3>
        <div class="medias">${medias}</div>
        ${aviso}
        <ul>`;

    equipo.jugadores.forEach((nombre, p) => {
      const jugador = buscarJugador(nombre);
      let opciones = "";
      equipos.forEach((otro, o) => {
        opciones += `<option value="${o}" ${o === e ? "selected" : ""}>${escapar(otro.nombre)}</option>`;
      });
      html += `
          <li>
            <span>${escapar(nombre)} (${redondear(mediaJugador(jugador))})</span>
            <select title="Mover a otro equipo" onchange="moverJugador(${e}, ${p}, this.value)">${opciones}</select>
          </li>`;
    });

    html += `
        </ul>
      </div>`;
  });
  contenedor.innerHTML = html;

  const medias = equipos.map(e => mediaGrupo(e.jugadores));
  const promedio = medias.reduce((a, b) => a + b, 0) / medias.length;
  resumen.textContent =
    "Promedio de las medias: " + redondear(promedio) +
    " · Diferencia entre el más fuerte y el más débil: " + diferenciaDeMedias(equipos.map(e => e.jugadores)).toFixed(2);
}


// ---------- TORNEO ----------

// Fixture todos contra todos (método del círculo)
function crearFixture(nombresEquipos, idaYVuelta) {
  const lista = [...nombresEquipos];
  if (lista.length % 2 === 1) lista.push(null); // null = fecha libre

  const total = lista.length;
  const resultado = [];

  for (let fecha = 0; fecha < total - 1; fecha++) {
    for (let k = 0; k < total / 2; k++) {
      let local = lista[k];
      let visitante = lista[total - 1 - k];
      if (local === null || visitante === null) continue;
      // Alternamos la localía del primer partido
      if (fecha % 2 === 1 && k === 0) [local, visitante] = [visitante, local];
      resultado.push({ fecha: fecha + 1, local, visitante, golesLocal: null, golesVisitante: null });
    }
    // Rotamos todos menos el primero
    lista.splice(1, 0, lista.pop());
  }

  if (idaYVuelta) {
    const fechasIda = total - 1;
    const vuelta = resultado.map(p => ({
      fecha: p.fecha + fechasIda, local: p.visitante, visitante: p.local, golesLocal: null, golesVisitante: null
    }));
    resultado.push(...vuelta);
  }
  return resultado;
}

function armarTorneo() {
  if (equipos.length < 2) {
    mostrarMensaje("mensajeTorneo", "Primero armá al menos 2 equipos.", "error");
    return;
  }
  if (partidos.length > 0 && !confirm("Ya hay un torneo. Si armás otro se borran los resultados. ¿Seguir?")) {
    return;
  }
  const idaYVuelta = document.getElementById("idaYVuelta").checked;
  partidos = crearFixture(equipos.map(e => e.nombre), idaYVuelta);
  mostrarMensaje("mensajeTorneo", "Torneo armado: " + partidos.length + " partidos.", "ok");
  guardar();
  mostrarTodo();
}

function guardarResultado(indice) {
  const golesLocal = document.getElementById("local" + indice).value;
  const golesVisitante = document.getElementById("visitante" + indice).value;

  // Si borrás los dos, el partido vuelve a "sin jugar"
  if (golesLocal === "" && golesVisitante === "") {
    partidos[indice].golesLocal = null;
    partidos[indice].golesVisitante = null;
  } else {
    const gl = Number(golesLocal);
    const gv = Number(golesVisitante);
    if (golesLocal === "" || golesVisitante === "" || !Number.isInteger(gl) || !Number.isInteger(gv) || gl < 0 || gv < 0) {
      mostrarMensaje("mensajeTorneo", "Los goles tienen que ser números enteros desde 0.", "error");
      return;
    }
    partidos[indice].golesLocal = gl;
    partidos[indice].golesVisitante = gv;
  }
  mostrarMensaje("mensajeTorneo", "Resultado guardado.", "ok");
  guardar();
  mostrarTodo();
}

function mostrarFixture() {
  const contenedor = document.getElementById("fixture");
  if (partidos.length === 0) {
    contenedor.innerHTML = "<p>Todavía no armaste un torneo.</p>";
    return;
  }

  const ultimaFecha = Math.max(...partidos.map(p => p.fecha));
  let html = "";
  for (let fecha = 1; fecha <= ultimaFecha; fecha++) {
    html += `<div class="fecha"><h4>Fecha ${fecha}</h4>`;
    const juegan = [];
    partidos.forEach((p, i) => {
      if (p.fecha !== fecha) return;
      juegan.push(p.local, p.visitante);
      const gl = p.golesLocal === null ? "" : p.golesLocal;
      const gv = p.golesVisitante === null ? "" : p.golesVisitante;
      html += `
        <div class="partido">
          <span>${escapar(p.local)}</span>
          <input type="number" min="0" id="local${i}" value="${gl}">
          <span>-</span>
          <input type="number" min="0" id="visitante${i}" value="${gv}">
          <span>${escapar(p.visitante)}</span>
          <button class="chico" onclick="guardarResultado(${i})">Guardar</button>
        </div>`;
    });
    const libres = equipos.map(e => e.nombre).filter(n => !juegan.includes(n));
    if (libres.length > 0) {
      html += `<p class="libre">Libre: ${escapar(libres.join(", "))}</p>`;
    }
    html += "</div>";
  }
  contenedor.innerHTML = html;
}

function mostrarTablaDePosiciones() {
  const tabla = document.getElementById("tablaPosiciones");
  if (partidos.length === 0) {
    tabla.innerHTML = "";
    return;
  }

  const filas = {};
  for (const equipo of equipos) {
    filas[equipo.nombre] = { equipo: equipo.nombre, pj: 0, g: 0, e: 0, p: 0, gf: 0, gc: 0 };
  }

  for (const partido of partidos) {
    if (partido.golesLocal === null) continue;
    const local = filas[partido.local];
    const visitante = filas[partido.visitante];
    local.pj++;
    visitante.pj++;
    local.gf += partido.golesLocal;
    local.gc += partido.golesVisitante;
    visitante.gf += partido.golesVisitante;
    visitante.gc += partido.golesLocal;
    if (partido.golesLocal > partido.golesVisitante) {
      local.g++;
      visitante.p++;
    } else if (partido.golesLocal < partido.golesVisitante) {
      visitante.g++;
      local.p++;
    } else {
      local.e++;
      visitante.e++;
    }
  }

  const lista = Object.values(filas);
  for (const fila of lista) {
    fila.dg = fila.gf - fila.gc;
    fila.pts = fila.g * 3 + fila.e;
  }
  // Ordenamos por puntos, diferencia de gol y goles a favor
  lista.sort((a, b) => b.pts - a.pts || b.dg - a.dg || b.gf - a.gf || a.equipo.localeCompare(b.equipo));

  let html = "";
  lista.forEach((fila, i) => {
    html += `
      <tr>
        <td>${i + 1}</td>
        <td class="nombre">${escapar(fila.equipo)}</td>
        <td>${fila.pj}</td>
        <td>${fila.g}</td>
        <td>${fila.e}</td>
        <td>${fila.p}</td>
        <td>${fila.gf}</td>
        <td>${fila.gc}</td>
        <td>${fila.dg > 0 ? "+" + fila.dg : fila.dg}</td>
        <td><b>${fila.pts}</b></td>
      </tr>`;
  });
  tabla.innerHTML = html;
}


// ---------- BORRAR TODO ----------

function borrarTodo() {
  if (!confirm("¿Seguro? Se borran jugadores, equipos y torneo.")) return;
  jugadores = [];
  equipos = [];
  partidos = [];
  combinacionesVistas = [];
  guardar();
  mostrarTodo();
}


// ---------- ARRANQUE ----------

function mostrarTodo() {
  mostrarJugadores();
  mostrarEquipos();
  mostrarFixture();
  mostrarTablaDePosiciones();
}

document.getElementById("formJugador").addEventListener("submit", guardarJugador);
document.getElementById("botonArmar").addEventListener("click", () => armarEquipos(false));
document.getElementById("botonOtra").addEventListener("click", () => armarEquipos(true));
document.getElementById("botonTorneo").addEventListener("click", armarTorneo);
document.getElementById("botonBorrarTodo").addEventListener("click", borrarTodo);

cargar();
document.getElementById("formato").value = String(formatoActual);
mostrarTodo();
