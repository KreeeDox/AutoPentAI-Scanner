// LAB-ONLY: Final JS with Nmap Text Animation & Overflow Fix
let riskChart = null; let vulnerabilityDB = {}; 
async function loadVulnerabilityDB() { try { const response = await fetch('/static/vulnerability_db.json'); if (!response.ok) { console.error('Failed to load vulnerability_db.json'); return; } vulnerabilityDB = await response.json(); console.log('Vulnerability DB loaded.'); } catch (error) { console.error('Error loading vulnerability DB:', error); } }
document.addEventListener('DOMContentLoaded', () => {
    loadVulnerabilityDB(); 
    // Get Elements (All elements including Nmap area)
    const scanButton=document.getElementById('scan-button'), reportButton=document.getElementById('report-button'); const targetInput=document.getElementById('target'), nmapReportArea=document.getElementById('nmap-report-area'); const errorArea=document.getElementById('error-area'), chartCanvas=document.getElementById('riskChart'); const progressBar=document.getElementById('scanning-progress-bar'), progressText=document.getElementById('scanning-text'); const progressBarFill=document.getElementById('progress-bar-anim'), nmapProgressBar=document.getElementById('nmap-progress-bar'); const nmapBarFill=document.getElementById('nmap-bar-anim'); const niktoArea = document.getElementById('nikto-results-area'), niktoSummary = document.getElementById('nikto-summary'); const recommendationsArea = document.getElementById('recommendations-area'), recommendationsList = document.getElementById('recommendations-list');
    const chartColors = { critical: 'rgba(255, 82, 82, o.7)', high: 'rgba(0, 255, 156, 0.7)', medium: 'rgba(241, 196, 15, 0.7)', low: 'rgba(46, 204, 113, 0.7)', default: 'rgba(68, 71, 90, 0.7)' }; const ctx = chartCanvas.getContext('2d'); riskChart = new Chart(ctx, { type: 'doughnut', data: { labels: ['Awaiting Scan'], datasets: [{ label: 'Risk Breakdown', data: [1], backgroundColor: [chartColors.default], borderColor: '#0d1117', borderWidth: 3 }] }, options: { responsive: true, plugins: { legend: { position: 'top', labels: { color: '#c9d1d9', font: { family: "'Roboto Mono', monospace" } } }, title: { display: true, text: 'Scan Results', color: '#c9d1d9', font: { size: 16, family: "'Roboto Mono', monospace" } } } } });

    scanButton.addEventListener('click', async () => {
        const target = targetInput.value; if (!(target === '127.0.0.1' || target === 'localhost' || target.startsWith('192.168.56.'))) { errorArea.textContent = `Error: Invalid target '${target}'.`; errorArea.style.display = 'block'; return; }
        
        // --- UI RESET ---
        scanButton.disabled = true; scanButton.textContent = 'Scanning...'; 
        reportButton.classList.add('disabled'); errorArea.style.display = 'none'; 
        chartCanvas.style.display = 'none'; progressBar.style.display = 'block'; 
        progressText.style.display = 'block'; nmapProgressBar.style.display = 'block'; 
        niktoArea.style.display = 'none'; recommendationsArea.style.display = 'none'; 
        recommendationsList.innerHTML = ''; 
        
        // --- Nmap Text Area Setup ---
        // Ensure initial state for animation
        nmapReportArea.classList.remove('scanning'); // Remove class to reset animation
        nmapReportArea.style.backgroundPosition = '-100% 0'; // Instantly reset position for transition
        nmapReportArea.textContent = 'Initializing Nmap & Nikto scan...'; // Set text
        // For -webkit-text-fill-color, it also needs to be reset/set correctly
        nmapReportArea.style.webkitTextFillColor = 'transparent'; 
        nmapReportArea.style.textFillColor = 'transparent'; 
        // --- END Nmap Text Setup ---

        // --- START ANIMATIONS ---
        progressBarFill.classList.remove('scanning'); nmapBarFill.classList.remove('scanning'); 
        void progressBarFill.offsetWidth; // Force reflow
        progressBarFill.classList.add('scanning'); nmapBarFill.classList.add('scanning'); 
        
        // Start Nmap text area fill
        // Force reflow for nmapReportArea too before adding class
        void nmapReportArea.offsetWidth; 
        nmapReportArea.classList.add('scanning'); 
        // --- END ANIMATION START ---

        try {
            const response = await fetch('/scan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target: target }) }); 
            const results = await response.json(); 
             
            // Stop Nmap text animation, show final text
            nmapReportArea.classList.remove('scanning'); 
            nmapReportArea.style.backgroundPosition = '0 0'; // Ensure it's fully shown
            nmapReportArea.style.webkitTextFillColor = 'var(--text-color)'; // Make final text visible
            nmapReportArea.style.textFillColor = 'var(--text-color)'; 

            if (!response.ok) { 
                errorArea.textContent = `Error from server: ${results.error || 'Unknown error'} - ${results.message || ''}`; errorArea.style.display = 'block'; 
                updateChart(['Scan Failed'], [1], [chartColors.critical], 'Error');
            } else {
                const predictionLabel = results.prediction.label; const predictionConfidence = parseFloat(results.prediction.confidence); let riskColor = chartColors.default;
                if (predictionLabel.toLowerCase().includes('critical') || predictionLabel.toLowerCase().includes('compromised')) { riskColor = chartColors.critical; } else if (predictionLabel.toLowerCase().includes('high')) { riskColor = chartColors.high; } else if (predictionLabel.toLowerCase().includes('medium')) { riskColor = chartColors.medium; }
                updateChart([predictionLabel, 'Other Possibilities'], [predictionConfidence, 100 - predictionConfidence], [riskColor, 'rgba(22, 27, 34, 0.5)'], `Prediction: ${predictionLabel} (${predictionConfidence.toFixed(2)}%)`);
                
                let nmapOutput = `Target: ${results.target}\n`; nmapOutput += `Status: ${results.scan_report.status.state}\n\n`; nmapOutput += `Open Ports Found:\n------------------\n`; let foundRecommendations = []; 
                if (results.scan_report.tcp) { for (const [port, data] of Object.entries(results.scan_report.tcp)) { nmapOutput += `Port ${port} (${data.state}): ${data.product || ''} ${data.version || ''}\n`; if (data.state === 'open') { const service_key = `${data.product || ''} ${data.version || ''}`.toLowerCase().trim(); let recommendation = null; if (service_key && vulnerabilityDB[service_key]) { recommendation = vulnerabilityDB[service_key].recommendation; } else if (service_key) { let bestMatchKey = null; for(const dbKey in vulnerabilityDB){ if(dbKey && service_key.includes(dbKey) && (bestMatchKey === null || dbKey.length > bestMatchKey.length)) {bestMatchKey = dbKey;}} if(bestMatchKey){ recommendation = vulnerabilityDB[bestMatchKey].recommendation;} } if (!recommendation && data.name && vulnerabilityDB[data.name.toLowerCase()]) { recommendation = vulnerabilityDB[data.name.toLowerCase()].recommendation; } if (recommendation && !foundRecommendations.includes(recommendation)) { foundRecommendations.push(recommendation); } } } } else { nmapOutput += "No open TCP ports found.\n"; } 
                nmapReportArea.textContent = nmapOutput; // Display final Nmap text
                
                if (results.nikto_vuln_count !== undefined && results.nikto_vuln_count > 0) { niktoSummary.textContent = `Nikto found ${results.nikto_vuln_count} web vulns.`; niktoArea.style.display = 'block'; const webReco = "Review Nikto findings."; if (!foundRecommendations.includes(webReco)) foundRecommendations.push(webReco); } else if (results.nikto_vuln_count !== undefined && results.nikto_vuln_count === 0) { niktoSummary.textContent = `Nikto: No major web vulns found.`; niktoArea.style.display = 'block'; }
                if (foundRecommendations.length > 0) { recommendationsList.innerHTML = foundRecommendations.map(reco => `<li>${reco}</li>`).join(''); recommendationsArea.style.display = 'block'; } else { recommendationsList.innerHTML = '<li>No specific recommendations. Ensure patching.</li>'; recommendationsArea.style.display = 'block'; } 
                reportButton.classList.remove('disabled');
            }
        } catch (error) { 
            console.error('Fetch error:', error); errorArea.textContent = 'A critical error occurred. Check server logs.'; errorArea.style.display = 'block'; 
            nmapReportArea.classList.remove('scanning'); // Stop animation on error
            nmapReportArea.style.backgroundPosition = '0 0'; 
            nmapReportArea.textContent = 'Error during scan...'; // Show error text
        } finally { 
            scanButton.disabled = false; scanButton.textContent = 'Start Scan'; 
            progressBar.style.display = 'none'; progressText.style.display = 'none'; 
            chartCanvas.style.display = 'block'; nmapProgressBar.style.display = 'none'; 
            progressBarFill.classList.remove('scanning'); nmapBarFill.classList.remove('scanning'); 
            nmapReportArea.classList.remove('scanning'); // Ensure class is removed
            nmapReportArea.style.backgroundPosition = '0 0'; // Ensure reset
            nmapReportArea.style.webkitTextFillColor = 'var(--text-color)'; // Ensure final text is visible
            nmapReportArea.style.textFillColor = 'var(--text-color)'; 
        }
    });
});
function updateChart(labels, data, colors, titleText) { if (riskChart) { riskChart.data.labels = labels; riskChart.data.datasets[0].data = data; riskChart.data.datasets[0].backgroundColor = colors; riskChart.options.plugins.title.text = titleText; riskChart.update(); } }
