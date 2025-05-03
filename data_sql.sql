-- Create database
CREATE DATABASE IF NOT EXISTS zomato;
USE zomato;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    item_id INT,
    quantity INT NOT NULL,
    delivery_address TEXT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- Insert sample data
INSERT INTO users (username, email, phone) VALUES 
('john_doe', 'john@example.com', '1234567890'),
('jane_smith', 'jane@example.com', '9876543210');

INSERT INTO categories (category_name) VALUES 
('Vegetarian'), 
('Non-Vegetarian'), 
('Vegan');

INSERT INTO items (item_name, description, price, category_id) VALUES 
('Biriyani', 'Fragrant rice dish with spices and meat', 150.00, 2),
('Paneer', 'Indian cottage cheese curry', 100.00, 1),
('Butter Chicken', 'Creamy tomato-based chicken curry', 200.00, 2),
('Dal Tadka', 'Flavorful lentil dish', 80.00, 1),
('Vegan Burger', 'Plant-based burger with veggies', 120.00, 3);

-- Insert some sample orders
INSERT INTO orders (user_id, item_id, quantity, delivery_address) VALUES 
(1, 1, 2, '123 Main Street, Apt 4B, New York'),
(1, 3, 1, '123 Main Street, Apt 4B, New York'),
(2, 2, 3, '456 Oak Avenue, Boston'),
(2, 4, 2, '456 Oak Avenue, Boston');