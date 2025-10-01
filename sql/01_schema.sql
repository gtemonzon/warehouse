CREATE TABLE IF NOT EXISTS tab_products (
  id_product INT AUTO_INCREMENT PRIMARY KEY,
  id_product_type INT NULL,
  id_unit_measurement INT NULL,
  code INT NULL,
  cname VARCHAR(255) NULL,
  description LONGTEXT NULL,
  photo LONGBLOB NULL,
  unit_cost DOUBLE NULL,
  add_user INT NULL,
  add_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mod_user INT NULL,
  mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_products_code (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tab_warehouse (
  id_warehouse INT AUTO_INCREMENT PRIMARY KEY,
  code INT NULL,
  cname VARCHAR(255) NULL,
  description LONGTEXT NULL,
  add_user INT NULL,
  add_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mod_user INT NULL,
  mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_wh_code (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tab_kit (
  id_kit INT AUTO_INCREMENT PRIMARY KEY,
  code INT NULL,
  cname VARCHAR(255) NULL,
  description LONGTEXT NULL,
  photo LONGBLOB NULL,
  add_user INT NULL,
  add_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mod_user INT NULL,
  mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_kit_code (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tab_kit_composition (
  id_kit_composition INT AUTO_INCREMENT PRIMARY KEY,
  id_kit INT NOT NULL,
  id_product INT NOT NULL,
  quantaty INT NULL,
  add_user INT NULL,
  add_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mod_user INT NULL,
  mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_kc_kit (id_kit),
  KEY idx_kc_product (id_product),
  CONSTRAINT fk_kc_kit FOREIGN KEY (id_kit) REFERENCES tab_kit(id_kit)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_kc_product FOREIGN KEY (id_product) REFERENCES tab_products(id_product)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tab_product_transaction (
  id_product_transaction INT AUTO_INCREMENT PRIMARY KEY,
  id_product INT NOT NULL,
  id_warehouse INT NOT NULL,
  type_transaction TINYINT NOT NULL, -- 1=IN, 2=OUT
  id_planification_expense_request INT NULL,
  id_kit INT NULL,
  quantaty_kit INT NULL,
  quantaty_products INT NULL,
  description LONGTEXT NULL,
  expiration_date DATE NULL,
  add_user INT NULL,
  add_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mod_user INT NULL,
  mod_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_tr_product (id_product),
  KEY idx_tr_warehouse (id_warehouse),
  KEY idx_tr_type (type_transaction),
  CONSTRAINT fk_tr_product FOREIGN KEY (id_product) REFERENCES tab_products(id_product)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_tr_warehouse FOREIGN KEY (id_warehouse) REFERENCES tab_warehouse(id_warehouse)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Vista de stock por producto y almacén (para tus consultas on_hand)
CREATE OR REPLACE VIEW vw_inventory AS
SELECT
  t.id_product,
  t.id_warehouse,
  SUM(CASE WHEN t.type_transaction=1 THEN COALESCE(t.quantaty_products,0)
           WHEN t.type_transaction=2 THEN -COALESCE(t.quantaty_products,0)
           ELSE 0 END) AS on_hand
FROM tab_product_transaction t
GROUP BY t.id_product, t.id_warehouse;
