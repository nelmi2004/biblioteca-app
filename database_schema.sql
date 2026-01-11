-- Crear base de datos
CREATE DATABASE IF NOT EXISTS Biblioteca;
USE Biblioteca;

-- Tabla de categorías
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de carrera
CREATE TABLE carrera (
    id_carrera INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de autores
CREATE TABLE autores (
    id_autor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    nacionalidad VARCHAR(100),
    fecha_nacimiento DATE,
    fecha_fallecimiento DATE,
    biografia TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_autor_nombre (nombre, apellido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de libros (modificada para usar claves foráneas)
CREATE TABLE libros (
    id_libro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    id_autor INT NOT NULL,
    cota VARCHAR(20),
    id_categoria INT NOT NULL,
    id_carrera INT NOT NULL,
    tomo INT,
    ubi VARCHAR(50),
    editorial VARCHAR(100),
    descripcion TEXT,
    cantidad_total INT NOT NULL DEFAULT 1,
    cantidad_disponible INT NOT NULL DEFAULT 1,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_autor) REFERENCES autores(id_autor),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera),
    
    INDEX idx_libros_titulo (titulo),
    INDEX idx_libros_autor (id_autor),
    INDEX idx_libros_categoria (id_categoria),
    INDEX idx_libros_carrera (id_carrera),
    INDEX idx_libros_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    numero_estudiante VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(20),
    carrera VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_usuarios_numero (numero_estudiante)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de préstamos
CREATE TABLE prestamos (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_libro INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_prestamo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_aprobacion TIMESTAMP NULL,
    fecha_limite TIMESTAMP NOT NULL,
    fecha_devolucion TIMESTAMP NULL,
    estado ENUM('activo','pendiente','devuelto', 'vencido','rechazado') DEFAULT 'pendiente',
    observaciones TEXT,
    
    FOREIGN KEY (id_libro) REFERENCES libros(id_libro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    
    INDEX idx_prestamos_estado (estado),
    INDEX idx_prestamos_usuario (id_usuario),
    INDEX idx_prestamos_libro (id_libro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar datos de ejemplo para categorías
INSERT INTO categorias (nombre, descripcion) VALUES
('Literatura', 'Novelas, cuentos, poesía y obras literarias'),
('Ciencia', 'Libros científicos y de divulgación'),
('Historia', 'Libros históricos y biografías'),
('Tecnología', 'Informática, programación, ingeniería'),
('Arte', 'Arte, música, cine, fotografía');

-- Insertar datos de ejemplo para autores
INSERT INTO autores (nombre, apellido, nacionalidad, fecha_nacimiento) VALUES
('Gabriel', 'García Márquez', 'Colombiano', '1927-03-06'),
('Isabel', 'Allende', 'Chilena', '1942-08-02'),
('Mario', 'Vargas Llosa', 'Peruano', '1936-03-28'),
('Stephen', 'Hawking', 'Británico', '1942-01-08'),
('Yuval Noah', 'Harari', 'Israelí', '1976-02-24');

-- Insertar datos de ejemplo para libros
INSERT INTO libros (titulo, id_autor, cota, id_categoria, tomo, editorial, cantidad_total, cantidad_disponible) VALUES
('Cien años', 1, '978-8604947', 1, 1967, 'Sudmericana', 5, 3),
('La casa de los píritus', 2, '978-840080', 1, 1982, 'Pl & Janés', 3, 1),
('La ciudad y lo', 3, '978-846339349', 1, 1963, 'SeBarral', 4, 4),
('Breve historia iempo', 4, '978-84082949', 2, 1988, 'Crítica', 2, 2),
('Sapiens: De animales a dioses', 5, '978-', 3, 2014, 'Deate', 6, 2);

-- Insertar datos de ejemplo para usuarios
INSERT INTO usuarios (nombre, apellido, numero_estudiante, email, telefono, carrera) VALUES
('María', 'González', '2023001', 'maria.gonzalez@email.com', '0412-1234567', 'Ingeniería'),
('Carlos', 'Rodríguez', '2023002', 'carlos.rodriguez@email.com', '0414-7654321', 'Medicina'),
('Ana', 'López', '2023003', 'ana.lopez@email.com', '0424-9876543', 'Derecho');

-- Vista para obtener información completa de libros
CREATE VIEW vista_libros_completa AS
SELECT 
    l.id_libro,
    l.titulo,
    CONCAT(a.nombre, ' ', a.apellido) as autor,
    a.id_autor,
    l.cota,
    c.nombre as categoria,
    c.id_categoria,
    l.tomo,
    l.editorial,
    l.descripcion,
    l.cantidad_total,
    l.cantidad_disponible,
    CASE WHEN l.cantidad_disponible > 0 THEN TRUE ELSE FALSE END as disponible,
    l.activo
FROM libros l
JOIN autores a ON l.id_autor = a.id_autor
JOIN categorias c ON l.id_categoria = c.id_categoria;

-- Procedimiento almacenado para registrar préstamo
DELIMITER //
CREATE PROCEDURE registrar_prestamo(
    IN p_id_libro INT,
    IN p_id_usuario INT,
    IN p_dias_prestamo INT
)
BEGIN
    DECLARE fecha_limite_calc TIMESTAMP;
    
    SET fecha_limite_calc = DATE_ADD(NOW(), INTERVAL p_dias_prestamo DAY);
    
    INSERT INTO prestamos (id_libro, id_usuario, fecha_limite)
    VALUES (p_id_libro, p_id_usuario, fecha_limite_calc);
    
    UPDATE libros 
    SET cantidad_disponible = cantidad_disponible - 1 
    WHERE id_libro = p_id_libro;
END //
DELIMITER ;

-- Procedimiento almacenado para registrar devolución
DELIMITER //
CREATE PROCEDURE registrar_devolucion(
    IN p_id_prestamo INT
)
BEGIN
    DECLARE v_id_libro INT;
    
    SELECT id_libro INTO v_id_libro 
    FROM prestamos 
    WHERE id_prestamo = p_id_prestamo AND estado = 'activo';
    
    IF v_id_libro IS NOT NULL THEN
        UPDATE prestamos 
        SET estado = 'devuelto', fecha_devolucion = NOW() 
        WHERE id_prestamo = p_id_prestamo;
        
        UPDATE libros 
        SET cantidad_disponible = cantidad_disponible + 1 
        WHERE id_libro = v_id_libro;
    END IF;
END //
DELIMITER ;


-- Modificar tabla usuarios existente para incluir autenticación
ALTER TABLE usuarios 
ADD COLUMN username VARCHAR(50) UNIQUE,
ADD COLUMN password_hash VARCHAR(255),
ADD COLUMN es_administrador BOOLEAN DEFAULT FALSE,
ADD COLUMN ultimo_login TIMESTAMP NULL,
ADD COLUMN reset_password_token VARCHAR(100),
ADD COLUMN reset_password_expira TIMESTAMP NULL,
ADD COLUMN bloqueado BOOLEAN DEFAULT FALSE,
ADD COLUMN intentos_login INT DEFAULT 0,
ADD COLUMN fecha_bloqueo TIMESTAMP NULL;

-- Crear tabla de logs de acceso
CREATE TABLE logs_acceso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    tipo_evento ENUM('login_exitoso', 'login_fallido', 'logout', 'cambio_password', 'reset_password'),
    direccion_ip VARCHAR(45),
    user_agent TEXT,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear tabla de sesiones
CREATE TABLE sesiones (
    id_sesion VARCHAR(128) PRIMARY KEY,
    id_usuario INT,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_sesion TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    INDEX idx_sesiones_usuario (id_usuario),
    INDEX idx_sesiones_fecha (fecha_ultima_actividad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Actualizar usuarios existentes (migración)
UPDATE usuarios 
SET username = CONCAT('user', id_usuario), 
    password_hash = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- password: password
    es_administrador = CASE WHEN id_usuario = 1 THEN TRUE ELSE FALSE END;

-- Crear índice para búsqueda por username
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_numero_estudiante ON usuarios(numero_estudiante);