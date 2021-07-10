package tbc;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.ParseException;
import java.util.Scanner;

import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.opencsv.CSVParserBuilder;
import com.opencsv.exceptions.CsvValidationException;
import org.apache.cassandra.dht.Murmur3Partitioner;
import org.apache.cassandra.exceptions.InvalidRequestException;
import org.apache.cassandra.io.sstable.CQLSSTableWriter;
import tbc.tables.Table;

public class Converter {
    public static String readFile(String filePath) throws FileNotFoundException {
        StringBuilder sb = new StringBuilder();
        File fileObj = new File(filePath);
        Scanner sc = new Scanner(fileObj);
        while (sc.hasNextLine()) {
            sb.append(sc.nextLine());
        }
        sc.close();

        return sb.toString();
    }

    public static void createSSTable(String dataPath, String outDir, Table table) throws IOException, CsvValidationException, ParseException {
        CQLSSTableWriter.Builder builder = CQLSSTableWriter.builder();
        System.out.println("Generating sstable in path " + dataPath + "for table " +
                table.getTableName() + " output: " + outDir);
        builder.inDirectory(outDir)
                .forTable(table.getSchema())
                .using(table.getStmt())
                .withPartitioner(new Murmur3Partitioner());
        CQLSSTableWriter writer = builder.build();

        CSVReader reader = new CSVReaderBuilder(new FileReader(dataPath))
                .withCSVParser(new CSVParserBuilder().withSeparator('|').build()).build();


        String [] nextLine;
        try {
            while ((nextLine = reader.readNext()) != null) {
                writer.addRow(table.convert(nextLine));
            }
        }
        catch(Exception e) {
            writer.close();
            throw e;
        }



    }

    public static void main(String[] args) throws IOException, CsvValidationException, InvalidRequestException {
        String tablesPath = args[0];
        String fileContent = readFile(tablesPath);
        ObjectMapper mapper = new ObjectMapper();
        Tables tables = mapper.readValue(fileContent, Tables.class);



        for(TableInfo info: tables.infos) {
            Path path = Paths.get(info.outputDir+"/"+info.outputDirName);
            Files.createDirectories(path);
            try {
                createSSTable(info.dataSrcPath, path.toString(), tables.tables.get(info.tableName));
            }
            catch (ParseException e) {
                BufferedWriter writer = new BufferedWriter(new FileWriter(path.toString()));
                writer.write(e.getMessage());
                writer.close();
                return;
            }

        }

        return;
    }
}
