document.addEventListener('DOMContentLoaded', () => {
    // Inicializar íconos de Lucide
    lucide.createIcons();

    // Variables globales
    let librosDisponibles = [];
    let prestamoConfirmado = false;

    // Inicializar la aplicación
    initApp();

    async function initApp() {
        await cargarLibrosDisponibles();
        setupEnhancedInteractions();
        setupFormHandlers();
        setupSearchInteractions();
        setupNavigationInteractions();
    }

    // ===== INTERACCIONES MEJORADAS =====
    function setupEnhancedInteractions() {
        // Mejorar hover de botones
        enhanceButtons();
        
        // Mejorar formularios
        enhanceForms();
        
        // Mejorar tarjetas
        enhanceCards();
        
        // Configurar feedback táctil
        setupTouchFeedback();
    }

    function enhanceButtons() {
        document.querySelectorAll('button').forEach(btn => {
            // Feedback al hacer hover
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-1px)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
            
            // Feedback al hacer click
            btn.addEventListener('mousedown', () => {
                btn.style.transform = 'translateY(0)';
            });
            
            btn.addEventListener('mouseup', () => {
                btn.style.transform = 'translateY(-1px)';
            });
        });
    }

    function enhanceForms() {
        // Validación en tiempo real
        document.querySelectorAll('input[required]').forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearValidation);
        });

        // Mejorar focus
        document.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('focus', () => {
                field.parentElement.classList.add('focused');
            });
            
            field.addEventListener('blur', () => {
                field.parentElement.classList.remove('focused');
            });
        });
    }

    function enhanceCards() {
        document.querySelectorAll('.libro-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    function setupTouchFeedback() {
        // Mejorar feedback táctil para móviles
        document.addEventListener('touchstart', function() {}, { passive: true });
        
        // Prevenir zoom en inputs en iOS
        document.addEventListener('touchmove', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                e.preventDefault();
            }
        }, { passive: false });
    }

    // ===== CARGA DE DATOS =====
    async function cargarLibrosDisponibles() {
        try {
            const response = await fetch('/api/libros/disponibles');
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            const result = await response.json();
            
            if (result.estado === 'ok') {
                librosDisponibles = result.libros;
                console.log('Libros disponibles cargados:', librosDisponibles.length);
            } else {
                console.error('Error en la API:', result.mensaje);
            }
        } catch (error) {
            console.error('Error cargando libros disponibles:', error);
        }
    }

    // ===== MANEJO DE FORMULARIOS =====
    function setupFormHandlers() {
        // Configurar formulario de préstamo
        const formPrestamo = document.getElementById('form-prestamo');
        if (formPrestamo) {
            setupLoanForm(formPrestamo);
        }

        // Configurar formulario de devolución
        const formDevolucion = document.getElementById('form-devolucion');
        if (formDevolucion) {
            setupReturnForm(formDevolucion);
        }

        // Configurar formularios de búsqueda
        const formBusquedaCatalogo = document.getElementById('form-busqueda');
        if (formBusquedaCatalogo) {
            setupCatalogSearch(formBusquedaCatalogo);
        }

        const formBusquedaInicio = document.getElementById('form-busqueda-inicio');
        if (formBusquedaInicio) {
            setupHomeSearch(formBusquedaInicio);
        }
    }

    function setupLoanForm(form) {
        // Autocompletado inteligente para títulos de libros
        const tituloInput = document.getElementById('prestamo-titulo');
        if (tituloInput) {
            tituloInput.addEventListener('input', debounce(async (e) => {
                const query = e.target.value.trim();
                if (query.length >= 2) {
                    await buscarLibrosParaPrestamo(query);
                } else {
                    ocultarSugerencias();
                }
            }, 300));
        }

        // Validación de disponibilidad antes de enviar
        form.addEventListener('submit', async function(e) {
            if (!await validarDisponibilidadPrestamo()) {
                e.preventDefault();
                showNotification('El libro no está disponible para préstamo', 'error');
            }
        });
    }

    function setupReturnForm(form) {
        // Validación de préstamo existente antes de enviar
        form.addEventListener('submit', async function(e) {
            if (!await validarPrestamoExistente()) {
                e.preventDefault();
                showNotification('No se encontró un préstamo activo con esos datos', 'error');
            }
        });
    }

    function setupCatalogSearch(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[type="text"]');
            if (searchInput) {
                realizarBusquedaCatalogo(searchInput.value);
            }
        });

        // Búsqueda en tiempo real
        const searchInput = form.querySelector('input[type="text"]');
        if (searchInput) {
            let timeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    if (e.target.value.length >= 2 || e.target.value.length === 0) {
                        realizarBusquedaCatalogo(e.target.value);
                    }
                }, 500);
            });
        }
    }

    function setupHomeSearch(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[type="text"]');
            if (searchInput && searchInput.value.trim()) {
                window.location.href = `/catalogo?q=${encodeURIComponent(searchInput.value.trim())}`;
            }
        });
    }
    

    // ===== BÚSQUEDA Y FILTROS =====
    function setupSearchInteractions() {
        // Configurar filtros del catálogo
        configurarFiltrosCatalogo();

        // Configurar ordenamiento
        const ordenarSelect = document.getElementById('ordenar-por');
        if (ordenarSelect) {
            ordenarSelect.addEventListener('change', () => {
                realizarBusquedaCatalogo();
            });
        }

        // Configurar limpiar filtros
        const btnLimpiar = document.getElementById('limpiar-filtros');
        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', limpiarFiltros);
        }
    }

    function configurarFiltrosCatalogo() {
        const checkboxes = document.querySelectorAll('.filtro-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // Feedback visual
                checkbox.parentElement.classList.add('bg-blue-50');
                setTimeout(() => {
                    checkbox.parentElement.classList.remove('bg-blue-50');
                }, 300);
                
                realizarBusquedaCatalogo();
            });
        });
    }

    async function realizarBusquedaCatalogo(query = null) {
        const contenedor = document.getElementById('resultados-libros');
        const contador = document.getElementById('contador-resultados');
        const numeroResultados = document.getElementById('numero-resultados');
        
        if (!contenedor) return;

        // Mostrar estado de carga
        mostrarEstadoCarga(contenedor);

        try {
            const parametros = obtenerParametrosBusqueda();
            if (query !== null) {
                parametros.query = query;
            }

            const resultados = await buscarLibrosAPI(parametros);
            mostrarResultadosBusqueda(resultados, contenedor);
            
            // Actualizar contador
            if (contador && numeroResultados) {
                numeroResultados.textContent = resultados.length;
                contador.classList.remove('hidden');
            }
            
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            mostrarErrorBusqueda(contenedor);
        }
    }

    function obtenerParametrosBusqueda() {
        const busquedaInput = document.getElementById('busqueda-input');
        const ordenarSelect = document.getElementById('ordenar-por');
        
        return {
            query: busquedaInput ? busquedaInput.value : '',
            autores: Array.from(document.querySelectorAll('input[name="autor"]:checked')).map(cb => cb.value),
            categorias: Array.from(document.querySelectorAll('input[name="categoria"]:checked')).map(cb => cb.value),
            disponibilidad: Array.from(document.querySelectorAll('input[name="disponibilidad"]:checked')).map(cb => cb.value),
            orden: ordenarSelect ? ordenarSelect.value : 'titulo'
        };
    }

    async function buscarLibrosAPI(parametros) {
        try {
            const response = await fetch('/api/filtrar-libros', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(parametros)
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const result = await response.json();
            
            if (result.estado === 'ok') {
                return result.libros;
            } else {
                throw new Error(result.mensaje);
            }
        } catch (error) {
            console.error('Error en búsqueda API:', error);
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

    function mostrarResultadosBusqueda(libros, contenedor) {
        if (libros.length === 0) {
            contenedor.innerHTML = `
                <div class="col-span-full text-center py-12 text-gray-500">
                    <i data-lucide="search-x" class="w-16 h-16 mx-auto mb-4 text-gray-300"></i>
                    <h3 class="text-xl font-semibold text-gray-400 mb-2">No se encontraron libros</h3>
                    <p class="text-gray-400">Intenta con otros términos de búsqueda o ajusta los filtros</p>
                </div>
            `;
            return;
        }

        contenedor.innerHTML = libros.map(libro => `
            <div class="libro-card focus-visible" 
                 onclick="mostrarDetallesLibro(${libro.id})"
                 tabindex="0"
                 onkeypress="if(event.key === 'Enter') mostrarDetallesLibro(${libro.id})">
                <div class="h-32 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg mb-3 flex items-center justify-center">
                    <i data-lucide="book" class="w-8 h-8 text-blue-500"></i>
                </div>
                <h4 class="font-semibold text-gray-800 text-center mb-2 line-clamp-2">${libro.titulo}</h4>
                <p class="text-sm text-gray-600 text-center mb-3">${libro.autor}</p>
                <div class="flex justify-between items-center">
                    <span class="badge ${libro.disponible ? 'estado-disponible' : 'estado-prestado'}">
                        ${libro.disponible ? 'Disponible' : 'Prestado'}
                    </span>
                    <span class="text-xs text-gray-500">${libro.categoria}</span>
                </div>
            </div>
        `).join('');

        // Actualizar íconos
        lucide.createIcons();
    }

    function mostrarErrorBusqueda(contenedor) {
        contenedor.innerHTML = `
            <div class="col-span-full text-center py-12 text-gray-500">
                <i data-lucide="alert-circle" class="w-16 h-16 mx-auto mb-4 text-red-300"></i>
                <h3 class="text-xl font-semibold text-red-400 mb-2">Error en la búsqueda</h3>
                <p class="text-gray-400">Ocurrió un error al buscar libros. Intenta nuevamente.</p>
                <button onclick="realizarBusquedaCatalogo()" class="btn-primary mt-4">
                    Reintentar
                </button>
            </div>
        `;
        lucide.createIcons();
    }

    function limpiarFiltros() {
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
        const busquedaInput = document.getElementById('busqueda-input');
        if (busquedaInput) {
            busquedaInput.value = '';
        }
        
        realizarBusquedaCatalogo();
    }

    // ===== AUTocompletado PARA PRÉSTAMOS =====
    async function buscarLibrosParaPrestamo(query) {
        const sugerencias = document.getElementById('sugerencias-libros');
        const estadoLibro = document.getElementById('estado-libro');

        if (!sugerencias) return;

        try {
            const response = await fetch(`/api/libros/buscar?q=${encodeURIComponent(query)}`);
            const result = await response.json();
            
            if (result.estado === 'ok' && result.libros.length > 0) {
                mostrarSugerenciasPrestamo(result.libros, sugerencias);
                sugerencias.classList.remove('hidden');
            } else {
                sugerencias.classList.add('hidden');
                if (estadoLibro) {
                    estadoLibro.innerHTML = '<span class="text-red-500">❌ No se encontraron libros con ese título</span>';
                    estadoLibro.classList.remove('hidden');
                }
            }
        } catch (error) {
            console.error('Error buscando libros:', error);
            ocultarSugerencias();
        }
    }

    function mostrarSugerenciasPrestamo(libros, contenedor) {
        contenedor.innerHTML = libros.map(libro => `
            <div class="sugerencia-item libro-sugerencia" 
                 data-titulo="${libro.titulo}" 
                 data-autor="${libro.autor}" 
                 data-disponible="${libro.disponible}">
                <div class="font-medium">${libro.titulo}</div>
                <div class="text-sm text-gray-600">${libro.autor}</div>
                <div class="text-xs ${libro.disponible ? 'text-green-600' : 'text-red-600'}">
                    ${libro.disponible ? '✅ Disponible' : '❌ Prestado'}
                </div>
            </div>
        `).join('');

        // Agregar event listeners a las sugerencias
        document.querySelectorAll('.libro-sugerencia').forEach(element => {
            element.addEventListener('click', function() {
                seleccionarLibroPrestamo(this);
            });
        });
    }

    function seleccionarLibroPrestamo(element) {
        const titulo = element.getAttribute('data-titulo');
        const autor = element.getAttribute('data-autor');
        const disponible = element.getAttribute('data-disponible') === 'true';
        
        const tituloInput = document.getElementById('prestamo-titulo');
        const autorInput = document.getElementById('prestamo-autor');
        const estadoLibro = document.getElementById('estado-libro');
        const btnRegistrar = document.getElementById('btn-registrar-prestamo');
        
        if (tituloInput) tituloInput.value = titulo;
        if (autorInput) autorInput.value = autor;
        
        if (estadoLibro) {
            if (disponible) {
                estadoLibro.innerHTML = '<span class="text-green-600">✅ Libro disponible para préstamo</span>';
                if (btnRegistrar) btnRegistrar.disabled = false;
            } else {
                estadoLibro.innerHTML = '<span class="text-red-600">❌ Libro actualmente prestado</span>';
                if (btnRegistrar) btnRegistrar.disabled = true;
            }
            estadoLibro.classList.remove('hidden');
        }
        
        ocultarSugerencias();
    }

    function ocultarSugerencias() {
        const sugerencias = document.getElementById('sugerencias-libros');
        if (sugerencias) {
            sugerencias.classList.add('hidden');
        }
    }

    // ===== VALIDACIONES =====
    function setupNavigationInteractions() {
        // Prevenir envío doble de formularios
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.classList.add('loading');
                    
                    // Re-enable after 5 seconds (en caso de error)
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.classList.remove('loading');
                    }, 5000);
                }
            });
        });
    }

    function validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        const container = field.parentElement;
        
        // Limpiar estados previos
        container.classList.remove('valid', 'invalid');
        
        // Remover mensajes de validación existentes
        const existingMessage = container.querySelector('.validation-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        if (!value && field.required) {
            showFieldError(field, 'Este campo es obligatorio');
            return;
        }

        // Validaciones específicas
        if (field.type === 'email' && value && !isValidEmail(value)) {
            showFieldError(field, 'Por favor ingresa un email válido');
            return;
        }

        if (field.name === 'numero_estudiante' && value && !/^\d{5,10}$/.test(value)) {
            showFieldError(field, 'El número de estudiante debe tener entre 5 y 10 dígitos');
            return;
        }

        // Si pasa todas las validaciones
        if (value) {
            showFieldSuccess(field);
        }
    }

    function showFieldError(field, message) {
        const container = field.parentElement;
        container.classList.add('invalid');
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'validation-message validation-error';
        errorMessage.textContent = message;
        container.appendChild(errorMessage);
        
        field.classList.add('input-error');
    }

    function showFieldSuccess(field) {
        const container = field.parentElement;
        container.classList.add('valid');
        field.classList.add('input-success');
    }

    function clearValidation(e) {
        const field = e.target;
        const container = field.parentElement;
        
        container.classList.remove('valid', 'invalid');
        field.classList.remove('input-error', 'input-success');
        
        const existingMessage = container.querySelector('.validation-message');
        if (existingMessage) {
            existingMessage.remove();
        }
    }

    async function validarDisponibilidadPrestamo() {
        const tituloInput = document.getElementById('prestamo-titulo');
        const autorInput = document.getElementById('prestamo-autor');
        
        if (!tituloInput || !autorInput) return true;

        const titulo = tituloInput.value.trim();
        const autor = autorInput.value.trim();

        if (!titulo || !autor) return true;

        try {
            const response = await fetch(`/api/libros/buscar?q=${encodeURIComponent(titulo)}`);
            const result = await response.json();
            
            if (result.estado === 'ok') {
                const libro = result.libros.find(l => 
                    l.titulo.toLowerCase() === titulo.toLowerCase() && 
                    l.autor.toLowerCase() === autor.toLowerCase()
                );
                
                return libro && libro.disponible;
            }
        } catch (error) {
            console.error('Error validando disponibilidad:', error);
        }

        return true;
    }

    async function validarPrestamoExistente() {
        const tituloInput = document.getElementById('devolucion-titulo');
        const usuarioInput = document.getElementById('devolucion-usuario');
        
        if (!tituloInput || !usuarioInput) return true;

        const titulo = tituloInput.value.trim();
        const usuario = usuarioInput.value.trim();

        if (!titulo || !usuario) return true;

        // Esta validación sería más compleja en una implementación real
        // Por ahora retornamos true para permitir el envío
        return true;
    }

    // ===== CONFIGURACIÓN DE FORMULARIOS PRINCIPALES =====
    function setupForm(formId, messageId, successMessage, endpoint, validacion = null) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const messageElement = document.getElementById(messageId);

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(form);
                
                // Ejecutar validación personalizada si existe
                if (validacion) {
                    validacion(formData);
                }

                const data = Object.fromEntries(formData);
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.estado === 'ok') {
                    mostrarMensajeExito(messageElement, successMessage);
                    form.reset();
                    prestamoConfirmado = false;
                    
                    // Recargar libros disponibles después de un préstamo/devolución
                    await cargarLibrosDisponibles();
                } else {
                    throw new Error(result.mensaje || 'Error desconocido');
                }
            } catch (error) {
                if (error.message !== 'Esperando confirmación') {
                    mostrarMensajeError(messageElement, error.message);
                }
            }
        });
    }

    // ===== NOTIFICACIONES Y MENSAJES =====
    function mostrarMensajeExito(elemento, mensaje) {
        if (!elemento) return;
        
        elemento.textContent = '✅ ' + mensaje;
        elemento.className = 'mt-4 text-center text-lg font-medium text-green-600 bg-green-100 p-3 rounded-lg fade-in';
        elemento.classList.remove('hidden');
        
        setTimeout(() => {
            elemento.classList.add('hidden');
        }, 5000);
    }

    function mostrarMensajeError(elemento, mensaje) {
        if (!elemento) return;
        
        elemento.textContent = '❌ Error: ' + mensaje;
        elemento.className = 'mt-4 text-center text-lg font-medium text-red-600 bg-red-100 p-3 rounded-lg fade-in';
        elemento.classList.remove('hidden');
        
        setTimeout(() => {
            elemento.classList.add('hidden');
        }, 5000);
    }

    function showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
            type === 'success' ? 'message-success' :
            type === 'error' ? 'message-error' :
            type === 'warning' ? 'message-warning' :
            'bg-blue-500 text-white'
        }`;
        
        const icons = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'alert-triangle',
            info: 'info'
        };

        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <i data-lucide="${icons[type]}" class="w-5 h-5 mr-2"></i>
                    <span class="text-sm">${message}</span>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="ml-4 hover:opacity-70 focus-visible">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        lucide.createIcons();
        
        // Auto-remover después de la duración
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-10px)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }

    // ===== FUNCIONES AUXILIARES =====
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Inicializar Lucide icons periódicamente para elementos dinámicos
    setInterval(() => {
        lucide.createIcons();
    }, 1000);
});

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

