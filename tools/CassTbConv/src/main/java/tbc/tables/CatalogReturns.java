package tbc.tables;

import java.math.BigDecimal;

public class CatalogReturns implements Table {
    public String tableName = "Catalog_Returns";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Catalog_returns (\n" +
            "        cr_returned_date_sk bigint,\n" +
            "        cr_returned_time_sk bigint,\n" +
            "        cr_item_sk  bigint,\n" +
            "        cr_refunded_customer_sk bigint,\n" +
            "        cr_refunded_cdemo_sk bigint,\n" +
            "        cr_refunded_hdemo_sk bigint,\n" +
            "        cr_refunded_addr_sk bigint,\n" +
            "        cr_returning_customer_sk bigint,\n" +
            "        cr_returning_cdemo_sk bigint,\n" +
            "        cr_returning_hdemo_sk bigint,\n" +
            "        cr_returning_addr_sk bigint,\n" +
            "        cr_call_center_sk bigint,\n" +
            "        cr_catalog_page_sk  bigint,\n" +
            "        cr_ship_mode_sk  bigint,\n" +
            "        cr_warehouse_sk  bigint,\n" +
            "        cr_reason_sk  bigint,\n" +
            "        cr_order_number bigint PRIMARY KEY,\n" +
            "        cr_return_quantity  int,\n" +
            "        cr_return_amount decimal,\n" +
            "        cr_return_tax decimal,\n" +
            "        cr_return_amt_inc_tax decimal,\n" +
            "        cr_fee decimal,\n" +
            "        cr_return_ship_cost decimal,\n" +
            "        cr_refunded_cash decimal,\n" +
            "        cr_reversed_charge decimal,\n" +
            "        cr_store_credit decimal,\n" +
            "        cr_net_loss decimal\n" +
            ")";


    public String stmt = "" +
            "INSERT INTO tpc_ds.Catalog_returns (cr_returned_date_sk, cr_returned_time_sk, cr_item_sk, cr_refunded_customer_sk, cr_refunded_cdemo_sk, cr_refunded_hdemo_sk, cr_refunded_addr_sk, cr_returning_customer_sk, cr_returning_cdemo_sk, cr_returning_hdemo_sk, cr_returning_addr_sk, cr_call_center_sk, cr_catalog_page_sk, cr_ship_mode_sk, cr_warehouse_sk, cr_reason_sk, cr_order_number, cr_return_quantity, cr_return_amount, cr_return_tax, cr_return_amt_inc_tax, cr_fee, cr_return_ship_cost, cr_refunded_cash, cr_reversed_charge, cr_store_credit, cr_net_loss ) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    @Override
    public Object[] convert(String [] data) {
        return new Object[]{
                Long.parseLong(data[0]),
                Long.parseLong(data[1]),
                Long.parseLong(data[2]),
                Long.parseLong(data[3]),
                Long.parseLong(data[4]),
                Long.parseLong(data[5]),
                Long.parseLong(data[6]),
                Long.parseLong(data[7]),
                Long.parseLong(data[8]),
                Long.parseLong(data[9]),
                Long.parseLong(data[10]),
                Long.parseLong(data[11]),
                Long.parseLong(data[12]),
                Long.parseLong(data[13]),
                Long.parseLong(data[14]),
                Long.parseLong(data[15]),
                Long.parseLong(data[16]),
                Integer.parseInt(data[17]),
                BigDecimal.valueOf(Double.parseDouble(data[18])),
                BigDecimal.valueOf(Double.parseDouble(data[19])),
                BigDecimal.valueOf(Double.parseDouble(data[20])),
                BigDecimal.valueOf(Double.parseDouble(data[21])),
                BigDecimal.valueOf(Double.parseDouble(data[22])),
                BigDecimal.valueOf(Double.parseDouble(data[23])),
                BigDecimal.valueOf(Double.parseDouble(data[24])),
                BigDecimal.valueOf(Double.parseDouble(data[25])),
                BigDecimal.valueOf(Double.parseDouble(data[26])),
        };
    }

    @Override
    public String getTableName() {
        return tableName;
    }

    @Override
    public String getSchema() {
        return schema;
    }

    @Override
    public String getStmt() {
        return stmt;
    }
}
