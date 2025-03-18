"""
Test script to verify token streaming in diff_analyzer.py
"""
from diff_analyzer import analyze_diff
import time

def main():
    # Sample git diff for testing
    test_diff = """diff --git a/src/main.rs b/src/main.rs
--- a/src/main.rs
+++ b/src/main.rs
@@ -1,5 +1,7 @@
-fn main() {
-    println!("Hello, world!");
+fn main() -> Result<(), Box<dyn std::error::Error>> {
+    println!("Starting application...");
+    Ok(())
 }"""

    print("Starting analysis...")
    start_time = time.time()
    
    # Run the analysis
    result = analyze_diff(test_diff)
    
    end_time = time.time()
    print("\nAnalysis completed in {:.2f} seconds".format(end_time - start_time))
    print("\nFinal result:")
    print(result)

if __name__ == "__main__":
    main()
