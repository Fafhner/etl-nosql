package tbc;

public class TableInfo {
    public String outputDir;
    public String outputDirName;
    public String dataSrcPath;
    public String tableName;

    public TableInfo() {
    }

    public String getOutputDir() {
        return outputDir;
    }

    public void setOutputDir(String outputDir) {
        this.outputDir = outputDir;
    }

    public String getOutputDirName() {
        return outputDirName;
    }

    public void setOutputDirName(String outputDirName) {
        this.outputDirName = outputDirName;
    }

    public String getDataSrcPath() {
        return dataSrcPath;
    }

    public void setDataSrcPath(String dataSrcPath) {
        this.dataSrcPath = dataSrcPath;
    }

    public String getTableName() {
        return tableName;
    }

    public void setTableName(String tableName) {
        this.tableName = tableName;
    }
}
