package tbc.tables;

import java.math.BigDecimal;

public class Customer implements Table {
    public String tableName = "customer";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Customer   (\n" +
            "        c_customer_sk bigint PRIMARY KEY,\n" +
            "        c_customer_id     varchar,\n" +
            "        c_current_cdemo_sk   bigint,\n" +
            "        c_current_hdemo_sk bigint,\n" +
            "        c_current_addr_sk bigint,\n" +
            "        c_first_shipto_date_sk bigint,\n" +
            "        c_first_sales_date_sk bigint,\n" +
            "        c_salutation varchar,\n" +
            "        c_first_name varchar,\n" +
            "        c_last_name varchar,\n" +
            "        c_preferred_cust_flag ascii,\n" +
            "        c_birth_day int,\n" +
            "        c_birth_month  int,\n" +
            "        c_birth_year int,\n" +
            "        c_birth_country varchar,\n" +
            "        c_login  varchar,\n" +
            "        c_email_address varchar,\n" +
            "        c_last_review_date_sk bigint\n" +
            ")";


    public String stmt = "" +
            "INSERT INTO tpc_ds.customer(c_customer_sk, c_customer_id, c_current_cdemo_sk, c_current_hdemo_sk, c_current_addr_sk, c_first_shipto_date_sk, c_first_sales_date_sk, c_salutation, c_first_name, c_last_name, c_preferred_cust_flag, c_birth_day, c_birth_month, c_birth_year, c_birth_country, c_login, c_email_address, c_last_review_date_sk) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    @Override
    public Object[] convert(String[] data) {
        return new Object[]{
                Long.parseLong(data[0]),
                data[1],
                Long.parseLong(data[2]),
                Long.parseLong(data[3]),
                Long.parseLong(data[4]),
                Long.parseLong(data[5]),
                Long.parseLong(data[6]),
                data[7],
                data[8],
                data[9],
                data[10].charAt(0),
                Integer.parseInt(data[11]),
                Integer.parseInt(data[12]),
                Integer.parseInt(data[13]),
                data[14],
                data[15],
                data[16],
                Long.parseLong(data[17]),
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
