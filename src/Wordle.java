import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class Wordle {

    public List<String> SOLUTION;
    public Map<String, Double> FREQUENCY;
    public Map<String, Double> INFO;
    public List<String> remaining;
    public List<List<Character>> available;

    public Wordle() throws IOException {
        this("data/words.txt", "data/frequency.json", "data/info.json");
    }

    public Wordle(String words_file, String freq_file, String info_file) throws IOException {
        this.SOLUTION = new ArrayList<>();
        this.FREQUENCY = new HashMap<>();
        this.INFO = new HashMap<>();
        this.remaining = new ArrayList<>();
        initialize(words_file, freq_file, info_file);
    }

    public void initialize(String words_file, String freq_file, String info_file) throws IOException {
        // Load solution words
        for (String w : Files.readAllLines(Paths.get(words_file))) {
            if (w != null && !w.trim().isEmpty()) {
                SOLUTION.add(w.trim().toLowerCase());
            }
        }

        // Loading frequency dictionary 
        parseJson(freq_file, FREQUENCY);

        // Load info dictionary (lowercase keys)
        parseJson(info_file, INFO);

        // current state
        remaining = new ArrayList<>(SOLUTION);
        recompute_available();
    }

    private void parseJson(String file, Map<String, Double> target) throws IOException {
        String json = Files.readString(Paths.get(file)).trim();
        json = json.substring(1, json.length() - 1);
        if (json.isEmpty()) return;
        for (String pair : json.split(",")) {
            String[] kv = pair.split(":");
            String key = kv[0].trim().replace("\"", "").toLowerCase();
            Double val = Double.parseDouble(kv[1].trim());
            target.put(key, val);
        }
    }

    // ---------- helpers ----------
    public void recompute_available() {
        /**Recompute availability from remaining words.*/
        List<Set<Character>> letters = new ArrayList<>();
        for (int i = 0; i < 5; i++) letters.add(new HashSet<>());
        for (String w : remaining) {
            for (int i = 0; i < 5; i++) letters.get(i).add(w.charAt(i));
        }
        available = new ArrayList<>();
        for (Set<Character> s : letters) {
            List<Character> lst = new ArrayList<>(s);
            Collections.sort(lst);
            available.add(lst);
        }
    }

    public double information(String s) {
        /**Sum frequency info of unique letters in a word.*/
        double info = 0.0;
        Set<Character> seen = new HashSet<>();
        for (char c : s.toCharArray()) {
            if (!seen.contains(c)) {
                info += FREQUENCY.getOrDefault(String.valueOf(c), 0.0);
                seen.add(c);
            }
        }
        return info;
    }

    public boolean isvalid(String s) {
        /**Check if word is in remaining and matches positional availability.*/
        if (!remaining.contains(s)) return false;
        for (int i = 0; i < 5; i++)
            if (!available.get(i).contains(s.charAt(i))) return false;
        return true;
    }

    // ---------- Wordle feedback ----------
    public String feedback(String secret, String guess) {
        /**Return pattern string of length 5 with 'G','Y','B' */
        if (secret == null)
            throw new IllegalArgumentException("Did somebody actually called automode without telling the secret word.");

        secret = secret.toLowerCase();
        guess = guess.toLowerCase();
        char[] res = {'B','B','B','B','B'};
        boolean[] used = {false,false,false,false,false};

        // Greens
        for (int i = 0; i < 5; i++) {
            if (guess.charAt(i) == secret.charAt(i)) {
                res[i] = 'G';
                used[i] = true;
            }
        }

        // Yellows
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

    public boolean is_consistent(String word, String guess, String pattern) {
        /**Check if 'word' would produce 'pattern' when guessed with 'guess' tbh i just made a one line function idk why.*/
        return feedback(word, guess).equals(pattern);
    }

    // ---------- state update ----------
    public void update(String guess, String pattern) {
        /**update remaining based on (guess, pattern) and recompute available.*/
        guess = guess.toLowerCase();
        pattern = pattern.toUpperCase();
        List<String> next = new ArrayList<>();
        for (String w : remaining)
            if (is_consistent(w, guess, pattern))
                next.add(w);
        remaining = next;
        recompute_available();
    }

    // ---------- guessing ----------
    public String guess() {
        /**guesses the best word that fits.*/
        if (remaining.isEmpty()) return null;

        // 🔒 SAFE entropy usage: valid guesses only, valid outcomes only
        if (remaining.size() <= 500) {
            Map<String, Object> result =
                    Entropy.bestEntropyWord(remaining, remaining);

            String best = (String) result.get("word");
            if (best != null) return best;
        }

        // ---------- fallback: ORIGINAL LOGIC (UNCHANGED) ----------
        String bestInfo = null;
        double bestVal = -1;
        for (String w : remaining) {
            Double v = INFO.get(w);
            if (v != null && v > bestVal) {
                bestVal = v;
                bestInfo = w;
            }
        }
        if (bestInfo != null) return bestInfo;

        // Fallback 
        String best = null;
        int bestUniq = -1;
        double bestFreq = -1;
        for (String w : remaining) {
            Set<Character> uniq = new HashSet<>();
            for (char c : w.toCharArray()) uniq.add(c);
            double freqsum = 0;
            for (char c : uniq)
                freqsum += FREQUENCY.getOrDefault(String.valueOf(c), 0.0);

            if (uniq.size() > bestUniq ||
               (uniq.size() == bestUniq && freqsum > bestFreq)) {
                bestUniq = uniq.size();
                bestFreq = freqsum;
                best = w;
            }
        }
        return best;
    }

    // ---------- solver ----------
    public int solve(String secret, boolean auto, boolean verbose, int max_attempts) {
        /**
        Play until solved or attempts ended.
        Returns attempts used if solved, else -1.
        */
        remaining = new ArrayList<>(SOLUTION);
        recompute_available();

        Scanner sc = auto ? null : new Scanner(System.in);
        int attempts = 0;

        while (attempts < max_attempts) {
            attempts++;
            String g = guess();
            if (g == null) return -1;

            if (verbose) System.out.println("Guess " + attempts + ": " + g);

            String pattern;
            if (auto) {
                if (secret == null)
                    throw new IllegalArgumentException("Did somebody actually called automode without telling the secret word.");
                pattern = feedback(secret, g);
                if (verbose) System.out.println("Auto feedback: " + pattern);
            } else {
                while (true) {
                    System.out.print("Enter pattern (B/Y/G, length 5): ");
                    pattern = sc.nextLine().trim().toUpperCase();
                    if (pattern.length() == 5 && pattern.chars().allMatch(c -> "BYG".indexOf(c) >= 0)) break;
                    System.out.println("Invalid pattern format. Try again.");
                }
            }

            if (pattern.equals("GGGGG")) return attempts;

            int prev = remaining.size();
            update(g, pattern);
            if (remaining.isEmpty()) return -1;
            if (remaining.size() == prev && verbose)
                System.out.println("No reduction in words so maybe your bot is stupid");
        }
        return -1;
    }

    public static void main(String[] args) throws Exception {
        Wordle solver = new Wordle();

        if (args.length >= 1 && args[0].equalsIgnoreCase("hint")) {
            // GUI hint mode: expects remaining words file
            if (args.length < 2) {
                System.err.println("Usage: java Wordle hint <remaining_file>");
                return;
            }
            List<String> remainingWords = Files.readAllLines(Paths.get(args[1]));
            solver.remaining = new ArrayList<>();
            for (String w : remainingWords) if (!w.isBlank()) solver.remaining.add(w.trim().toLowerCase());
            solver.recompute_available();

            String nextGuess = solver.guess();
            System.out.println(nextGuess == null ? "NO_WORDS_LEFT" : nextGuess);
            return;
        }

        // Normal full simulation mode
        long start = System.currentTimeMillis();
        List<String> words = Files.readAllLines(Paths.get("data/words.txt"));
        Map<Integer, Integer> power = new HashMap<>();
        for (int i : new int[]{1,2,3,4,5,6,-1}) power.put(i, 0);

        for (String w : words) {
            if (w.isBlank()) continue;
            int at = solver.solve(w.trim().toLowerCase(), true, false, 6);
            power.put(at, power.get(at) + 1);
        }

        long elapsed = System.currentTimeMillis() - start;

        // prepare output map
        Map<String, Object> output = new HashMap<>();
        output.put("power", power);
        output.put("time", elapsed / 1000.0);

        // print as single line (Python will read it)
        System.out.println(output);
    }

}
