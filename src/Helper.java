import java.io.IOException;
public class Helper {
    public static void main(String[] args) throws IOException{
        Wordle obj=new Wordle();
        obj.solve(null, false, true, 6);
    }
}
