from database import db
from datetime import datetime, timedelta

class Libro:
    @staticmethod
    def obtener_todos():
        """Obtener todos los libros"""
        query = """
        SELECT 
            l.id_libro as id,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor,
            l.cota,
            c.nombre as categoria,
            c.id_categoria,
            d.nombre as carrera,
            d.id_carrera,
            l.tomo as tomo,
            l.ubi as Ubicacion,
            l.editorial,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        JOIN carrera d ON l.id_carrera = d.id_carrera
        WHERE l.activo = 1 AND a.activo = 1 AND c.activo = 1 AND d.activo = 1
        ORDER BY l.titulo
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def buscar(query_text):
        """Buscar libros por título, autor o categoría"""
        query = """
        SELECT 
            l.id_libro as id,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor,
            l.cota,
            c.nombre as categoria,
            c.id_categoria,
            d.nombre as carrera,
            d.id_carrera,
            l.tomo as tomo,
            l.ubi as Ubicacion,
            l.editorial,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        JOIN carrera d ON l.id_carrera = d.id_carrera
        WHERE l.activo = 1 AND a.activo = 1 AND c.activo = 1 AND d.activo = 1
            AND (l.titulo LIKE %s 
                OR CONCAT(a.nombre, ' ', a.apellido) LIKE %s
                OR a.nombre LIKE %s 
                OR a.apellido LIKE %s
                OR c.nombre LIKE %s)
        ORDER BY l.titulo
        """
        search_term = f"%{query_text}%"
        return db.execute_query(query, (search_term, search_term, search_term, search_term, search_term)) or []
    
    @staticmethod
    def obtener_por_id(libro_id):
        """Obtener libro por ID"""
        query = """
        SELECT 
            l.id_libro as id,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor,
            l.cota,
            c.nombre as categoria,
            c.id_categoria,
            d.nombre as carrera,
            d.id_carrera,
            l.tomo as tomo,
            l.ubi as Ubicacion,
            l.editorial,
            l.descripcion,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        JOIN carrera d ON l.id_carrera = d.id_carrera
        WHERE l.id_libro = %s AND l.activo = 1 AND a.activo = 1 AND c.activo = 1 AND d.activo = 1
        """
        result = db.execute_query(query, (libro_id,))
        return result[0] if result else None
    
    @staticmethod
    def obtener_disponibles():
        """Obtener libros disponibles"""
        query = """
        SELECT 
            l.id_libro as id,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor,
            l.cota,
            c.nombre as categoria,
            c.id_categoria,
            d.nombre as carrera,
            d.id_carrera,
            l.tomo as tomo,
            l.ubi as Ubicacion,
            l.editorial,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        JOIN carrera d ON l.id_carrera = d.id_carrera
        WHERE l.activo = 1 AND a.activo = 1 AND c.activo = 1 AND d.activo = 1 
            AND l.cantidad_disponible > 0
        ORDER BY l.titulo
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def obtener_destacados(limit=3):
        """Obtener libros destacados (los más prestados)"""
        query = """
        SELECT 
            l.id_libro as id,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor,
            l.cota,
            c.nombre as categoria,
            c.id_categoria,
            d.nombre as carrera,
            d.id_carrera,
            l.tomo as tomo,
            l.ubi as Ubicacion,
            l.editorial,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible,
            (SELECT COUNT(*) FROM prestamos p WHERE p.id_libro = l.id_libro AND p.estado = 'devuelto') as veces_prestado
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        JOIN carrera d ON l.id_carrera = d.id_carrera
        WHERE l.activo = 1 AND a.activo = 1 AND c.activo = 1 AND d.activo = 1
        ORDER BY veces_prestado DESC, l.titulo
        LIMIT %s
        """
        return db.execute_query(query, (limit,)) or []
    
    @staticmethod
    def obtener_autores_unicos():
        """Obtener lista de autores únicos para filtros"""
        query = """
        SELECT DISTINCT 
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            a.id_autor
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        WHERE l.activo = 1 AND a.activo = 1
        ORDER BY autor
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def obtener_categorias_unicas():
        """Obtener lista de categorías únicas para filtros"""
        query = """
        SELECT DISTINCT 
            c.nombre as categoria,
            c.id_categoria
        FROM libros l
        JOIN categorias c ON l.id_categoria = c.id_categoria
        WHERE l.activo = 1 AND c.activo = 1
        ORDER BY categoria
        """
        return db.execute_query(query) or []

class Autor:
    @staticmethod
    def obtener_todos():
        """Obtener todos los autores"""
        query = """
        SELECT 
            id_autor as id,
            CONCAT(nombre, ' ', apellido) as nombre_completo,
            nombre,
            apellido,
            nacionalidad,
            fecha_nacimiento,
            fecha_fallecimiento,
            biografia
        FROM autores
        WHERE activo = 1
        ORDER BY apellido, nombre
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def obtener_por_id(autor_id):
        """Obtener autor por ID"""
        query = """
        SELECT 
            id_autor as id,
            CONCAT(nombre, ' ', apellido) as nombre_completo,
            nombre,
            apellido,
            nacionalidad,
            fecha_nacimiento,
            fecha_fallecimiento,
            biografia
        FROM autores
        WHERE id_autor = %s AND activo = 1
        """
        result = db.execute_query(query, (autor_id,))
        return result[0] if result else None

class Categoria:
    @staticmethod
    def obtener_todas():
        """Obtener todas las categorías"""
        query = """
        SELECT 
            id_categoria as id,
            nombre,
            descripcion
        FROM categorias
        WHERE activo = 1
        ORDER BY nombre
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def obtener_por_id(categoria_id):
        """Obtener categoría por ID"""
        query = """
        SELECT 
            id_categoria as id,
            nombre,
            descripcion
        FROM categorias
        WHERE id_categoria = %s AND activo = 1
        """
        result = db.execute_query(query, (categoria_id,))
        return result[0] if result else None

class Usuario:
    @staticmethod
    def obtener_por_numero(numero_estudiante):
        """Obtener usuario por número de estudiante"""
        query = """
        SELECT 
            id_usuario as id,
            CONCAT(nombre, ' ', apellido) as nombre_completo,
            nombre,
            apellido,
            numero_estudiante,
            email,
            telefono,
            carrera,
            activo
        FROM usuarios 
        WHERE numero_estudiante = %s AND activo = 1
        """
        result = db.execute_query(query, (numero_estudiante,))
        return result[0] if result else None
    
    @staticmethod
    def crear(nombre, apellido, numero_estudiante, email, telefono, carrera):
        """Crear nuevo usuario"""
        query = """
        INSERT INTO usuarios (nombre, apellido, numero_estudiante, email, telefono, carrera, activo)
        VALUES (%s, %s, %s, %s, %s, %s, 1)
        """
        return db.execute_query(query, (nombre, apellido, numero_estudiante, email, telefono, carrera))
    
    @staticmethod
    def buscar_por_nombre_o_numero(query_text):
        """Buscar usuarios por nombre o número"""
        query = """
        SELECT 
            id_usuario as id,
            CONCAT(nombre, ' ', apellido) as nombre_completo,
            nombre,
            apellido,
            numero_estudiante,
            email,
            telefono,
            carrera
        FROM usuarios
        WHERE activo = 1 
            AND (CONCAT(nombre, ' ', apellido) LIKE %s 
                OR numero_estudiante LIKE %s
                OR nombre LIKE %s 
                OR apellido LIKE %s)
        ORDER BY nombre, apellido
        LIMIT 10
        """
        search_term = f"%{query_text}%"
        return db.execute_query(query, (search_term, search_term, search_term, search_term)) or []

class Prestamo:
    @staticmethod
    def crear(id_libro, id_usuario, fecha_limite):
        """Crear nuevo préstamo"""
        query = """
        INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo, fecha_limite, estado)
        VALUES (%s, %s, NOW(), %s, 'pendiente')
        """
        result = db.execute_query(query, (id_libro, id_usuario, fecha_limite))
        
        # Actualizar cantidad disponible del libro
        if result:
            update_query = """
            UPDATE libros 
            SET cantidad_disponible = cantidad_disponible - 1 
            WHERE id_libro = %s AND cantidad_disponible > 0
            """
            db.execute_query(update_query, (id_libro,))
        
        return result
    
    @staticmethod
    def obtener_activos_por_usuario(numero_estudiante):
        """Obtener préstamos activos por número de estudiante"""
        query = """
        SELECT 
            p.id_prestamo as id,
            p.fecha_prestamo,
            p.fecha_limite,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            CONCAT(u.nombre, ' ', u.apellido) as usuario_nombre
        FROM prestamos p
        INNER JOIN libros l ON p.id_libro = l.id_libro
        INNER JOIN autores a ON l.id_autor = a.id_autor
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE u.numero_estudiante = %s AND p.estado = 'activo'
        ORDER BY p.fecha_limite
        """
        return db.execute_query(query, (numero_estudiante,)) or []
    
    @staticmethod
    def obtener_prestamo_activo(titulo, numero_estudiante):
        """Obtener préstamo activo específico por título y usuario"""
        query = """
        SELECT 
            p.id_prestamo as id,
            p.fecha_prestamo,
            p.fecha_limite,
            l.titulo,
            CONCAT(a.nombre, ' ', a.apellido) as autor,
            CONCAT(u.nombre, ' ', u.apellido) as usuario_nombre,
            u.numero_estudiante
        FROM prestamos p
        INNER JOIN libros l ON p.id_libro = l.id_libro
        INNER JOIN autores a ON l.id_autor = a.id_autor
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE u.numero_estudiante = %s 
            AND l.titulo LIKE %s
            AND p.estado = 'activo'
        LIMIT 1
        """
        search_term = f"%{titulo}%"
        result = db.execute_query(query, (numero_estudiante, search_term))
        return result[0] if result else None
    
    @staticmethod
    def registrar_devolucion(id_prestamo):
        """Registrar devolución de préstamo"""
        query = """
        UPDATE prestamos 
        SET estado = 'devuelto', fecha_devolucion = NOW() 
        WHERE id_prestamo = %s AND estado = 'activo'
        """
        result = db.execute_query(query, (id_prestamo,))
        
        # Actualizar cantidad disponible del libro
        if result:
            update_query = """
            UPDATE libros 
            SET cantidad_disponible = cantidad_disponible + 1 
            WHERE id_libro = (
                SELECT id_libro FROM prestamos WHERE id_prestamo = %s
            )
            """
            db.execute_query(update_query, (id_prestamo,))
        
        return result
    
    @staticmethod
    def obtener_prestamo_pendientes(buscar, filtro_estado, filtro_fecha, fecha_desde, fecha_hasta,auth_usuario):
        """Obtener todos los préstamos pendientes"""
        query = """
        SELECT 
            p.id_prestamo as id,
            p.id_prestamo as codigo_prestamo,
            p.estado,
            p.fecha_prestamo,
            p.fecha_aprobacion,
            p.fecha_limite,
            p.fecha_devolucion as fecha_devuelto,
            p.observaciones,

            u.id_usuario,
            CONCAT(u.nombre, ' ', u.apellido) as estudiante_nombre,
            u.numero_estudiante as estudiante_numero,
            u.email as estudiante_email,
            u.carrera as estudiante_carrera,
            u.telefono as estudiante_telefono,

            l.id_libro as libro_id,
            l.titulo as libro_titulo,
            CONCAT(a.nombre, ' ', a.apellido) as libro_autor,
            i.nombre as libro_categoria,
            l.cota as libro_cota,
            t.nombre as libro_carrera,
            CASE 
               WHEN l.cantidad_total = l.cantidad_disponible THEN false
               ELSE true
            END AS libro_disponible




        FROM prestamos p
        INNER JOIN libros l ON p.id_libro = l.id_libro
        INNER JOIN autores a ON l.id_autor = a.id_autor
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        INNER JOIN categorias i ON l.id_categoria = i.id_categoria
        INNER JOIN carrera t ON l.id_carrera = t.id_carrera
        WHERE 1=1


        """
        params = []

        # Filtrar por estado
        if filtro_estado:
            query += " AND p.estado = %s"
            params.append(filtro_estado)
        else:
            query += " AND p.estado IN ('pendiente', 'aprobado', 'activo', 'devuelto', 'rechazado')"
        
        # Filtrar por búsqueda
        if buscar:
            query += """
                AND (
                    u.nombre LIKE %s OR 
                    u.numero_estudiante LIKE %s OR 
                    l.titulo LIKE %s OR 
                    CONCAT(a.nombre, ' ', a.apellido) LIKE %s OR
                    p.id_prestamo LIKE %s
                )
            """
            search_term = f"%{buscar}%"
            params.extend([search_term, search_term, search_term, search_term, search_term])
        
        # Filtrar por fecha
        if filtro_fecha and filtro_fecha != 'personalizado':
            hoy = datetime.now().date()
            if filtro_fecha == 'hoy':
                query += " AND DATE(p.fecha_prestamo) = %s"
                params.append(hoy)
            elif filtro_fecha == 'semana':
                semana_pasada = hoy - timedelta(days=7)
                query += " AND DATE(p.fecha_prestamo) >= %s"
                params.append(semana_pasada)
            elif filtro_fecha == 'mes':
                mes_pasado = hoy - timedelta(days=30)
                query += " AND DATE(p.fecha_prestamo) >= %s"
                params.append(mes_pasado)
        
        # Filtrar por fechas personalizadas
        if filtro_fecha == 'personalizado':
            if fecha_desde:
                query += " AND DATE(p.fecha_prestamo) >= %s"
                params.append(fecha_desde)
            if fecha_hasta:
                query += " AND DATE(p.fecha_prestamo) <= %s"
                params.append(fecha_hasta)
        
        # Filtrar por usuario si no es administrador
        if auth_usuario['es_administrador'] == 0:
            query += " AND u.id_usuario = %s"
            params.append(auth_usuario['id_usuario'])

        #Ordenar por fecha de solicitud (más reciente primero)
        query += " ORDER BY p.fecha_prestamo DESC"

        return db.execute_query(query, params) or []
    
    @staticmethod
    def obtener_prestamo_id(id_prestamo):
        """Obtener préstamos por ID"""
        query = """
        SELECT 
            p.id_prestamo as id,
            p.id_prestamo as codigo_prestamo,
            p.estado,
            p.fecha_prestamo,
            p.fecha_aprobacion,
            p.fecha_limite,
            p.fecha_devolucion AS fecha_devuelto,
            p.observaciones,

            u.id_usuario,
            CONCAT(u.nombre, ' ', u.apellido) as estudiante_nombre,
            u.numero_estudiante as estudiante_numero,
            u.email as estudiante_email,
            u.carrera as estudiante_carrera,
            u.telefono as estudiante_telefono,

            l.id_libro as libro_id,
            l.titulo as libro_titulo,
            CONCAT(a.nombre, ' ', a.apellido) as libro_autor,
            i.nombre as libro_categoria,
            l.cota as libro_cota,
            t.nombre as libro_carrera,
                CASE WHEN l.cantidad_total = l.cantidad_disponible THEN FALSE ELSE TRUE
            END AS libro_disponible






        FROM prestamos p
        INNER JOIN libros l ON p.id_libro = l.id_libro
        INNER JOIN autores a ON l.id_autor = a.id_autor
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        INNER JOIN categorias i ON l.id_categoria = i.id_categoria
        INNER JOIN carrera t ON l.id_carrera = t.id_carrera
        WHERE p.id_prestamo = %s
        ORDER BY p.fecha_prestamo DESC


        """
        return db.execute_query(query, (id_prestamo,))
    
    @staticmethod
    def aprobar_prestamos(id_prestamo,id_prestamos,fecha_limite,observaciones):
        if id_prestamo:
           """Aprobar préstamo"""
           query = """
           UPDATE prestamos 
           SET estado = 'activo', fecha_aprobacion = NOW(), fecha_limite = %s, observaciones = %s
           WHERE id_prestamo = %s AND estado = 'pendiente'
           """
           return db.execute_query(query, (fecha_limite,observaciones, id_prestamo))
        
        elif id_prestamos and len(id_prestamos) > 0:
            #Actualizar múltiples préstamos
             placeholders = ', '.join(['%s'] * len(id_prestamos))
             print(placeholders)
             query = f"""
                 UPDATE prestamos 
                 SET estado = 'activo',
                     fecha_aprobacion = NOW(),
                     fecha_limite = %s,
                     observaciones = CONCAT(COALESCE(observaciones, ''), '\nAprobado masivamente: ', %s)
                 WHERE id_prestamo IN ({placeholders}) AND estado = 'pendiente'
            # """
             params = [fecha_limite, observaciones] + id_prestamos
             return db.execute_query(query, params)
    @staticmethod
    def rechazar_prestamos(id_prestamo,id_prestamos,motivo,observaciones):  
        # Procesar rechazo individual
        if id_prestamo:
            query = """
                UPDATE prestamos 
                SET estado = 'rechazado',
                    observaciones = CONCAT(COALESCE(observaciones, ''), '\nRechazado: ', %s, ' - ', %s)
                WHERE id_prestamo = %s AND estado = 'pendiente'
            """

            result=db.execute_query(query, (motivo, observaciones, id_prestamo))
            if result:
                update_query = """
                    UPDATE libros 
                    SET cantidad_disponible = cantidad_disponible + 1 
                    WHERE id_libro = (
                        SELECT id_libro FROM prestamos WHERE id_prestamo = %s
                    )
                    """
                db.execute_query(update_query, (id_prestamo,))      
        
        # Procesar rechazo masivo
        elif id_prestamos and len(id_prestamos) > 0:
            placeholders = ', '.join(['%s'] * len(id_prestamos))
            query = f"""
                UPDATE prestamos 
                SET estado = 'rechazado',
                    observaciones = CONCAT(COALESCE(observaciones, ''), '\nRechazado masivamente: ', %s, ' - ', %s)
                WHERE id_prestamo IN ({placeholders}) AND estado = 'pendiente'
            """
            params = [motivo, observaciones] + id_prestamos
            result = db.execute_query(query, params)
                # Actualizar cantidad disponible del libro
            if result:
                for id in id_prestamos:
                    update_query = """
                        UPDATE libros 
                        SET cantidad_disponible = cantidad_disponible + 1 
                        WHERE id_libro IN (
                            SELECT id_libro FROM prestamos WHERE id_prestamo = %s
                        )
                        """
                    db.execute_query(update_query, id)
                    print("Actualizado libro para préstamo ID:", i)



            



        

    

class Estadisticas:
    @staticmethod
    def obtener_generales():
        """Obtener estadísticas generales de la biblioteca"""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM libros WHERE activo = 1) as total_libros,
            (SELECT COUNT(*) FROM libros WHERE activo = 1 AND cantidad_disponible > 0) as libros_disponibles,
            (SELECT COUNT(*) FROM prestamos WHERE estado = 'activo') as prestamos_activos,
            (SELECT COUNT(*) FROM usuarios WHERE activo = 1) as total_usuarios,
            (SELECT COUNT(*) FROM autores WHERE activo = 1) as total_autores,
            (SELECT COUNT(*) FROM categorias WHERE activo = 1) as total_categorias
        """
        result = db.execute_query(query)
        return result[0] if result else {
            'total_libros': 0,
            'libros_disponibles': 0,
            'prestamos_activos': 0,
            'total_usuarios': 0,
            'total_autores': 0,
            'total_categorias': 0
        }