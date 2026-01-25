// Funciones de CATALOGO DE LIBROS//

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando catálogo...');
    
    // Asegurar que el modal esté oculto al inicio
    const modal = document.getElementById('modal-detalles');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Inicializar los libros del backend
    inicializarLibrosBackend();
    
    // Inicializar componentes del catálogo
    initCatalogo();
    
    // Configurar event listeners para las tarjetas de libros
    setupLibroCardsEventListeners();
    
    // Configurar event listeners del modal
    setupModalEventListeners();
    
    // Configurar búsqueda inicial si hay query
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
        document.getElementById('busqueda-input').value = query;
        // Realizar búsqueda automática si hay query en la URL
        setTimeout(() => {
            paginaActual = 1;
            realizarBusqueda();
        }, 500);
    }
});

// Función para inicializar los libros desde el backend
function inicializarLibrosBackend() {
    console.log('📚 Inicializando libros del backend...');
    
    // Obtener todos los libros renderizados por el backend
    const libroCards = document.querySelectorAll('[class*="libro-card-"]');
    const resultadosLibros = document.getElementById('resultados-libros');
    
    if (libroCards.length === 0) {
        console.log('No hay libros iniciales');
        return;
    }
    
    // Guardar todos los libros en la variable global
    todosLosLibros = obtenerTodosLibrosIniciales();
    
    console.log(`📚 Se cargaron ${todosLosLibros.length} libros iniciales`);
    
    // Configurar paginación inicial
    if (todosLosLibros.length > 0) {
        totalPaginas = Math.ceil(todosLosLibros.length / LIBROS_POR_PAGINA);
        
        // Si hay más de 9 libros, mostrar paginación y dividir en páginas
        if (todosLosLibros.length > LIBROS_POR_PAGINA) {
            console.log(`📖 Mostrando paginación inicial: ${totalPaginas} páginas`);
            
            // Ocultar todos los libros iniciales
            libroCards.forEach(card => {
                card.style.display = 'none';
            });
            
            // Mostrar solo los libros de la primera página
            const inicio = 0;
            const fin = LIBROS_POR_PAGINA;
            const librosPrimeraPagina = todosLosLibros.slice(inicio, fin);
            
            // Limpiar contenedor y mostrar solo los libros de la primera página
            resultadosLibros.innerHTML = '';
            mostrarLibrosEnContenedor(librosPrimeraPagina, resultadosLibros);
            
            // Configurar paginación inicial
            actualizarControlesPaginacionInicial();
            
            // Mostrar contador de resultados
            actualizarContadorResultados(todosLosLibros.length);
        } else {
            // Menos de 9 libros, mantener todos visibles y ocultar paginación
            const paginacionInicial = document.getElementById('paginacion-inicial');
            if (paginacionInicial) {
                paginacionInicial.classList.add('hidden');
            }
            
            // Actualizar contador de resultados
            actualizarContadorResultados(todosLosLibros.length);
        }
    }
}

// Función para obtener todos los libros iniciales desde las tarjetas existentes
function obtenerTodosLibrosIniciales() {
    const libroCards = document.querySelectorAll('[class*="libro-card-"]');
    const libros = [];
    
    libroCards.forEach(card => {
        const libroId = card.getAttribute('data-libro-id');
        const titulo = card.querySelector('h4')?.textContent || '';
        const autor = card.querySelector('p.text-sm.text-gray-600')?.textContent || '';
        
        // Detectar correctamente la disponibilidad
        const estadoBadge = card.querySelector('.badge');
        let disponible = true;
        
        if (estadoBadge) {
            const estadoTexto = estadoBadge.textContent.trim();
            const estadoClases = estadoBadge.className;
            disponible = estadoTexto === 'Disponible' || 
                        estadoClases.includes('estado-disponible');
        }
        
        const categoria = card.querySelector('span.text-xs.text-gray-500')?.textContent || 'General';
        const carrera = card.getAttribute('data-carrera') || 'General';
        
        libros.push({
            id: parseInt(libroId),
            titulo: titulo.trim(),
            autor: autor.trim(),
            disponible: disponible,
            categoria: categoria.replace('Sin categoría', 'General').trim(),
            carrera: carrera,
            estado: disponible ? 'disponible' : 'prestado'
        });
    });
    
    return libros;
}

// Función para mostrar libros en el contenedor
function mostrarLibrosEnContenedor(libros, contenedor) {
    if (libros.length === 0) {
        contenedor.innerHTML = `
            <div class="col-span-full text-center py-12 text-gray-500">
                <i data-lucide="book-x" class="w-16 h-16 mx-auto mb-4 text-gray-300"></i>
                <h3 class="text-xl font-semibold text-gray-400 mb-2">No hay libros en esta página</h3>
            </div>
        `;
        return;
    }

    contenedor.innerHTML = libros.map(libro => `
        <div class="libro-card focus-visible hover-lift libro-card-${libro.id}" 
             data-libro-id="${libro.id}"
             data-carrera="${libro.carrera || 'General'}"
             tabindex="0"
             role="button"
             aria-label="Ver detalles de ${libro.titulo} por ${libro.autor}">
            <div class="h-32 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg mb-3 flex items-center justify-center relative">
                <i data-lucide="book" class="w-8 h-8 text-blue-500"></i>
                ${!libro.disponible ? `
                    <div class="absolute top-2 right-2">
                        <span class="bg-red-500 text-white text-xs px-2 py-1 rounded-full">Prestado</span>
                    </div>
                ` : ''}
            </div>
            <h4 class="font-semibold text-gray-800 text-center mb-2 line-clamp-2">${libro.titulo}</h4>
            <p class="text-sm text-gray-600 text-center mb-3 line-clamp-1">${libro.autor}</p>
            <div class="flex justify-between items-center">
                <span class="badge ${libro.disponible ? 'estado-disponible' : 'estado-prestado'}">
                    ${libro.disponible ? 'Disponible' : 'Prestado'}
                </span>
                <span class="text-xs text-gray-500">${libro.categoria || 'General'}</span>
            </div>
        </div>
    `).join('');

    // Actualizar íconos
    if (window.lucide && window.lucide.createIcons) {
        lucide.createIcons();
    }
}

// Función para actualizar controles de paginación inicial
function actualizarControlesPaginacionInicial() {
    const paginacion = document.getElementById('paginacion-inicial');
    const btnAnterior = document.getElementById('pagina-anterior-inicial');
    const btnSiguiente = document.getElementById('pagina-siguiente-inicial');
    const numerosPagina = document.getElementById('numeros-pagina-inicial');
    
    if (!paginacion || totalPaginas <= 1) {
        paginacion.classList.add('hidden');
        return;
    }
    
    // Mostrar paginación
    paginacion.classList.remove('hidden');
    
    // Actualizar estado de botones
    btnAnterior.disabled = paginaActual === 1;
    btnSiguiente.disabled = paginaActual === totalPaginas;
    
    // Configurar eventos de botones
    btnAnterior.onclick = () => cambiarPaginaInicial(paginaActual - 1);
    btnSiguiente.onclick = () => cambiarPaginaInicial(paginaActual + 1);
    
    // Generar números de página
    generarNumerosPagina(numerosPagina, 'inicial');
}

// Función para cambiar página inicial
function cambiarPaginaInicial(nuevaPagina) {
    if (nuevaPagina < 1 || nuevaPagina > totalPaginas) return;
    
    paginaActual = nuevaPagina;
    
    // Obtener libros para la nueva página
    const inicio = (paginaActual - 1) * LIBROS_POR_PAGINA;
    const fin = Math.min(inicio + LIBROS_POR_PAGINA, todosLosLibros.length);
    const librosPagina = todosLosLibros.slice(inicio, fin);
    
    // Mostrar resultados de la nueva página
    const contenedor = document.getElementById('resultados-libros');
    mostrarLibrosEnContenedor(librosPagina, contenedor);
    
    // Actualizar controles de paginación
    actualizarControlesPaginacionInicial();
    
    // Re-configurar event listeners para las nuevas tarjetas
    setTimeout(setupLibroCardsEventListeners, 100);
    
    // Scroll suave hacia arriba
    window.scrollTo({
        top: contenedor.offsetTop - 100,
        behavior: 'smooth'
    });
}

// Función para generar números de página
function generarNumerosPagina(contenedor, tipo) {
    const maxPaginasMostrar = 5;
    let inicio = 1;
    let fin = totalPaginas;
    
    if (totalPaginas > maxPaginasMostrar) {
        inicio = Math.max(1, paginaActual - Math.floor(maxPaginasMostrar / 2));
        fin = Math.min(totalPaginas, inicio + maxPaginasMostrar - 1);
        
        if (fin - inicio + 1 < maxPaginasMostrar) {
            inicio = Math.max(1, fin - maxPaginasMostrar + 1);
        }
    }
    
    let numerosHTML = '';
    
    // Puntos suspensivos al inicio si es necesario
    if (inicio > 1) {
        numerosHTML += `
            <button class="px-3 py-1 text-gray-600 hover:text-blue-600 focus-visible" onclick="cambiarPagina${tipo === 'inicial' ? 'Inicial' : 'Dinamica'}(1)">
                1
            </button>
            <span class="px-2 text-gray-400">...</span>
        `;
    }
    
    // Números de página
    for (let i = inicio; i <= fin; i++) {
        numerosHTML += `
            <button class="px-3 py-1 rounded focus-visible ${paginaActual === i 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'}"
                onclick="cambiarPagina${tipo === 'inicial' ? 'Inicial' : 'Dinamica'}(${i})">
                ${i}
            </button>
        `;
    }
    
    // Puntos suspensivos al final si es necesario
    if (fin < totalPaginas) {
        numerosHTML += `
            <span class="px-2 text-gray-400">...</span>
            <button class="px-3 py-1 text-gray-600 hover:text-blue-600 focus-visible" onclick="cambiarPagina${tipo === 'inicial' ? 'Inicial' : 'Dinamica'}(${totalPaginas})">
                ${totalPaginas}
            </button>
        `;
    }
    
    contenedor.innerHTML = numerosHTML;
}

function initCatalogo() {
    console.log('🔧 Configurando búsqueda y filtros...');
    
    // Configurar búsqueda
    const formBusqueda = document.getElementById('form-busqueda');
    const busquedaInput = document.getElementById('busqueda-input');
    const ordenarSelect = document.getElementById('ordenar-por');
    
    if (formBusqueda) {
        formBusqueda.addEventListener('submit', function(e) {
            e.preventDefault();
            realizarBusqueda();
        });
    }

    // Búsqueda en tiempo real
    if (busquedaInput) {
        let timeout;
        busquedaInput.addEventListener('input', function(e) {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (e.target.value.length >= 2 || e.target.value.length === 0) {
                    realizarBusqueda();
                }
            }, 500);
        });
    }

    // Configurar filtros
    document.querySelectorAll('.filtro-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log('📝 Cambio en filtro:', this.name, this.value, this.checked);
            realizarBusqueda();
        });
    });

    // Configurar ordenamiento
    if (ordenarSelect) {
        ordenarSelect.addEventListener('change', function() {
            console.log('📝 Cambio en orden:', this.value);
            realizarBusqueda();
        });
    }

    // Configurar limpiar filtros
    const btnLimpiar = document.getElementById('limpiar-filtros');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', function() {
            console.log('🧹 Limpiando filtros...');
            
            // Limpiar todos los checkboxes
            document.querySelectorAll('.filtro-checkbox').forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Marcar solo disponible como checked
            const disponibleCheckbox = document.querySelector('input[name="disponibilidad"][value="disponible"]');
            if (disponibleCheckbox) {
                disponibleCheckbox.checked = true;
            }
            
            // Limpiar búsqueda
            if (busquedaInput) {
                busquedaInput.value = '';
            }
            
            // Resetear ordenamiento
            if (ordenarSelect) {
                ordenarSelect.value = 'titulo';
            }
            
            // Obtener libros iniciales
            todosLosLibros = obtenerTodosLibrosIniciales();
            paginaActual = 1;
            totalPaginas = Math.ceil(todosLosLibros.length / LIBROS_POR_PAGINA);
            
            // Mostrar primera página
            const inicio = 0;
            const fin = LIBROS_POR_PAGINA;
            const librosPagina = todosLosLibros.slice(inicio, fin);
            const contenedor = document.getElementById('resultados-libros');
            mostrarLibrosEnContenedor(librosPagina, contenedor);
            
            // Actualizar controles de paginación
            manejarPaginacionInicial();
            
            // Actualizar contador
            actualizarContadorResultados(todosLosLibros.length);
            
            // Actualizar título
            const tituloResultados = document.getElementById('titulo-resultados');
            if (tituloResultados) {
                tituloResultados.textContent = `Todos los libros (${todosLosLibros.length} libros)`;
            }
            
            // Re-configurar event listeners
            setTimeout(setupLibroCardsEventListeners, 100);
        });
    }
}

function setupLibroCardsEventListeners() {
    console.log('🔧 Configurando event listeners para tarjetas...');
    
    // Remover event listeners previos
    const libroCards = document.querySelectorAll('[class*="libro-card-"]');
    libroCards.forEach(card => {
        card.removeEventListener('click', handleLibroCardClick);
        card.removeEventListener('keydown', handleLibroCardKeydown);
    });
    
    // Agregar nuevos event listeners
    libroCards.forEach(card => {
        card.addEventListener('click', handleLibroCardClick);
        card.addEventListener('keydown', handleLibroCardKeydown);
    });
    
    function handleLibroCardClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const libroId = this.getAttribute('data-libro-id');
        // Verificar que el ID sea válido
        if (libroId && libroId > 0) {
            console.log('📖 Click en libro ID:', libroId);
            mostrarDetallesLibro(parseInt(libroId));
        }
    }
    
    function handleLibroCardKeydown(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            e.stopPropagation();
            
            const libroId = this.getAttribute('data-libro-id');
            // Verificar que el ID sea válido
            if (libroId && libroId > 0) {
                console.log('📖 Tecla presionada en libro ID:', libroId);
                mostrarDetallesLibro(parseInt(libroId));
            }
        }
    }
}

function setupModalEventListeners() {
    console.log('🔧 Configurando event listeners del modal...');
    
    // Configurar botón cerrar modal
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCerrarDetalles = document.getElementById('btn-cerrar-detalles');
    
    if (btnCerrarModal) {
        btnCerrarModal.addEventListener('click', cerrarModalDetalles);
    }
    
    if (btnCerrarDetalles) {
        btnCerrarDetalles.addEventListener('click', cerrarModalDetalles);
    }

    // Cerrar modal al hacer click fuera del contenido
    const modal = document.getElementById('modal-detalles');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModalDetalles();
            }
        });
    }

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modalAbierto) {
            cerrarModalDetalles();
        }
    });
}

// Función para realizar la búsqueda
async function realizarBusqueda() {
    console.log('🔍 Iniciando búsqueda...');
    
    const contenedor = document.getElementById('resultados-libros');
    const contador = document.getElementById('contador-resultados');
    const busquedaInput = document.getElementById('busqueda-input');
    const query = busquedaInput ? busquedaInput.value : '';

    if (!contenedor) return;

    // Mostrar estado de carga
    mostrarEstadoCarga(contenedor);

    try {
        const parametros = obtenerParametrosBusqueda();
        console.log('📡 Parámetros de búsqueda:', parametros);
        
        // Verificar si hay filtros activos o búsqueda
        const hayFiltrosActivos = 
            (parametros.query && parametros.query.length > 0) ||
            parametros.autores.length > 0 ||
            parametros.categorias.length > 0 ||
            (parametros.disponibilidad.length > 0 && !(parametros.disponibilidad.length === 1 && parametros.disponibilidad[0] === 'disponible')) ||
            parametros.carreras.length > 0;
        
        console.log('🔍 ¿Hay filtros activos?', hayFiltrosActivos);
        
        if (hayFiltrosActivos) {
            // Usar la API para búsquedas filtradas
            console.log('🔍 Usando API para búsqueda filtrada');
            const resultados = await buscarLibrosAPI(parametros);
            console.log('✅ Resultados recibidos:', resultados.length, 'libros');
            
            if (resultados.length === 0) {
                // No hay resultados
                mostrarNoResultados(contenedor, query);
                todosLosLibros = [];
                totalPaginas = 1;
                paginaActual = 1;
            } else {
                // Guardar todos los libros para paginación
                todosLosLibros = resultados;
                
                // Calcular paginación
                totalPaginas = Math.ceil(resultados.length / LIBROS_POR_PAGINA);
                paginaActual = 1; // Siempre empezar en página 1 para nuevas búsquedas
                
                // Obtener libros para la página actual
                const inicio = (paginaActual - 1) * LIBROS_POR_PAGINA;
                const fin = Math.min(inicio + LIBROS_POR_PAGINA, resultados.length);
                const librosPagina = resultados.slice(inicio, fin);
                
                console.log(`📖 Página ${paginaActual}/${totalPaginas}: ${librosPagina.length} libros (${resultados.length} total)`);
                
                // Mostrar resultados de la página actual
                mostrarLibrosEnContenedor(librosPagina, contenedor);
                
                // Manejar paginación dinámica
                manejarPaginacionDespuesDeBusqueda();
            }
        } else {
            // No hay filtros activos, mostrar todos los libros iniciales
            console.log('📚 Mostrando todos los libros iniciales');
            todosLosLibros = obtenerTodosLibrosIniciales();
            
            // Aplicar ordenamiento localmente si es necesario
            if (parametros.orden && parametros.orden !== 'titulo') {
                ordenarLibrosLocalmente(parametros.orden);
            }
            
            // Calcular paginación
            totalPaginas = Math.ceil(todosLosLibros.length / LIBROS_POR_PAGINA);
            
            // Restaurar a página 1 si es necesario
            if (paginaActual > totalPaginas) {
                paginaActual = 1;
            }
            
            // Obtener libros para la página actual
            const inicio = (paginaActual - 1) * LIBROS_POR_PAGINA;
            const fin = Math.min(inicio + LIBROS_POR_PAGINA, todosLosLibros.length);
            const librosPagina = todosLosLibros.slice(inicio, fin);
            
            console.log(`📖 Página ${paginaActual}/${totalPaginas}: ${librosPagina.length} libros (${todosLosLibros.length} total)`);
            
            // Mostrar resultados
            mostrarLibrosEnContenedor(librosPagina, contenedor);
            
            // Usar paginación inicial
            manejarPaginacionInicial();
        }
        
        // Actualizar contador
        actualizarContadorResultados(todosLosLibros.length);
        
        // Actualizar título de resultados
        const tituloResultados = document.getElementById('titulo-resultados');
        if (tituloResultados) {
            if (query) {
                tituloResultados.textContent = `Resultados para "${query}" (${todosLosLibros.length} libros)`;
            } else if (hayFiltrosActivos) {
                tituloResultados.textContent = `Libros filtrados (${todosLosLibros.length} libros)`;
            } else {
                tituloResultados.textContent = `Todos los libros (${todosLosLibros.length} libros)`;
            }
        }
        
        // Re-configurar event listeners para las nuevas tarjetas
        setTimeout(setupLibroCardsEventListeners, 100);

    } catch (error) {
        console.error('❌ Error en la búsqueda:', error);
        mostrarErrorBusqueda(contenedor);
        
        // Ocultar ambas paginaciones
        document.getElementById('paginacion-inicial')?.classList.add('hidden');
        document.getElementById('paginacion-dinamica')?.classList.add('hidden');
    }
}

// Función para mostrar cuando no hay resultados
function mostrarNoResultados(contenedor, query) {
    contenedor.innerHTML = `
        <div class="col-span-full text-center py-12 text-gray-500">
            <i data-lucide="search-x" class="w-16 h-16 mx-auto mb-4 text-gray-300"></i>
            <h3 class="text-xl font-semibold text-gray-400 mb-2">
                No se encontraron libros
            </h3>
            <p class="text-gray-400">
                ${query ? `No hay resultados para "${query}" con los filtros aplicados` : 'No hay libros que coincidan con los filtros seleccionados'}
            </p>
        </div>
    `;
    
    // Actualizar íconos
    if (window.lucide && window.lucide.createIcons) {
        lucide.createIcons();
    }
}

// Función para ordenar libros localmente
function ordenarLibrosLocalmente(orden) {
    if (!todosLosLibros || todosLosLibros.length === 0) return;
    
    switch (orden) {
        case 'titulo':
            todosLosLibros.sort((a, b) => a.titulo.localeCompare(b.titulo));
            break;
        case 'titulo-desc':
            todosLosLibros.sort((a, b) => b.titulo.localeCompare(a.titulo));
            break;
        case 'autor':
            todosLosLibros.sort((a, b) => a.autor.localeCompare(b.autor));
            break;
        case 'fecha':
            // Si no hay fecha, mantener el orden actual
            break;
        default:
            todosLosLibros.sort((a, b) => a.titulo.localeCompare(b.titulo));
    }
}

// Nueva función para manejar paginación inicial
function manejarPaginacionInicial() {
    const paginacionInicial = document.getElementById('paginacion-inicial');
    const paginacionDinamica = document.getElementById('paginacion-dinamica');
    
    // Mostrar/ocultar paginación inicial según resultados
    if (paginacionInicial) {
        if (todosLosLibros.length > LIBROS_POR_PAGINA) {
            console.log('📄 Mostrando paginación inicial');
            paginacionInicial.classList.remove('hidden');
            actualizarControlesPaginacionInicial();
        } else {
            console.log('📄 Ocultando paginación inicial (menos de ' + LIBROS_POR_PAGINA + ' libros)');
            paginacionInicial.classList.add('hidden');
        }
    }
    
    // Siempre ocultar paginación dinámica en modo inicial
    if (paginacionDinamica) {
        paginacionDinamica.classList.add('hidden');
    }
}

// Función para obtener parámetros de búsqueda
function obtenerParametrosBusqueda() {
    const busquedaInput = document.getElementById('busqueda-input');
    const ordenarSelect = document.getElementById('ordenar-por');
    
    // Obtener valores seleccionados
    const autores = Array.from(document.querySelectorAll('input[name="autor"]:checked')).map(cb => cb.value);
    const categorias = Array.from(document.querySelectorAll('input[name="categoria"]:checked')).map(cb => cb.value);
    const disponibilidad = Array.from(document.querySelectorAll('input[name="disponibilidad"]:checked')).map(cb => cb.value);
    const carreras = Array.from(document.querySelectorAll('input[name="carrera"]:checked')).map(cb => cb.value);
    
    console.log('🔍 Filtros activos:', { autores, categorias, disponibilidad, carreras });
    
    return {
        query: busquedaInput ? busquedaInput.value : '',
        autores: autores,
        categorias: categorias,
        disponibilidad: disponibilidad,
        carreras: carreras,
        orden: ordenarSelect ? ordenarSelect.value : 'titulo'
    };
}

async function buscarLibrosAPI(parametros) {
    console.log('📡 Enviando solicitud a API con parámetros:', parametros);
    
    try {
        const response = await fetch('/api/filtrar-libros', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(parametros)
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Respuesta de API recibida:', {
            estado: result.estado,
            cantidad_libros: result.libros ? result.libros.length : 0,
            mensaje: result.mensaje || 'Sin mensaje'
        });
        
        if (result.estado === 'ok') {
            return result.libros;
        } else {
            console.warn('⚠️ API devolvió estado no OK:', result.mensaje);
            return [];
        }
    } catch (error) {
        console.error('❌ Error en búsqueda API:', error);
        throw error;
    }
}

function mostrarEstadoCarga(contenedor) {
    contenedor.innerHTML = `
        <div class="col-span-full text-center py-12">
            <div class="spinner mx-auto mb-4"></div>
            <p class="text-gray-600">Buscando libros...</p>
        </div>
    `;
}

function mostrarErrorBusqueda(contenedor) {
    contenedor.innerHTML = `
        <div class="col-span-full text-center py-12 text-gray-500">
            <i data-lucide="alert-circle" class="w-16 h-16 mx-auto mb-4 text-red-300"></i>
            <h3 class="text-xl font-semibold text-red-400 mb-2">Error en la búsqueda</h3>
            <p class="text-gray-400">Ocurrió un error al buscar libros. Intenta nuevamente.</p>
        </div>
    `;
    if (window.lucide && window.lucide.createIcons) {
        lucide.createIcons();
    }
}

function actualizarContadorResultados(cantidad = null) {
    const contador = document.getElementById('contador-resultados');
    const numeroResultados = document.getElementById('numero-resultados');
    
    if (!contador || !numeroResultados) return;

    if (cantidad !== null) {
        numeroResultados.textContent = cantidad;
        if (cantidad > 0) {
            contador.classList.remove('hidden');
        } else {
            contador.classList.add('hidden');
        }
    }
}

// Función para manejar paginación después de búsqueda
function manejarPaginacionDespuesDeBusqueda() {
    const paginacionInicial = document.getElementById('paginacion-inicial');
    const paginacionDinamica = document.getElementById('paginacion-dinamica');
    
    // Ocultar siempre la paginación inicial después de una búsqueda
    if (paginacionInicial) {
        paginacionInicial.classList.add('hidden');
    }
    
    // Mostrar/ocultar paginación dinámica según resultados
    if (paginacionDinamica) {
        if (todosLosLibros.length > LIBROS_POR_PAGINA) {
            console.log('📄 Mostrando paginación dinámica');
            paginacionDinamica.classList.remove('hidden');
            actualizarControlesPaginacionDinamica();
        } else {
            console.log('📄 Ocultando paginación dinámica (menos de ' + LIBROS_POR_PAGINA + ' libros)');
            paginacionDinamica.classList.add('hidden');
        }
    }
}

// Función para actualizar controles de paginación dinámica
function actualizarControlesPaginacionDinamica() {
    const paginacion = document.getElementById('paginacion-dinamica');
    const btnAnterior = document.getElementById('pagina-anterior-dinamica');
    const btnSiguiente = document.getElementById('pagina-siguiente-dinamica');
    const numerosPagina = document.getElementById('numeros-pagina-dinamica');
    
    if (!paginacion) return;
    
    if (totalPaginas <= 1) {
        paginacion.classList.add('hidden');
        return;
    }
    
    // Mostrar paginación
    paginacion.classList.remove('hidden');
    
    // Actualizar estado de botones
    btnAnterior.disabled = paginaActual === 1;
    btnSiguiente.disabled = paginaActual === totalPaginas;
    
    // Configurar eventos de botones
    btnAnterior.onclick = () => cambiarPaginaDinamica(paginaActual - 1);
    btnSiguiente.onclick = () => cambiarPaginaDinamica(paginaActual + 1);
    
    // Generar números de página
    generarNumerosPagina(numerosPagina, 'dinamica');
    
    console.log(`🔄 Controles de paginación: Página ${paginaActual} de ${totalPaginas}`);
}

// Función para cambiar página dinámica
function cambiarPaginaDinamica(nuevaPagina) {
    if (nuevaPagina < 1 || nuevaPagina > totalPaginas) return;
    
    paginaActual = nuevaPagina;
    
    // Verificar que tenemos libros para paginar
    if (!todosLosLibros || todosLosLibros.length === 0) {
        console.error('No hay libros para paginar');
        return;
    }
    
    // Obtener libros para la nueva página
    const inicio = (paginaActual - 1) * LIBROS_POR_PAGINA;
    const fin = Math.min(inicio + LIBROS_POR_PAGINA, todosLosLibros.length);
    const librosPagina = todosLosLibros.slice(inicio, fin);
    
    console.log(`📖 Cambiando a página ${paginaActual}: ${librosPagina.length} libros (${todosLosLibros.length} total)`);
    
    // Mostrar resultados de la nueva página
    const contenedor = document.getElementById('resultados-libros');
    
    if (librosPagina.length === 0) {
        contenedor.innerHTML = `
            <div class="col-span-full text-center py-12 text-gray-500">
                <i data-lucide="book-x" class="w-16 h-16 mx-auto mb-4 text-gray-300"></i>
                <h3 class="text-xl font-semibold text-gray-400 mb-2">No hay libros en esta página</h3>
                <p class="text-gray-400">Intenta seleccionar otra página</p>
            </div>
        `;
    } else {
        mostrarLibrosEnContenedor(librosPagina, contenedor);
    }
    
    // Actualizar controles de paginación
    actualizarControlesPaginacionDinamica();
    
    // Re-configurar event listeners para las nuevas tarjetas
    setTimeout(setupLibroCardsEventListeners, 100);
    
    // Scroll suave hacia arriba
    window.scrollTo({
        top: contenedor.offsetTop - 100,
        behavior: 'smooth'
    });
}

// ===== FUNCIONES PARA EL POP-UP =====

// Función para mostrar detalles del libro - VERSIÓN CORREGIDA
function mostrarDetallesLibro(libroId) {
    console.log('📚 Mostrando detalles del libro ID:', libroId);
    
    // PROTECCIÓN: Verificar que el ID sea válido
    if (!libroId || libroId <= 0) {
        console.error('❌ ID de libro inválido:', libroId);
        return;
    }
    
    // Mostrar el modal inmediatamente
    const modal = document.getElementById('modal-detalles');
    modal.classList.remove('hidden');
    modalAbierto = true;
    
    // Bloquear scroll del body
    document.body.style.overflow = 'hidden';
    
    // Mostrar loading
    const contenido = document.getElementById('modal-contenido-dinamico');
    contenido.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner mx-auto mb-2"></div>
            <p class="text-gray-600">Cargando detalles del libro...</p>
        </div>
    `;
    
    // Hacer la petición a la API
    fetch(`/api/libros/${libroId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            console.log('✅ Datos recibidos:', result);
            
            if (result.estado === 'ok' && result.libro) {
                actualizarModalConDatos(result.libro);
            } else {
                throw new Error(result.mensaje || 'Libro no encontrado');
            }
        })
        .catch(error => {
            console.error('❌ Error cargando detalles:', error);
            mostrarErrorEnModal(error.message);
        });
}

function actualizarModalConDatos(libro) {
    console.log('🎨 Actualizando modal con datos:', libro);
    
    const contenido = document.getElementById('modal-contenido-dinamico');
    
    // Crear HTML con todos los datos
    contenido.innerHTML = `
        <div class="space-y-3">
            <div>
                <label class="text-sm font-medium text-gray-600 block mb-1">Título:</label>
                <p class="font-semibold text-gray-800 text-lg">${libro.titulo || 'No disponible'}</p>
            </div>
            <div>
                <label class="text-sm font-medium text-gray-600 block mb-1">Autor:</label>
                <p class="text-gray-700">${libro.autor || 'No disponible'}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Categoría:</label>
                    <p class="text-gray-700">${libro.categoria || 'No especificada'}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">COTA:</label>
                    <p class="text-gray-700">${libro.cota || 'No disponible'}</p>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Editorial:</label>
                    <p class="text-gray-700">${libro.editorial || 'No especificada'}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Tomo:</label>
                    <p class="text-gray-700">${libro.tomo || 'No especificado'}</p>
                </div>
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">UBI:</label>
                    <p class="text-gray-700">${libro.Ubicacion || 'No especificado'}</p>
                </div>      
                <div>
                    <label class="text-sm font-medium text-gray-600 block mb-1">Carrera:</label>
                    <p class="text-gray-700">${libro.carrera || 'No especificado'}</p>
                </div>               
            </div>
            <div>
                <label class="text-sm font-medium text-gray-600 block mb-1">Ejemplares:</label>
                <p class="text-gray-700">Total: ${libro.cantidad_total || 0} | Disponibles: ${libro.cantidad_disponible || 0}</p>
            </div>
            ${libro.descripcion ? `
            <div>
                <label class="text-sm font-medium text-gray-600 block mb-1">Descripción:</label>
                <p class="text-gray-700 text-sm leading-relaxed">${libro.descripcion}</p>
            </div>
            ` : ''}
            
            <!-- Sección de Acciones -->
            <div class="pt-4 border-t">
                <h4 class="text-sm font-medium text-gray-600 mb-2">Acciones:</h4>
                <div class="flex space-x-3">
                    <button id="btn-solicitar-prestamo" 
                            class="btn-primary flex-1 focus-visible disabled:opacity-50 disabled:cursor-not-allowed"
                            ${(libro.disponible && libro.cantidad_disponible > 0) ? '' : 'disabled'}>
                        <i data-lucide="book-open" class="w-4 h-4 mr-2"></i>
                        Solicitar Préstamo
                    </button>
                    <button id="btn-reservar-libro" 
                            class="btn-secondary focus-visible disabled:opacity-50 disabled:cursor-not-allowed"
                            ${(libro.disponible && libro.cantidad_disponible === 0) ? '' : 'disabled'}>
                        <i data-lucide="bookmark" class="w-4 h-4 mr-2"></i>
                        Reservar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Actualizar estado
    const estadoElement = document.getElementById('modal-estado');
    const disponible = libro.disponible || (libro.cantidad_disponible > 0);
    estadoElement.textContent = disponible ? 'Disponible' : 'Prestado';
    estadoElement.className = `badge ${disponible ? 'estado-disponible' : 'estado-prestado'} text-sm`;
    
    // Configurar botón de préstamo
    const btnPrestar = document.getElementById('btn-solicitar-prestamo');
    const btnReservar = document.getElementById('btn-reservar-libro');
    
    if (disponible && libro.cantidad_disponible > 0) {
        btnPrestar.disabled = false;
        btnPrestar.classList.remove('disabled', 'opacity-50', 'cursor-not-allowed');
        btnPrestar.onclick = () => {
            solicitarPrestamo(libro.id);
        };
    } else {
        btnPrestar.disabled = true;
        btnPrestar.classList.add('disabled', 'opacity-50', 'cursor-not-allowed');
    }
    
    // Configurar botón de reserva si no hay ejemplares disponibles
    if (disponible && libro.cantidad_disponible === 0 && libro.cantidad_total > 0) {
        btnReservar.disabled = false;
        btnReservar.classList.remove('disabled', 'opacity-50', 'cursor-not-allowed');
        btnReservar.onclick = () => {
            reservarLibro(libro.id);
        };
    } else {
        btnReservar.disabled = true;
        btnReservar.classList.add('disabled', 'opacity-50', 'cursor-not-allowed');
    }
    
    // Actualizar íconos
    if (window.lucide && window.lucide.createIcons) {
        lucide.createIcons();
    }
}

// Función para solicitar préstamo directamente desde el modal
async function solicitarPrestamo(libroId) {
    console.log('📚 Solicitando préstamo para libro ID:', libroId);
    
    // Mostrar confirmación
    const confirmar = confirm('¿Deseas solicitar el préstamo de este libro?');
    if (!confirmar) return;
    
    try {
        // Mostrar estado de carga
        const btnPrestar = document.getElementById('btn-solicitar-prestamo');
        const originalText = btnPrestar.innerHTML;
        btnPrestar.innerHTML = '<div class="spinner-small mx-auto"></div> Procesando...';
        btnPrestar.disabled = true;
        
        // Enviar solicitud al servidor
        const response = await fetch('/api/registrar-prestamo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ libro_id: libroId })
        });
        
        const result = await response.json();
        
        // Restaurar botón
        btnPrestar.innerHTML = originalText;
        
        if (result.estado === 'ok') {
            // Mostrar mensaje de éxito
            alert('✅ Préstamo solicitado exitosamente. Revisa tu correo para más detalles.');
            
            // Actualizar estado en el modal
            const estadoElement = document.getElementById('modal-estado');
            estadoElement.textContent = 'Prestado';
            estadoElement.className = 'badge estado-prestado text-sm';
            
            // Deshabilitar botón de préstamo
            btnPrestar.disabled = true;
            btnPrestar.classList.add('disabled', 'opacity-50', 'cursor-not-allowed');
            
            // Inicializa nuevamente el catálogo para reflejar cambios
            initCatalogo();
        } else {
            // Mostrar error
            alert(`❌ Error: ${result.mensaje || 'No se pudo procesar la solicitud'}`);
        }
    } catch (error) {
        console.error('❌ Error solicitando préstamo:', error);
        alert('❌ Error de conexión. Intenta nuevamente.');
        
        // Restaurar botón
        const btnPrestar = document.getElementById('btn-solicitar-prestamo');
        btnPrestar.innerHTML = '<i data-lucide="book-open" class="w-4 h-4 mr-2"></i>Solicitar Préstamo';
        btnPrestar.disabled = false;
    }
}

// Función para reservar libro
async function reservarLibro(libroId) {
    console.log('📚 Reservando libro ID:', libroId);
    
    // Mostrar confirmación
    const confirmar = confirm('¿Deseas reservar este libro? Serás notificado cuando esté disponible.');
    if (!confirmar) return;
    
    try {
        // Mostrar estado de carga
        const btnReservar = document.getElementById('btn-reservar-libro');
        const originalText = btnReservar.innerHTML;
        btnReservar.innerHTML = '<div class="spinner-small mx-auto"></div> Procesando...';
        btnReservar.disabled = true;
        
        // Enviar solicitud al servidor
        const response = await fetch('/api/reservar-libro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ libro_id: libroId })
        });
        
        const result = await response.json();
        
        // Restaurar botón
        btnReservar.innerHTML = originalText;
        
        if (result.estado === 'ok') {
            alert('✅ Libro reservado exitosamente. Te notificaremos cuando esté disponible.');
            
            // Deshabilitar botón de reserva
            btnReservar.disabled = true;
            btnReservar.classList.add('disabled', 'opacity-50', 'cursor-not-allowed');
        } else {
            alert(`❌ Error: ${result.mensaje || 'No se pudo procesar la reserva'}`);
        }
    } catch (error) {
        console.error('❌ Error reservando libro:', error);
        alert('❌ Error de conexión. Intenta nuevamente.');
        
        // Restaurar botón
        const btnReservar = document.getElementById('btn-reservar-libro');
        btnReservar.innerHTML = '<i data-lucide="bookmark" class="w-4 h-4 mr-2"></i>Reservar';
        btnReservar.disabled = false;
    }
}

function mostrarErrorEnModal(mensaje) {
    const contenido = document.getElementById('modal-contenido-dinamico');
    contenido.innerHTML = `
        <div class="text-center py-4 text-red-600">
            <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-2"></i>
            <p class="font-medium">Error al cargar los detalles</p>
            <p class="text-sm text-gray-600 mt-1">${mensaje}</p>
        </div>
    `;
    if (window.lucide && window.lucide.createIcons) {
        lucide.createIcons();
    }
}

// Función para cerrar modal de detalles
function cerrarModalDetalles() {
    console.log('❌ Cerrando modal...');
    const modal = document.getElementById('modal-detalles');
    modal.classList.add('hidden');
    modalAbierto = false;
    
    // Restaurar scroll del body
    document.body.style.overflow = 'auto';
}

// Función para alternar filtros
function toggleFilter(filterId) {
    const filterList = document.getElementById(filterId);
    const icon = filterList.previousElementSibling.querySelector('i');
    
    if (filterList.classList.contains('hidden')) {
        filterList.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
    } else {
        filterList.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    }
}

// Hacer funciones disponibles globalmente
window.toggleFilter = toggleFilter;
window.realizarBusqueda = realizarBusqueda;
window.cambiarPaginaInicial = cambiarPaginaInicial;
window.cambiarPaginaDinamica = cambiarPaginaDinamica;
window.mostrarDetallesLibro = mostrarDetallesLibro;
window.cerrarModalDetalles = cerrarModalDetalles;
window.solicitarPrestamo = solicitarPrestamo;
window.reservarLibro = reservarLibro;



// ===== FUNCIONES GLOBALES =====

// Función global para el toggle de filtros
window.toggleFilter = (listId) => {
    const list = document.getElementById(listId);
    if (!list) return;
    
    const icon = list.previousElementSibling.querySelector('i');
    list.classList.toggle('hidden');
    
    if (list.classList.contains('hidden')) {
        icon.style.transform = 'rotate(0deg)';
    } else {
        icon.style.transform = 'rotate(180deg)';
    }
};

