from database import db

class Libro:
    @staticmethod
    def obtener_todos():
        """Obtener todos los libros"""
        query = """
        SELECT 
            id_libro as id,
            titulo,
            autor,
            isbn,
            categoria,
            anio_publicacion as fecha_publicacion,
            editorial,
            cantidad_total,
            cantidad_disponible,
            CASE WHEN cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros 
        WHERE activo = 1
        ORDER BY titulo
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def buscar(query_text):
        """Buscar libros por título, autor o categoría"""
        query = """
        SELECT 
            id_libro as id,
            titulo,
            autor,
            isbn,
            categoria,
            anio_publicacion as fecha_publicacion,
            editorial,
            cantidad_total,
            cantidad_disponible,
            CASE WHEN cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros 
        WHERE activo = 1 
            AND (titulo LIKE ? OR autor LIKE ? OR categoria LIKE ?)
        ORDER BY titulo
        """
        search_term = f"%{query_text}%"
        return db.execute_query(query, (search_term, search_term, search_term)) or []
    
    @staticmethod
    def obtener_por_id(libro_id):
        """Obtener libro por ID"""
        query = """
        SELECT 
            id_libro as id,
            titulo,
            autor,
            isbn,
            categoria,
            anio_publicacion as fecha_publicacion,
            editorial,
            descripcion,
            cantidad_total,
            cantidad_disponible,
            CASE WHEN cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros 
        WHERE id_libro = ? AND activo = 1
        """
        result = db.execute_query(query, (libro_id,))
        return result[0] if result else None
    
    @staticmethod
    def obtener_disponibles():
        """Obtener libros disponibles"""
        query = """
        SELECT 
            id_libro as id,
            titulo,
            autor,
            isbn,
            categoria,
            anio_publicacion as fecha_publicacion,
            editorial,
            cantidad_total,
            cantidad_disponible,
            CASE WHEN cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros 
        WHERE activo = 1 AND cantidad_disponible > 0
        ORDER BY titulo
        """
        return db.execute_query(query) or []
    
    @staticmethod
    def obtener_destacados(limit=3):
        """Obtener libros destacados (los más prestados)"""
        query = """
        SELECT TOP (?) 
            l.id_libro as id,
            l.titulo,
            l.autor,
            l.isbn,
            l.categoria,
            l.anio_publicacion as fecha_publicacion,
            l.editorial,
            l.cantidad_total,
            l.cantidad_disponible,
            CASE WHEN l.cantidad_disponible > 0 THEN 1 ELSE 0 END as disponible
        FROM libros l
        WHERE l.activo = 1
        ORDER BY l.cantidad_total - l.cantidad_disponible DESC, l.titulo
        """
        return db.execute_query(query, (limit,)) or []

class Usuario:
    @staticmethod
    def obtener_por_numero(numero_estudiante):
        """Obtener usuario por número de estudiante"""
        query = """
        SELECT 
            id_usuario as id,
            nombre,
            apellido,
            numero_estudiante,
            email,
            telefono,
            carrera,
            activo
        FROM usuarios 
        WHERE numero_estudiante = ? AND activo = 1
        """
        result = db.execute_query(query, (numero_estudiante,))
        return result[0] if result else None
    
    @staticmethod
    def crear(nombre, apellido, numero_estudiante, email, telefono, carrera):
        """Crear nuevo usuario"""
        query = """
        INSERT INTO usuarios (nombre, apellido, numero_estudiante, email, telefono, carrera, activo)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        return db.execute_query(query, (nombre, apellido, numero_estudiante, email, telefono, carrera))

class Prestamo:
    @staticmethod
    def crear(id_libro, id_usuario, fecha_limite):
        """Crear nuevo préstamo"""
        query = """
        INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo, fecha_limite, estado)
        VALUES (?, ?, GETDATE(), ?, 'activo')
        """
        result = db.execute_query(query, (id_libro, id_usuario, fecha_limite))
        
        # Actualizar cantidad disponible del libro
        if result:
            update_query = """
            UPDATE libros 
            SET cantidad_disponible = cantidad_disponible - 1 
            WHERE id_libro = ? AND cantidad_disponible > 0
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
            l.autor,
            u.nombre + ' ' + u.apellido as usuario_nombre
        FROM prestamos p
        INNER JOIN libros l ON p.id_libro = l.id_libro
        INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE u.numero_estudiante = ? AND p.estado = 'activo'
        ORDER BY p.fecha_limite
        """
        return db.execute_query(query, (numero_estudiante,)) or []
    
    @staticmethod
    def registrar_devolucion(id_prestamo):
        """Registrar devolución de préstamo"""
        query = """
        UPDATE prestamos 
        SET estado = 'devuelto', fecha_devolucion = GETDATE() 
        WHERE id_prestamo = ? AND estado = 'activo'
        """
        result = db.execute_query(query, (id_prestamo,))
        
        # Actualizar cantidad disponible del libro
        if result:
            update_query = """
            UPDATE libros 
            SET cantidad_disponible = cantidad_disponible + 1 
            WHERE id_libro = (
                SELECT id_libro FROM prestamos WHERE id_prestamo = ?
            )
            """
            db.execute_query(update_query, (id_prestamo,))
        
        return result

class Estadisticas:
    @staticmethod
    def obtener_generales():
        """Obtener estadísticas generales de la biblioteca"""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM libros WHERE activo = 1) as total_libros,
            (SELECT COUNT(*) FROM libros WHERE activo = 1 AND cantidad_disponible > 0) as libros_disponibles,
            (SELECT COUNT(*) FROM prestamos WHERE estado = 'activo') as prestamos_activos,
            (SELECT COUNT(*) FROM usuarios WHERE activo = 1) as total_usuarios
        """
        result = db.execute_query(query)
        return result[0] if result else {
            'total_libros': 0,
            'libros_disponibles': 0,
            'prestamos_activos': 0,
            'total_usuarios': 0
        }