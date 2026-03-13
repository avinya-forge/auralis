--- run.sh	2023-10-24 10:00:00.000000000 +0000
+++ run.sh.new	2023-10-24 10:00:00.000000000 +0000
@@ -37,7 +37,8 @@
         mkdir -p docs/planning docs/architecture docs/engineering docs/release docs/rules
         for file in docs/planning/backlog.md docs/planning/roadmap.md docs/architecture/system-design.md docs/engineering/conventions.md; do
             if [ ! -f "$file" ]; then
-                echo "# $(basename "$file" .md | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')" > "$file"
+                title="$(basename "$file" .md | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')"
+                echo "# $title" > "$file"
                 echo "" >> "$file"
                 echo "> Auto-populated uniform schema." >> "$file"
                 echo "[RUN.SH] Created missing file: $file"
