

ALTER TABLE customer ADD CONSTRAINT fk_customer_1 FOREIGN KEY (c_current_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE customer ADD CONSTRAINT fk_customer_2 FOREIGN KEY (c_first_shipto_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE customer ADD CONSTRAINT fk_customer_3 FOREIGN KEY (c_first_sales_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE customer ADD CONSTRAINT fk_customer_4 FOREIGN KEY (c_last_review_date_sk) REFERENCES date_dim (d_date_sk);


ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_1 FOREIGN KEY (cs_sold_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_2 FOREIGN KEY (cs_ship_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_3 FOREIGN KEY (cs_bill_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_4 FOREIGN KEY (cs_ship_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_5 FOREIGN KEY (cs_ship_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE catalog_sales ADD CONSTRAINT fk_catalog_sales_6 FOREIGN KEY (cs_warehouse_sk) REFERENCES warehouse (w_warehouse_sk);



ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_1 FOREIGN KEY (cr_returned_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_2 FOREIGN KEY (cr_item_sk,cr_order_number) REFERENCES catalog_sales (cs_item_sk,cs_order_number);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_3 FOREIGN KEY (cr_refunded_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_4 FOREIGN KEY (cr_refunded_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_5 FOREIGN KEY (cr_returning_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_6 FOREIGN KEY (cr_returning_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE catalog_returns ADD CONSTRAINT fk_catalog_returns_7 FOREIGN KEY (cr_warehouse_sk) REFERENCES warehouse (w_warehouse_sk);


ALTER TABLE store_sales ADD CONSTRAINT fk_store_sales_1 FOREIGN KEY (ss_sold_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE store_sales ADD CONSTRAINT fk_store_sales_2 FOREIGN KEY (ss_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE store_sales ADD CONSTRAINT fk_store_sales_3 FOREIGN KEY (ss_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE store_sales ADD CONSTRAINT fk_store_sales_4 FOREIGN KEY (ss_addr_sk) REFERENCES customer_address (ca_address_sk);


ALTER TABLE store_returns ADD CONSTRAINT fk_store_returns_1 FOREIGN KEY (sr_returned_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE store_returns ADD CONSTRAINT fk_store_returns_2 FOREIGN KEY (sr_item_sk, sr_ticket_number) REFERENCES store_sales (ss_item_sk, ss_ticket_number);
ALTER TABLE store_returns ADD CONSTRAINT fk_store_returns_3 FOREIGN KEY (sr_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE store_returns ADD CONSTRAINT fk_store_returns_4 FOREIGN KEY (sr_addr_sk) REFERENCES customer_address (ca_address_sk);



ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_1 FOREIGN KEY (ws_sold_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_2 FOREIGN KEY (ws_ship_date_sk) REFERENCES date_dim (d_date_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_3 FOREIGN KEY (ws_bill_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_4 FOREIGN KEY (ws_bill_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_5 FOREIGN KEY (ws_ship_customer_sk) REFERENCES customer (c_customer_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_6 FOREIGN KEY (ws_ship_addr_sk) REFERENCES customer_address (ca_address_sk);
ALTER TABLE web_sales ADD CONSTRAINT fk_store_sales_7 FOREIGN KEY (ws_warehouse_sk) REFERENCES warehouse (w_warehouse_sk);


SELECT create_reference_table('date_dim');
SELECT create_reference_table('warehouse');
SELECT create_reference_table('customer_address');
SELECT create_reference_table('customer');
SELECT create_reference_table('catalog_sales');
SELECT create_reference_table('store_sales');


















