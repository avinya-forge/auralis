--- run.sh	2023-10-24 10:00:00.000000000 +0000
+++ run.sh.new	2023-10-24 10:00:00.000000000 +0000
@@ -29,10 +29,23 @@
         if [ -f "scripts/skills.sh" ]; then
             bash scripts/skills.sh audit
         else
-            grep -E "TASK|DEBT" docs/planning/backlog.md
+            grep -E "EPIC|DEBT" docs/planning/backlog.md
         fi
         ;;
-    --sync|--skills)
+    --sync)
+        echo "[RUN.SH] MODE: SYNC - IDEMPOTENT file-tree alignment"
+        mkdir -p docs/planning docs/architecture docs/engineering docs/release docs/rules
+        for file in docs/planning/backlog.md docs/planning/roadmap.md docs/architecture/system-design.md docs/engineering/conventions.md; do
+            if [ ! -f "$file" ]; then
+                echo "# $(basename "$file" .md | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')" > "$file"
+                echo "" >> "$file"
+                echo "> Auto-populated uniform schema." >> "$file"
+                echo "[RUN.SH] Created missing file: $file"
+            fi
+        done
+        echo "[RUN.SH] Sync complete."
+        ;;
+    --skills)
         echo "[RUN.SH] MODE: EVOLVE"
         echo "[SKILLS] Syncing agentic patterns from https://skills.sh/..."
         mkdir -p scripts
