-- ================================================
-- SCHÉMA DATA WAREHOUSE E-COMMERCE
-- ================================================

-- Supprimer les tables si elles existent déjà
IF OBJECT_ID('fact_orders', 'U') IS NOT NULL DROP TABLE fact_orders;
IF OBJECT_ID('dim_customer', 'U') IS NOT NULL DROP TABLE dim_customer;
IF OBJECT_ID('dim_product', 'U') IS NOT NULL DROP TABLE dim_product;
IF OBJECT_ID('dim_date', 'U') IS NOT NULL DROP TABLE dim_date;
IF OBJECT_ID('dim_country', 'U') IS NOT NULL DROP TABLE dim_country;

-- ================================================
-- 1. DIMENSION : CUSTOMER
-- ================================================
CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    country_name NVARCHAR(100),
    first_purchase_date DATE,
    last_purchase_date DATE,
    total_orders INT,
    total_revenue DECIMAL(18, 2),
    created_at DATETIME DEFAULT GETDATE()
);

-- ================================================
-- 2. DIMENSION : PRODUCT
-- ================================================
CREATE TABLE dim_product (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    stock_code NVARCHAR(50) NOT NULL,
    description NVARCHAR(500),
    avg_price DECIMAL(18, 2),
    total_quantity_sold INT,
    created_at DATETIME DEFAULT GETDATE()
);

-- ================================================
-- 3. DIMENSION : DATE
-- ================================================
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name NVARCHAR(20),
    day INT,
    day_of_week INT,
    day_name NVARCHAR(20),
    is_weekend BIT,
    created_at DATETIME DEFAULT GETDATE()
);

-- ================================================
-- 4. DIMENSION : COUNTRY
-- ================================================
CREATE TABLE dim_country (
    country_id INT IDENTITY(1,1) PRIMARY KEY,
    country_name NVARCHAR(100) NOT NULL UNIQUE,
    total_orders INT,
    total_revenue DECIMAL(18, 2),
    created_at DATETIME DEFAULT GETDATE()
);

-- ================================================
-- 5. FACT : ORDERS
-- ================================================
CREATE TABLE fact_orders (
    order_line_id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_no NVARCHAR(50) NOT NULL,
    date_id INT NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    country_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(18, 2) NOT NULL,
    total_amount DECIMAL(18, 2) NOT NULL,
    invoice_datetime DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    
    -- Foreign Keys
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id)
);

-- ================================================
-- INDEX POUR PERFORMANCE
-- ================================================
CREATE INDEX idx_fact_orders_date ON fact_orders(date_id);
CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_fact_orders_product ON fact_orders(product_id);
CREATE INDEX idx_fact_orders_invoice ON fact_orders(invoice_no);

PRINT 'Schéma créé avec succès !';