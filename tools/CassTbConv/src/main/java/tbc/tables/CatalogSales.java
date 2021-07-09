package tbc.tables;

import java.math.BigDecimal;

public class CatalogSales implements Table {
    public String tableName = "Catalog_sales";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Catalog_sales (\n" +
            "        cs_sold_date_sk bigint,\n" +
            "        cs_sold_time_sk bigint,\n" +
            "        cs_ship_date_sk bigint,\n" +
            "        cs_bill_customer_sk bigint,\n" +
            "        cs_bill_cdemo_sk bigint,\n" +
            "        cs_bill_hdemo_sk bigint,\n" +
            "        cs_bill_addr_sk bigint,\n" +
            "        cs_ship_customer_sk bigint,\n" +
            "        cs_ship_cdemo_sk bigint,\n" +
            "        cs_ship_hdemo_sk bigint,\n" +
            "        cs_ship_addr_sk bigint,\n" +
            "        cs_call_center_sk bigint,\n" +
            "        cs_catalog_page_sk bigint,\n" +
            "        cs_ship_mode_sk bigint,\n" +
            "        cs_warehouse_sk bigint,\n" +
            "        cs_item_sk  bigint,\n" +
            "        cs_promo_sk bigint,\n" +
            "        cs_order_number bigint PRIMARY KEY,\n" +
            "        cs_quantity int,\n" +
            "        cs_wholesale_cost decimal,\n" +
            "        cs_list_price decimal,\n" +
            "        cs_sales_price decimal,\n" +
            "        cs_ext_discount_amt decimal,\n" +
            "        cs_ext_sales_price decimal,\n" +
            "        cs_ext_wholesale_cost decimal,\n" +
            "        cs_ext_list_price decimal,\n" +
            "        cs_ext_tax decimal,\n" +
            "        cs_coupon_amt decimal,\n" +
            "        cs_ext_ship_cost decimal,\n" +
            "        cs_net_paid decimal,\n" +
            "        cs_net_paid_inc_tax decimal,\n" +
            "        cs_net_paid_inc_ship decimal,\n" +
            "        cs_net_paid_inc_ship_tax decimal,\n" +
            "        cs_net_profit decimal\n" +
            ")";

    public String stmt = "" +
            "INSERT INTO tpc_ds.catalog_sales(cs_sold_date_sk, cs_sold_time_sk, cs_ship_date_sk, cs_bill_customer_sk, cs_bill_cdemo_sk, cs_bill_hdemo_sk, cs_bill_addr_sk, cs_ship_customer_sk, cs_ship_cdemo_sk, cs_ship_hdemo_sk, cs_ship_addr_sk, cs_call_center_sk, cs_catalog_page_sk, cs_ship_mode_sk, cs_warehouse_sk, cs_item_sk, cs_promo_sk, cs_order_number, cs_quantity , cs_wholesale_cost, cs_list_price, cs_sales_price, cs_ext_discount_amt, cs_ext_sales_price, cs_ext_wholesale_cost, cs_ext_list_price, cs_ext_tax, cs_coupon_amt, cs_ext_ship_cost, cs_net_paid, cs_net_paid_inc_tax, cs_net_paid_inc_ship, cs_net_paid_inc_ship_tax, cs_net_profit) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    @Override
    public Object[] convert(String[] data) {
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
                Long.parseLong(data[17]),
                Integer.parseInt(data[18]),
                BigDecimal.valueOf(Double.parseDouble(data[19])),
                BigDecimal.valueOf(Double.parseDouble(data[20])),
                BigDecimal.valueOf(Double.parseDouble(data[21])),
                BigDecimal.valueOf(Double.parseDouble(data[22])),
                BigDecimal.valueOf(Double.parseDouble(data[23])),
                BigDecimal.valueOf(Double.parseDouble(data[24])),
                BigDecimal.valueOf(Double.parseDouble(data[25])),
                BigDecimal.valueOf(Double.parseDouble(data[26])),
                BigDecimal.valueOf(Double.parseDouble(data[27])),
                BigDecimal.valueOf(Double.parseDouble(data[28])),
                BigDecimal.valueOf(Double.parseDouble(data[29])),
                BigDecimal.valueOf(Double.parseDouble(data[30])),
                BigDecimal.valueOf(Double.parseDouble(data[31])),
                BigDecimal.valueOf(Double.parseDouble(data[32])),
                BigDecimal.valueOf(Double.parseDouble(data[33]))
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
