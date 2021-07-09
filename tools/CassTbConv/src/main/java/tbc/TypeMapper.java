package tbc;

import java.math.BigInteger;

public class TypeMapper {
    public static Object map(String type, String value) {
        if(type.equals("int")) return Integer.parseInt(value);
        if(type.equals("bigInt")) return BigInteger.valueOf(Integer.parseInt(value));
        if(type.equals("String")) return value;
        if(type.equals("varchar")) return value.charAt(0);
        if(type.equals("double")) return Double.valueOf(value);
        if(type.equals("float")) return Float.valueOf(value);

        System.out.println("Cannot convert value as type " + type);
        return null;
    }
}
