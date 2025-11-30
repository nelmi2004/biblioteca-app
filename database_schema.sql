-- Crear base de datos
CREATE DATABASE Biblioteca;
GO

USE Biblioteca;
GO

-- Tabla de libros
CREATE TABLE libros (
    id_libro INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(255) NOT NULL,
    autor NVARCHAR(255) NOT NULL,
    isbn NVARCHAR(20),
    categoria NVARCHAR(100),
    anio_publicacion INT,
    editorial NVARCHAR(100),
    descripcion TEXT,
    cantidad_total INT NOT NULL DEFAULT 1,
    cantidad_disponible INT NOT NULL DEFAULT 1,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
GO

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    apellido NVARCHAR(100) NOT NULL,
    numero_estudiante NVARCHAR(20) UNIQUE NOT NULL,
    email NVARCHAR(255),
    telefono NVARCHAR(20),
    carrera NVARCHAR(100),
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
GO

-- Tabla de préstamos
CREATE TABLE prestamos (
    id_prestamo INT IDENTITY(1,1) PRIMARY KEY,
    id_libro INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_prestamo DATETIME NOT NULL DEFAULT GETDATE(),
    fecha_limite DATETIME NOT NULL,
    fecha_devolucion DATETIME NULL,
    estado NVARCHAR(20) DEFAULT 'activo', -- activo, devuelto, vencido
    observaciones TEXT,
    FOREIGN KEY (id_libro) REFERENCES libros(id_libro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
GO

-- Insertar datos de ejemplo
INSERT INTO libros (titulo, autor, isbn, categoria, anio_publicacion, editorial, cantidad_total, cantidad_disponible) VALUES
('Cien años de soledad', 'Gabriel Garcia Marquez', '978-8437604947', 'Literatura', 1967, 'Sudamericana', 5, 3),
('La casa de los espíritus', 'Isabel Allende', '978-8401332080', 'Literatura', 1982, 'Plaza & Janés', 3, 1),
('La ciudad y los perros', 'Mario Vargas Llosa', '978-8466339349', 'Literatura', 1963, 'Seix Barral', 4, 4),
('Breve historia del tiempo', 'Stephen Hawking', '978-8408082949', 'Ciencia', 1988, 'Crítica', 2, 2),
('Sapiens: De animales a dioses', 'Yuval Noah Harari', '978-8499926223', 'Historia', 2014, 'Debate', 6, 2);
GO

INSERT INTO usuarios (nombre, apellido, numero_estudiante, email, telefono, carrera) VALUES
('María', 'González', '2023001', 'maria.gonzalez@email.com', '0412-1234567', 'Ingeniería'),
('Carlos', 'Rodríguez', '2023002', 'carlos.rodriguez@email.com', '0414-7654321', 'Medicina'),
('Ana', 'López', '2023003', 'ana.lopez@email.com', '0424-9876543', 'Derecho');
GO

-- Crear índices para mejorar rendimiento
CREATE INDEX IX_libros_titulo ON libros(titulo);
CREATE INDEX IX_libros_autor ON libros(autor);
CREATE INDEX IX_libros_categoria ON libros(categoria);
CREATE INDEX IX_usuarios_numero ON usuarios(numero_estudiante);
CREATE INDEX IX_prestamos_estado ON libros(activo);
GO