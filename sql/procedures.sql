-- procedures.sql
USE warehouse;

DELIMITER $$

-- Receive products (individual IN)
CREATE PROCEDURE sp_receive_product (
  IN p_user_id INT,
  IN p_product_id INT,
  IN p_warehouse_id INT,
  IN p_quantity INT,
  IN p_plan_req_id INT,
  IN p_note VARCHAR(500)
)
BEGIN
  IF p_quantity <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be > 0 for IN movement';
  END IF;

  INSERT INTO tab_product_transaction
    (product_id, warehouse_id, quantity, movement_type, planification_expense_request_id, kit_id, note, performed_by)
  VALUES
    (p_product_id, p_warehouse_id, p_quantity, 'IN', p_plan_req_id, NULL, p_note, p_user_id);
END$$

-- Issue products (individual OUT)
CREATE PROCEDURE sp_issue_product (
  IN p_user_id INT,
  IN p_product_id INT,
  IN p_warehouse_id INT,
  IN p_quantity INT,
  IN p_plan_req_id INT,
  IN p_note VARCHAR(500)
)
BEGIN
  IF p_quantity <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be > 0 for OUT movement (will be recorded as negative)';
  END IF;

  -- Optional: stock check (prevent negative)
  DECLARE v_on_hand INT DEFAULT 0;
  SELECT COALESCE(SUM(quantity),0) INTO v_on_hand
  FROM tab_product_transaction
  WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;

  IF v_on_hand < p_quantity THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
  END IF;

  INSERT INTO tab_product_transaction
    (product_id, warehouse_id, quantity, movement_type, planification_expense_request_id, kit_id, note, performed_by)
  VALUES
    (p_product_id, p_warehouse_id, -p_quantity, 'OUT', p_plan_req_id, NULL, p_note, p_user_id);
END$$

-- Issue kits (OUT by expanding into product lines)
CREATE PROCEDURE sp_issue_kit (
  IN p_user_id INT,
  IN p_kit_id INT,
  IN p_warehouse_id INT,
  IN p_kit_quantity INT,
  IN p_plan_req_id INT,
  IN p_note VARCHAR(500)
)
BEGIN
  IF p_kit_quantity <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Kit quantity must be > 0';
  END IF;

  -- Stock check for every component
  DECLARE done INT DEFAULT 0;
  DECLARE v_product_id INT;
  DECLARE v_qty_per_kit INT;
  DECLARE cur CURSOR FOR
    SELECT product_id, quantity FROM tab_kit_item WHERE kit_id = p_kit_id;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur;
  stock_check: LOOP
    FETCH cur INTO v_product_id, v_qty_per_kit;
    IF done = 1 THEN
      LEAVE stock_check;
    END IF;

    DECLARE v_needed INT;
    DECLARE v_on_hand INT;
    SET v_needed = v_qty_per_kit * p_kit_quantity;

    SELECT COALESCE(SUM(quantity),0) INTO v_on_hand
    FROM tab_product_transaction
    WHERE product_id = v_product_id AND warehouse_id = p_warehouse_id;

    IF v_on_hand < v_needed THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = CONCAT('Insufficient stock for product_id ', v_product_id);
    END IF;
  END LOOP;
  CLOSE cur;

  -- Perform the OUT transactions for each component
  SET done = 0;
  OPEN cur;
  issue_loop: LOOP
    FETCH cur INTO v_product_id, v_qty_per_kit;
    IF done = 1 THEN
      LEAVE issue_loop;
    END IF;

    INSERT INTO tab_product_transaction
      (product_id, warehouse_id, quantity, movement_type, planification_expense_request_id, kit_id, note, performed_by)
    VALUES
      (v_product_id, p_warehouse_id, -(v_qty_per_kit * p_kit_quantity), 'OUT', p_plan_req_id, p_kit_id, p_note, p_user_id);
  END LOOP;
  CLOSE cur;
END$$

DELIMITER ;