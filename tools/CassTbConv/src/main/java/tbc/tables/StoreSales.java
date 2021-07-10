package tbc.tables;

import java.math.BigDecimal;


public class StoreSales  implements Table{
    public String tableName = "store_sales";
    public  String schema = "" +
            "CREATE TABLE tpc_ds.Store_sales (\n" +
            "        ss_sold_date_sk bigint,\n" +
            "        ss_sold_time_sk bigint,\n" +
            "        ss_item_sk bigint,\n" +
            "        ss_customer_sk bigint,\n" +
            "        ss_cdemo_sk bigint,\n" +
            "        ss_hdemo_sk bigint,\n" +
            "        ss_addr_sk bigint,\n" +
            "        ss_store_sk bigint,\n" +
            "        ss_promo_sk bigint,\n" +
            "        ss_ticket_number bigint PRIMARY KEY,\n" +
            "        ss_quantity int,\n" +
            "        ss_wholesale_cost decimal,\n" +
            "        ss_list_price decimal,\n" +
            "        ss_sales_price decimal,\n" +
            "        ss_ext_discount_amt decimal,\n" +
            "        ss_ext_sales_price decimal,\n" +
            "        ss_ext_wholesale_cost decimal,\n" +
            "        ss_ext_list_price decimal,\n" +
            "        ss_ext_tax decimal,\n" +
            "        ss_coupon_amt decimal,\n" +
            "        ss_net_paid decimal,\n" +
            "        ss_net_paid_inc_tax decimal,\n" +
            "        ss_net_profit decimal\n" +
            ")";


    public String stmt = "" +
            "INSERT INTO tpc_ds.store_sales(ss_sold_date_sk, ss_sold_time_sk, ss_item_sk, ss_customer_sk, ss_cdemo_sk, ss_hdemo_sk, ss_addr_sk, ss_store_sk, ss_promo_sk, ss_ticket_number, ss_quantity , ss_wholesale_cost, ss_list_price, ss_sales_price, ss_ext_discount_amt, ss_ext_sales_price, ss_ext_wholesale_cost, ss_ext_list_price, ss_ext_tax, ss_coupon_amt, ss_net_paid, ss_net_paid_inc_tax, ss_net_profit) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

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
                Integer.parseInt(data[10]),
                BigDecimal.valueOf(Double.parseDouble(data[11])),
                BigDecimal.valueOf(Double.parseDouble(data[12])),
                BigDecimal.valueOf(Double.parseDouble(data[13])),
                BigDecimal.valueOf(Double.parseDouble(data[14])),
                BigDecimal.valueOf(Double.parseDouble(data[15])),
                BigDecimal.valueOf(Double.parseDouble(data[16])),
                BigDecimal.valueOf(Double.parseDouble(data[17])),
                BigDecimal.valueOf(Double.parseDouble(data[18])),
                BigDecimal.valueOf(Double.parseDouble(data[19])),
                BigDecimal.valueOf(Double.parseDouble(data[20])),
                BigDecimal.valueOf(Double.parseDouble(data[21])),
                BigDecimal.valueOf(Double.parseDouble(data[22])),
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
