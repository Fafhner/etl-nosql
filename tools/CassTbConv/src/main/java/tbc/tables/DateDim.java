package tbc.tables;

import com.datastax.driver.core.LocalDate;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class DateDim implements Table {
    public String tableName = "date_dim";
    public String schema = "" +
            "CREATE TABLE tpc_ds.Date_dim    (\n" +
            "    d_date_sk bigint PRIMARY KEY,\n" +
            "        d_date_id    varchar,\n" +
            "        d_date date,\n" +
            "        d_month_seq int,\n" +
            "        d_week_seq int,\n" +
            "        d_quarter_seq int,\n" +
            "        d_year int,\n" +
            "        d_dow int,\n" +
            "        d_moy int,\n" +
            "        d_dom int,\n" +
            "        d_qoy int,\n" +
            "        d_fy_year int,\n" +
            "        d_fy_quarter_seq  int,\n" +
            "        d_fy_week_seq  int,\n" +
            "        d_day_name varchar,\n" +
            "        d_quarter_name varchar,\n" +
            "        d_holiday ascii,\n" +
            "        d_weekend ascii,\n" +
            "        d_following_holiday ascii,\n" +
            "        d_first_dom int,\n" +
            "        d_last_dom int,\n" +
            "        d_same_day_ly int,\n" +
            "        d_same_day_lq int,\n" +
            "        d_current_day ascii,\n" +
            "        d_current_week ascii,\n" +
            "        d_current_month ascii,\n" +
            "        d_current_quarter ascii,\n" +
            "        d_current_year ascii\n" +
            ")";

    public String stmt = "" +
            "INSERT INTO tpc_ds.date_dim(d_date_sk, d_date_id, d_date, d_month_seq, d_week_seq, d_quarter_seq, d_year, d_dow, d_moy, d_dom, d_qoy, d_fy_year, d_fy_quarter_seq, d_fy_week_seq, d_day_name, d_quarter_name, d_holiday, d_weekend, d_following_holiday, d_first_dom, d_last_dom, d_same_day_ly, d_same_day_lq, d_current_day, d_current_week, d_current_month, d_current_quarter, d_current_year) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    @Override
    public Object[] convert(String[] data) throws ParseException {
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd", Locale.ENGLISH);
        Date date = formatter.parse(data[1].trim());
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);
        LocalDate ld =  LocalDate.fromYearMonthDay(cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH));

        return new Object[]{
                Long.parseLong(data[0]),
                data[1],
                ld,
                Integer.parseInt(data[3]),
                Integer.parseInt(data[4]),
                Integer.parseInt(data[5]),
                Integer.parseInt(data[6]),
                Integer.parseInt(data[7]),
                Integer.parseInt(data[8]),
                Integer.parseInt(data[9]),
                Integer.parseInt(data[10]),
                Integer.parseInt(data[11]),
                Integer.parseInt(data[12]),
                Long.parseLong(data[13]),
                data[14],
                data[15],
                data[16].charAt(0),
                data[17].charAt(0),
                data[18].charAt(0),
                Integer.parseInt(data[19]),
                Integer.parseInt(data[20]),
                Integer.parseInt(data[21]),
                Integer.parseInt(data[22]),
                data[23].charAt(0),
                data[24].charAt(0),
                data[25].charAt(0),
                data[26].charAt(0),
                data[27].charAt(0)
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
