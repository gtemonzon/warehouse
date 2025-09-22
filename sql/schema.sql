-- schema.sql
-- MySQL 8 schema for Warehouse module

CREATE DATABASE IF NOT EXISTS warehouse CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE warehouse;

-- Users (simple selection-based auth for this module)
CREATE TABLE IF NOT EXISTS tab_user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  display_name VARCHAR(150) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Warehouses
CREATE TABLE IF NOT EXISTS tab_warehouse (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(150) NOT NULL,
  location VARCHAR(255) NULL,
  photo LONGBLOB NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_warehouse_user FOREIGN KEY (created_by) REFERENCES tab_user(id)
);

-- Products
CREATE TABLE IF NOT EXISTS tab_product (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  unit VARCHAR(50) NOT NULL, -- e.g., 'pcs', 'box', 'kg'
  min_stock INT NOT NULL DEFAULT 0,
  photo LONGBLOB NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_user FOREIGN KEY (created_by) REFERENCES tab_user(id)
);

-- Kits
CREATE TABLE IF NOT EXISTS tab_kit (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(100) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  photo LONGBLOB NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_kit_user FOREIGN KEY (created_by) REFERENCES tab_user(id)
);

-- Kit items (composition of kits)
CREATE TABLE IF NOT EXISTS tab_kit_item (
  id INT AUTO_INCREMENT PRIMARY KEY,
  kit_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  UNIQUE KEY uq_kit_product (kit_id, product_id),
  CONSTRAINT fk_kit_item_kit FOREIGN KEY (kit_id) REFERENCES tab_kit(id) ON DELETE CASCADE,
  CONSTRAINT fk_kit_item_product FOREIGN KEY (product_id) REFERENCES tab_product(id)
);

-- Polymorphic documents (attachments), supports multiple PDFs or files per record
CREATE TABLE IF NOT EXISTS tab_document (
  id INT AUTO_INCREMENT PRIMARY KEY,
  target_table VARCHAR(64) NOT NULL, -- e.g., 'tab_product', 'tab_product_transaction', etc.
  target_id INT NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  mime_type VARCHAR(100) NOT NULL,
  file_data LONGBLOB NOT NULL, -- store bytes; swap to external storage if desired
  uploaded_by INT NOT NULL,
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_document_target (target_table, target_id),
  CONSTRAINT fk_document_user FOREIGN KEY (uploaded_by) REFERENCES tab_user(id)
);

-- Product transactions (stock ledger)
-- quantity is signed: positive for IN, negative for OUT
CREATE TABLE IF NOT EXISTS tab_product_transaction (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  warehouse_id INT NOT NULL,
  quantity INT NOT NULL,
  movement_type ENUM('IN','OUT') NOT NULL,
  planification_expense_request_id INT NULL,
  kit_id INT NULL, -- if generated from a kit issue
  note VARCHAR(500) NULL,
  performed_by INT NOT NULL,
  performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_qty_sign CHECK (
    (movement_type = 'IN' AND quantity > 0) OR
    (movement_type = 'OUT' AND quantity < 0)
  ),
  CONSTRAINT fk_tx_product FOREIGN KEY (product_id) REFERENCES tab_product(id),
  CONSTRAINT fk_tx_warehouse FOREIGN KEY (warehouse_id) REFERENCES tab_warehouse(id),
  CONSTRAINT fk_tx_kit FOREIGN KEY (kit_id) REFERENCES tab_kit(id),
  CONSTRAINT fk_tx_user FOREIGN KEY (performed_by) REFERENCES tab_user(id)
);

-- Current stock per product and warehouse
CREATE OR REPLACE VIEW vw_current_stock AS
SELECT
  t.product_id,
  t.warehouse_id,
  SUM(t.quantity) AS qty_on_hand
FROM tab_product_transaction t
GROUP BY t.product_id, t.warehouse_id;

-- Convenience view for product ledger (latest first)
CREATE OR REPLACE VIEW vw_product_ledger AS
SELECT
  t.id,
  t.product_id,
  p.name AS product_name,
  t.warehouse_id,
  w.name AS warehouse_name,
  t.quantity,
  t.movement_type,
  t.planification_expense_request_id,
  t.kit_id,
  t.note,
  t.performed_by,
  u.display_name AS performed_by_name,
  t.performed_at
FROM tab_product_transaction t
JOIN tab_product p ON p.id = t.product_id
JOIN tab_warehouse w ON w.id = t.warehouse_id
JOIN tab_user u ON u.id = t.performed_by
ORDER BY t.performed_at DESC, t.id DESC;