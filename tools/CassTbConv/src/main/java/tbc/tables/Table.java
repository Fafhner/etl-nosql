package tbc.tables;

import java.text.ParseException;

public interface Table {
    String tableName = "";
    String schema = "";
    String stmt = "";

    public Object[] convert(String [] data) throws ParseException;

    public String getTableName();
    public String getSchema();
    public String getStmt();
}
