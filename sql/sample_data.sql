-- sample_data.sql
USE warehouse;

INSERT INTO tab_user (username, display_name) VALUES
('admin', 'Administrator'),
('estuar', 'Estuardo');

INSERT INTO tab_warehouse (code, name, location, created_by) VALUES
('MAIN', 'Main Warehouse', 'HQ', 1),
('SAT1', 'Satellite 1', 'Branch A', 1);

INSERT INTO tab_product (sku, name, unit, min_stock, created_by) VALUES
('GAN-001', 'Folder hooks', 'pcs', 50, 1),
('PEN-001', 'Blue pen', 'pcs', 100, 1),
('GLV-001', 'Latex gloves', 'box', 10, 1);

INSERT INTO tab_kit (code, name, description, created_by) VALUES
('KIT-PI', 'Early Childhood', 'Kit for early childhood activities', 1);

INSERT INTO tab_kit_item (kit_id, product_id, quantity) VALUES
(1, 1, 10), -- 10 folder hooks per kit
(1, 2, 5);  -- 5 blue pens per kit

-- Initial stock reception
CALL sp_receive_product(1, 1, 1, 500, NULL, 'Initial stock');
CALL sp_receive_product(1, 2, 1, 200, NULL, 'Initial stock');
CALL sp_receive_product(1, 3, 1, 50,  NULL, 'Initial stock');

-- Issue 2 kits from MAIN warehouse
CALL sp_issue_kit(1, 1, 1, 2, 12345, 'Distribution event');