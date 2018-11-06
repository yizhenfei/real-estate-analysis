CREATE TABLE community (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(128),
    address VARCHAR(512),
    year_built YEAR,
    building_num INT,
    home_num INT
);
