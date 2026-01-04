"""
Generate a static HTML dashboard from Excel data
Run this whenever you update the Excel file
"""
import openpyxl
import pandas as pd
from datetime import datetime
import json

# Load Excel file
print("Loading Excel data...")
excel_file = "data to add.xlsx"

# Read sheets
athletes_df = pd.read_excel(excel_file, sheet_name="Athletes")
meets_df = pd.read_excel(excel_file, sheet_name="Events")  # Actually contains meets
results_df = pd.read_excel(excel_file, sheet_name="Results")

# Clean data - remove empty rows
athletes_df = athletes_df.dropna(subset=['Athlete'])
meets_df = meets_df.dropna(subset=['Meet'])
results_df = results_df.dropna(subset=['ATHLETE', 'EVENT'])

# Convert EVENT column to string for consistent comparison
results_df['EVENT'] = results_df['EVENT'].astype(str)

# Merge results with meets to get dates
results_with_dates = results_df.merge(
    meets_df[['Meet', 'DATE']],
    left_on='MEET',
    right_on='Meet',
    how='left'
)

# Sort meets by date (newest first)
meets_df = meets_df.sort_values('DATE', ascending=False, na_position='last')

# Sort results by date (newest first)
results_with_dates = results_with_dates.sort_values('DATE', ascending=False, na_position='last')

print(f"Loaded: {len(athletes_df)} athletes, {len(meets_df)} meets, {len(results_df)} results")

# Generate HTML dashboard
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAZA Track Club - Results Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 10px;
            font-size: 1rem;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .search-box {
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .pr-badge {
            background: #ffd700;
            color: #333;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85rem;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏃 WAZA Track Club - Results Dashboard</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">""" + str(len(athletes_df)) + """</div>
                <div class="stat-label">Athletes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">""" + str(len(meets_df)) + """</div>
                <div class="stat-label">Meets</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">""" + str(len(results_df)) + """</div>
                <div class="stat-label">Results</div>
            </div>
        </div>

        <div class="section">
            <div class="tabs">
                <button class="tab active" onclick="showTab('athletes')">Athletes</button>
                <button class="tab" onclick="showTab('meets')">Meets</button>
                <button class="tab" onclick="showTab('results')">Results</button>
                <button class="tab" onclick="showTab('prs')">Personal Records</button>
                <button class="tab" onclick="showTab('progression')">Progression</button>
            </div>

            <div id="athletes-content" class="tab-content active">
                <h2>Athletes</h2>
                <input type="text" class="search-box" id="athleteSearch" placeholder="Search athletes..." onkeyup="filterTable('athletesTable', 'athleteSearch')">
                <table id="athletesTable">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Birth Date</th>
                            <th>Gender</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add athletes
for _, athlete in athletes_df.iterrows():
    name = athlete.get('Athlete', '')
    birth = athlete.get('BirthDate', '')
    gender = athlete.get('Gender', '')

    html_content += f"""
                        <tr>
                            <td>{name}</td>
                            <td>{birth}</td>
                            <td>{gender}</td>
                        </tr>
    """

html_content += """
                    </tbody>
                </table>
            </div>

            <div id="meets-content" class="tab-content">
                <h2>Meets</h2>
                <input type="text" class="search-box" id="meetSearch" placeholder="Search meets..." onkeyup="filterTable('meetsTable', 'meetSearch')">
                <table id="meetsTable">
                    <thead>
                        <tr>
                            <th>Meet Name</th>
                            <th>Date</th>
                            <th>Location</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add meets
for _, meet in meets_df.iterrows():
    name = meet.get('Meet', '')
    date = meet.get('DATE', '')
    season = meet.get('Season', '')

    html_content += f"""
                        <tr>
                            <td>{name}</td>
                            <td>{date}</td>
                            <td>{season}</td>
                        </tr>
    """

html_content += """
                    </tbody>
                </table>
            </div>

            <div id="results-content" class="tab-content">
                <h2>All Results</h2>
                <input type="text" class="search-box" id="resultSearch" placeholder="Search results..." onkeyup="filterTable('resultsTable', 'resultSearch')">
                <table id="resultsTable">
                    <thead>
                        <tr>
                            <th>Athlete</th>
                            <th>Event</th>
                            <th>Result</th>
                            <th>Meet</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add results (with dates from merged dataframe)
for _, result in results_with_dates.iterrows():
    athlete = result.get('ATHLETE', '')
    event = result.get('EVENT', '')
    performance = result.get('Result (Seconds / Meters)', '')
    meet = result.get('MEET', '')
    date = result.get('DATE', '')
    # Format date if it exists
    if pd.notna(date):
        try:
            date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
        except:
            date_str = str(date)
    else:
        date_str = ''

    html_content += f"""
                        <tr>
                            <td>{athlete}</td>
                            <td>{event}</td>
                            <td>{performance}</td>
                            <td>{meet}</td>
                            <td>{date_str}</td>
                        </tr>
    """

html_content += """
                    </tbody>
                </table>
            </div>

            <div id="prs-content" class="tab-content">
                <h2>Personal Records</h2>
                <p style="color: #666; margin-bottom: 20px;">Select an athlete to see their personal records:</p>
                <select id="prAthlete" class="search-box" onchange="showPRs()">
                    <option value="">-- Select Athlete --</option>
"""

# Add athlete options for PR lookup
for _, athlete in athletes_df.iterrows():
    name = athlete.get('Athlete', '')
    if pd.notna(name):
        html_content += f'<option value="{name}">{name}</option>\n'

html_content += """
                </select>
                <div id="prTable"></div>
            </div>

            <div id="progression-content" class="tab-content">
                <h2>Progression Over Time</h2>
                <p style="color: #666; margin-bottom: 20px;">Select an event and athletes to view progression:</p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <label style="display: block; margin-bottom: 10px; font-weight: 600;">Event:</label>
                        <select id="progressionEvent" class="search-box">
                            <option value="">-- Select Event --</option>
"""

# Add unique events for progression
unique_events = [str(e) for e in results_df['EVENT'].unique() if pd.notna(e)]
unique_events = sorted(unique_events)
for event in unique_events:
    html_content += f'<option value="{event}">{event}</option>\n'

html_content += """
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 10px; font-weight: 600;">Athletes (hold Ctrl/Cmd to select multiple):</label>
                        <select id="progressionAthletes" class="search-box" multiple style="height: 150px;">
"""

# Add athlete options for progression
for _, athlete in athletes_df.iterrows():
    name = athlete.get('Athlete', '')
    if pd.notna(name):
        html_content += f'<option value="{name}">{name}</option>\n'

html_content += """
                        </select>
                    </div>
                </div>
                <button onclick="updateProgression()" style="width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; margin-bottom: 20px;">Generate Chart</button>
                <div id="progressionChart" style="width: 100%; height: 500px;"></div>
            </div>
        </div>

        <div class="footer">
            <p>Last updated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
            <p style="margin-top: 10px;">WAZA Track Club © 2025</p>
        </div>
    </div>

    <script>
        // Tab switching
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-content').classList.add('active');
            event.target.classList.add('active');
        }

        // Table filtering
        function filterTable(tableId, searchId) {
            const input = document.getElementById(searchId);
            const filter = input.value.toUpperCase();
            const table = document.getElementById(tableId);
            const tr = table.getElementsByTagName('tr');

            for (let i = 1; i < tr.length; i++) {
                let txtValue = tr[i].textContent || tr[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = '';
                } else {
                    tr[i].style.display = 'none';
                }
            }
        }

        // Store all results for PR calculation (with dates)
        const allResults = """ + results_with_dates.to_json(orient='records', date_format='iso') + """;

        // Show PRs for selected athlete
        function showPRs() {
            const athleteName = document.getElementById('prAthlete').value;
            const prTableDiv = document.getElementById('prTable');

            if (!athleteName) {
                prTableDiv.innerHTML = '';
                return;
            }

            // Filter results for this athlete
            const athleteResults = allResults.filter(r => r.ATHLETE === athleteName);

            if (athleteResults.length === 0) {
                prTableDiv.innerHTML = '<p style="color: #999; margin-top: 20px;">No results found for this athlete.</p>';
                return;
            }

            // Group by event and find best
            const prs = {};
            athleteResults.forEach(result => {
                const event = result.EVENT;
                const performance = result['Result (Seconds / Meters)'];
                if (!prs[event]) {
                    prs[event] = result;
                } else {
                    // For time events (lower is better), for distance events (higher is better)
                    // Simple comparison - assumes lower is better
                    if (performance < prs[event]['Result (Seconds / Meters)']) {
                        prs[event] = result;
                    }
                }
            });

            // Build PR table
            let html = '<table style="margin-top: 20px;"><thead><tr><th>Event</th><th>PR</th><th>Meet</th><th>Date</th></tr></thead><tbody>';
            Object.keys(prs).sort().forEach(event => {
                const pr = prs[event];
                const date = pr.DATE ? new Date(pr.DATE).toLocaleDateString() : 'N/A';
                html += `<tr>
                    <td>${event}</td>
                    <td><span class="pr-badge">${pr['Result (Seconds / Meters)']}</span></td>
                    <td>${pr.MEET}</td>
                    <td>${date}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            prTableDiv.innerHTML = html;
        }

        // Progression chart
        function updateProgression() {
            const event = document.getElementById('progressionEvent').value;
            const athleteSelect = document.getElementById('progressionAthletes');
            const selectedAthletes = Array.from(athleteSelect.selectedOptions).map(opt => opt.value);

            if (!event || selectedAthletes.length === 0) {
                document.getElementById('progressionChart').innerHTML = '<p style="color: #999; padding: 40px; text-align: center;">Select an event and at least one athlete to view progression</p>';
                return;
            }

            // Filter results for selected event and athletes
            // EVENT is already converted to string in Python, but double-check here
            const eventResults = allResults.filter(r => {
                const eventMatch = String(r.EVENT) === String(event);
                const athleteMatch = selectedAthletes.includes(r.ATHLETE);
                const hasDate = r.DATE != null && r.DATE !== '';
                return eventMatch && athleteMatch && hasDate;
            });

            console.log('Selected event:', event);
            console.log('Selected athletes:', selectedAthletes);
            console.log('Filtered results:', eventResults.length);
            console.log('Sample result EVENT type:', eventResults.length > 0 ? typeof eventResults[0].EVENT : 'none');

            if (eventResults.length === 0) {
                // More detailed error message
                const allEventsForAthletes = allResults.filter(r => selectedAthletes.includes(r.ATHLETE));
                const uniqueEvents = [...new Set(allEventsForAthletes.map(r => String(r.EVENT)))];
                document.getElementById('progressionChart').innerHTML =
                    `<p style="color: #999; padding: 40px; text-align: center;">
                        No results found for ${event} with selected athletes.<br>
                        <small>Available events for selected athletes: ${uniqueEvents.join(', ')}</small>
                    </p>`;
                return;
            }

            // Group by athlete
            const traces = [];
            selectedAthletes.forEach(athlete => {
                const athleteResults = eventResults
                    .filter(r => r.ATHLETE === athlete)
                    .sort((a, b) => new Date(a.DATE) - new Date(b.DATE));

                if (athleteResults.length > 0) {
                    traces.push({
                        x: athleteResults.map(r => new Date(r.DATE)),
                        y: athleteResults.map(r => r['Result (Seconds / Meters)']),
                        mode: 'lines+markers',
                        name: athlete,
                        type: 'scatter',
                        text: athleteResults.map(r => r.MEET),
                        hovertemplate: '<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>Time: %{y}<extra></extra>'
                    });
                }
            });

            // Helper function to format seconds as MM:SS.xx
            function formatTime(seconds) {
                const mins = Math.floor(seconds / 60);
                const secs = (seconds % 60).toFixed(2);
                return mins > 0 ? `${mins}:${secs.padStart(5, '0')}` : `${secs}s`;
            }

            const layout = {
                title: event + ' Progression',
                xaxis: { title: 'Date' },
                yaxis: {
                    title: 'Performance',
                    autorange: 'reversed',  // Lower is better for time events
                    tickformat: '',
                    tickmode: 'auto',
                    ticksuffix: ''
                },
                hovermode: 'closest',
                showlegend: true,
                plot_bgcolor: '#f8f9fa',
                paper_bgcolor: 'white'
            };

            // Update hover template to show formatted time
            traces.forEach(trace => {
                trace.hovertemplate = '<b>%{text}</b><br>Date: %{x|%Y-%m-%d}<br>Time: %{customdata}<extra></extra>';
                trace.customdata = trace.y.map(formatTime);
            });

            const config = {
                responsive: true,
                displayModeBar: true
            };

            Plotly.newPlot('progressionChart', traces, layout, config).then(function(gd) {
                // Format y-axis tick labels as MM:SS.xx
                const yaxis = gd._fullLayout.yaxis;
                const tickvals = yaxis.tickvals;
                const ticktext = tickvals.map(formatTime);

                Plotly.relayout(gd, {
                    'yaxis.tickvals': tickvals,
                    'yaxis.ticktext': ticktext
                });
            });
        }
    </script>
</body>
</html>
"""

# Write HTML file
output_file = "index.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n[OK] Dashboard generated: {output_file}")
print(f"\nTo view: Open {output_file} in your browser")
print(f"To update: Edit the Excel file and run this script again")
print(f"\nTo deploy to pearseprojects.org:")
print(f"1. Upload {output_file} to your web server")
print(f"2. Configure DNS to point waza.pearseprojects.org to it")
