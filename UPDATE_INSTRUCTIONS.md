# Instructions to Add Missing 2026 LAB Meets

## Step 1: Open Excel File
Open `data to add.xlsx`

## Step 2: Go to "Events" Sheet
(This sheet actually contains meet data)

## Step 3: Add Two New Rows
Add these meets to the sheet:

| Meet | DATE | Track Size | Season |
|------|------|------------|--------|
| LAB 1 - 2026 | 12/13/2025 | Indoor | Indoor |
| LAB 2 - 2026 | 12/20/2025 | Indoor | Indoor |

## Step 4: Save the Excel File

## Step 5: Regenerate Dashboard
Run:
```bash
cd "c:/Users/Steve/OneDrive/Programs/track-club-app/waza-dashboard"
python generate_dashboard.py
```

## Step 6: Deploy
```bash
git add -A
git commit -m "Add LAB 1 and LAB 2 2026 meets"
git push
```

The dashboard will update automatically in 1-2 minutes!

## Note
Any results already in the Results sheet with "LAB 1 - 2026" or "LAB 2 - 2026" in the MEET column will automatically get the dates once you add these meets to the Events sheet.
