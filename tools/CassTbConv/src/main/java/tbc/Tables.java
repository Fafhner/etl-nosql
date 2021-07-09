package tbc;

import tbc.tables.*;

import java.util.ArrayList;
import java.util.HashMap;

public class Tables {
    public HashMap<String, Table> tables;
    public ArrayList<TableInfo> infos;

    public Tables() {
        tables = new HashMap<>();
        infos = new ArrayList<>();

        CatalogReturns cr = new CatalogReturns();
        CatalogSales cs = new CatalogSales();
        Customer c = new Customer();
        DateDim dd = new DateDim();
        StoreSales ss = new StoreSales();
        Warehouse w = new Warehouse();
        WebSales wb = new WebSales();

        tables.put(cr.tableName, cr);
        tables.put(cs.tableName, cs);
        tables.put(c.tableName, c);
        tables.put(dd.tableName, dd);
        tables.put(ss.tableName, ss);
        tables.put(w.tableName, w);
        tables.put(wb.tableName, wb);
    }

    public HashMap<String, Table> getTables() {
        return tables;
    }

    public void setTables(HashMap<String, Table> tables) {
        this.tables = tables;
    }

    public ArrayList<TableInfo> getInfos() {
        return infos;
    }

    public void setInfos(ArrayList<TableInfo> infos) {
        this.infos = infos;
    }
}
