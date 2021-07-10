package tbc.tables;

import java.math.BigDecimal;

public class Warehouse implements Table {
    public String tableName = "warehouse";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Warehouse (\n" +
            "        w_warehouse_sk bigint PRIMARY KEY,\n" +
            "        w_warehouse_id    varchar,\n" +
            "        w_warehouse_name   varchar,\n" +
            "        w_warehouse_sq_ft int,\n" +
            "        w_street_number varchar,\n" +
            "        w_street_name varchar,\n" +
            "        w_street_type varchar,\n" +
            "        w_suite_number varchar,\n" +
            "        w_city varchar,\n" +
            "        w_county varchar,\n" +
            "        w_state varchar,\n" +
            "        w_zip varchar,\n" +
            "        w_country varchar,\n" +
            "        w_gmt_offset decimal\n" +
            ")";


    public String stmt = "" +
            "INSERT INTO tpc_ds.warehouse(w_warehouse_sk, w_warehouse_id, w_warehouse_name, w_warehouse_sq_ft, w_street_number, w_street_name, w_street_type, w_suite_number, w_city, w_county,w_state, w_zip, w_country, w_gmt_offset)" +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    @Override
    public Object[] convert(String[] data) {
        return new Object[]{
                Long.parseLong(data[0]),
                data[1],
                data[2],
                Integer.parseInt(data[3]),
                data[4],
                data[5],
                data[6],
                data[7],
                data[8],
                data[9],
                data[10],
                data[11],
                data[12],
                BigDecimal.valueOf(Double.parseDouble(data[13]))
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
