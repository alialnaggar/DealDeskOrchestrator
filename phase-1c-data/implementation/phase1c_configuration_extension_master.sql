-- Isolated supplemental evaluation catalogue. V2 copies retain V1 commercial facts.
-- Load after the shared V1 master, only in the disposable evaluation database.
INSERT INTO products (product_id, product_code, catalog_version, product_name, category, product_type, attributes_json, list_price, standard_cost, billing_model, unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom)
SELECT 'SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001-V2', product_code, 'CATALOGUE_2026_V2', product_name, category, product_type, attributes_json, list_price, standard_cost, billing_model, unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom
FROM products WHERE product_id='SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001' AND catalog_version='CATALOGUE_2026_V1';
INSERT INTO products (product_id, product_code, catalog_version, product_name, category, product_type, attributes_json, list_price, standard_cost, billing_model, unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom)
SELECT 'SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005-V2', product_code, 'CATALOGUE_2026_V2', product_name, category, product_type, attributes_json, list_price, standard_cost, billing_model, unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom
FROM products WHERE product_id='SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005' AND catalog_version='CATALOGUE_2026_V1';
