-- 03_procedures.sql
USE warehouse;

-- Por si ya existían:
DROP FUNCTION IF EXISTS fn_on_hand;
DROP PROCEDURE IF EXISTS sp_place_order;

DELIMITER $$

-- Función simple para conocer stock disponible de un producto
CREATE FUNCTION fn_on_hand(p_product_id INT) RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE v INT DEFAULT 0;
  SELECT COALESCE(quantity, 0) INTO v
    FROM inventory
   WHERE product_id = p_product_id
   LIMIT 1;
  RETURN v;
END $$

-- Ejemplo de procedimiento que valida stock y descuenta inventario
CREATE PROCEDURE sp_place_order(
  IN p_product_id INT,
  IN p_qty INT
)
BEGIN
  DECLARE v_on_hand INT DEFAULT 0;

  -- DECLAREs siempre al inicio del BEGIN (antes de cualquier otra sentencia)
  SELECT COALESCE(quantity, 0)
    INTO v_on_hand
    FROM inventory
   WHERE product_id = p_product_id
   LIMIT 1;

  IF v_on_hand < p_qty THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Not enough stock';
  END IF;

  -- Ejemplos; ajusta a tus tablas reales
  INSERT INTO orders(created_at) VALUES (NOW());
  INSERT INTO order_items(order_id, product_id, quantity)
  VALUES (LAST_INSERT_ID(), p_product_id, p_qty);

  UPDATE inventory
     SET quantity = quantity - p_qty
   WHERE product_id = p_product_id;
END $$

DELIMITER ;
