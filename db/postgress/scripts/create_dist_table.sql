SET citus.shard_replication_factor = 3;

SELECT create_distributed_table('catalog_returns', 'cr_item_sk');

SELECT create_distributed_table('catalog_sales', 'cs_item_sk');

SELECT create_distributed_table('customer', 'c_customer_sk');

SELECT create_distributed_table('date_dim', 'd_date_sk');

SELECT create_distributed_table('store_returns', 'sr_item_sk');

SELECT create_distributed_table('store_sales', 'ss_item_sk');

SELECT create_distributed_table('warehouse', 'w_warehouse_sk');

SELECT create_distributed_table('web_sales', 'ws_item_sk');


