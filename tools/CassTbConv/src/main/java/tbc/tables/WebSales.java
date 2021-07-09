package tbc.tables;

import java.math.BigDecimal;

public class WebSales implements Table {
    public String tableName = "Web_sales";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Web_sales  (\n" +
            "        ws_sold_date_sk bigint,\n" +
            "        ws_sold_time_sk bigint,\n" +
            "        ws_ship_date_sk bigint,\n" +
            "        ws_item_sk  bigint,\n" +
            "        ws_bill_customer_sk bigint,\n" +
            "        ws_bill_cdemo_sk bigint,\n" +
            "        ws_bill_hdemo_sk bigint,\n" +
            "        ws_bill_addr_sk bigint,\n" +
            "        ws_ship_customer_sk bigint,\n" +
            "        ws_ship_cdemo_sk bigint,\n" +
            "        ws_ship_hdemo_sk bigint,\n" +
            "        ws_ship_addr_sk bigint,\n" +
            "        ws_web_page_sk bigint,\n" +
            "        ws_web_site_sk bigint,\n" +
            "        ws_ship_mode_sk bigint,\n" +
            "        ws_warehouse_sk bigint,\n" +
            "        ws_promo_sk bigint,\n" +
            "        ws_order_number  bigint PRIMARY KEY,\n" +
            "        ws_quantity int,\n" +
            "        ws_wholesale_cost decimal,\n" +
            "        ws_list_price decimal,\n" +
            "        ws_sales_price decimal,\n" +
            "        ws_ext_discount_amt decimal,\n" +
            "        ws_ext_sales_price decimal,\n" +
            "        ws_ext_wholesale_cost decimal,\n" +
            "        ws_ext_list_price decimal,\n" +
            "        ws_ext_tax decimal,\n" +
            "        ws_coupon_amt decimal,\n" +
            "        ws_ext_ship_cost decimal,\n" +
            "        ws_net_paid decimal,\n" +
            "        ws_net_paid_inc_tax decimal,\n" +
            "        ws_net_paid_inc_ship decimal,\n" +
            "        ws_net_paid_inc_ship_tax decimal,\n" +
            "        ws_net_profit decimal\n" +
            ")";

    public String stmt = "" +
            "INSERT INTO tpc_ds.web_sales(ws_sold_date_sk, ws_sold_time_sk, ws_ship_date_sk, ws_item_sk, ws_bill_customer_sk, ws_bill_cdemo_sk, ws_bill_hdemo_sk, ws_bill_addr_sk, ws_ship_customer_sk, ws_ship_cdemo_sk, ws_ship_hdemo_sk, ws_ship_addr_sk, ws_web_page_sk, ws_web_site_sk, ws_ship_mode_sk, ws_warehouse_sk, ws_promo_sk, ws_order_number, ws_quantity, ws_wholesale_cost, ws_list_price, ws_sales_price, ws_ext_discount_amt, ws_ext_sales_price, ws_ext_wholesale_cost, ws_ext_list_price, ws_ext_tax, ws_coupon_amt, ws_ext_ship_cost, ws_net_paid, ws_net_paid_inc_tax, ws_net_paid_inc_ship, ws_net_paid_inc_ship_tax, ws_net_profit ) " +
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
