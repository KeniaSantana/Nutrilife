CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(120) UNIQUE,
    password VARCHAR(255),
    genero VARCHAR(50),
    experiencia VARCHAR(100),
    objetivo VARCHAR(100),
    alergias VARCHAR(255),
    intolerancias VARCHAR(255),
    dieta VARCHAR(100),
    no_gusta VARCHAR(255)
);


SELECT * FROM usuarios;

