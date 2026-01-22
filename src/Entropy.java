import java.util.*;

public class Entropy {

    // cache: guess -> entropy (valid only for current remaining set)
    private static final Map<String, Double> entropyCache = new HashMap<>();

    public static Map<String, Object> bestEntropyWord(
            List<String> remaining,
            List<String> guesses
    ) {
        entropyCache.clear();

        double bestEntropy = -1.0;
        String bestWord = null;

        for (String guess : guesses) {
            double e = entropy(guess, remaining);
            if (e > bestEntropy) {
                bestEntropy = e;
                bestWord = guess;
            }
        }

        Map<String, Object> out = new HashMap<>();
        out.put("word", bestWord);
        out.put("entropy", bestEntropy);
        return out;
    }

    private static double entropy(String guess, List<String> remaining) {
        if (entropyCache.containsKey(guess))
            return entropyCache.get(guess);

        Map<String, Integer> patternCount = new HashMap<>();

        for (String secret : remaining) {
            String p = feedback(secret, guess);
            patternCount.merge(p, 1, Integer::sum);
        }

        double H = 0.0;
        int total = remaining.size();

        for (int count : patternCount.values()) {
            double p = (double) count / total;
            H -= p * log2(p);
        }

        entropyCache.put(guess, H);
        return H;
    }

    private static double log2(double x) {
        return Math.log(x) / Math.log(2);
    }

    // exact same Wordle logic
    private static String feedback(String secret, String guess) {
        char[] res = {'B','B','B','B','B'};
        boolean[] used = new boolean[5];

        for (int i = 0; i < 5; i++) {
            if (guess.charAt(i) == secret.charAt(i)) {
                res[i] = 'G';
                used[i] = true;
            }
        }

        for (int i = 0; i < 5; i++) {
            if (res[i] == 'G') continue;
            for (int j = 0; j < 5; j++) {
                if (!used[j] && guess.charAt(i) == secret.charAt(j)) {
                    res[i] = 'Y';
                    used[j] = true;
                    break;
                }
            }
        }
        return new String(res);
    }
}
