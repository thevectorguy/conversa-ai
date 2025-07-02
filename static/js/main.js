document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("login-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const loginModal = document.getElementById("login-modal");
    const closeModal = document.getElementById("close-modal");
    const loginForm = document.getElementById("login-form");
    const authButtons = document.getElementById("auth-buttons");
    const userInfo = document.getElementById("user-info");
    const usernameDisplay = document.getElementById("username");
    const dashboardContent = document.getElementById("dashboard-content");
    const welcomeScreen = document.getElementById("welcome-screen");
    const summaryContent = document.getElementById("summary-content");
    const agentStatsDiv = document.getElementById("agent-stats");
    const analyzeBtn = document.getElementById("analyze-btn");
    const transcriptInput = document.getElementById("transcript-input");
    const analysisResults = document.getElementById("analysis-results");
    const resultsContent = document.getElementById("results-content");
    const loadingOverlay = document.getElementById("loading-overlay");
    const clearInputBtn = document.getElementById("clear-input");

    let token = localStorage.getItem("token");
    let user = localStorage.getItem("user");
    
    // Clear input functionality
    if (clearInputBtn) {
        clearInputBtn.addEventListener("click", () => {
            transcriptInput.value = "";
            // Also clear analysis results
            analysisResults.classList.add("hidden");
            // Reset summary to initial state
            summaryContent.innerHTML = `
                <div class="text-center text-gray-400 p-8">
                    <i class="fas fa-upload text-4xl mb-4"></i>
                    <p class="text-lg mb-2">No transcript analyzed yet</p>
                    <p class="text-sm">Upload or paste a transcript to see its summary and sentiment analysis here.</p>
                </div>
            `;
        });
    }

    function showDashboard() {
        authButtons.classList.add("hidden");
        userInfo.classList.remove("hidden");
        welcomeScreen.classList.add("hidden");
        dashboardContent.classList.remove("hidden");
        usernameDisplay.innerText = user;
        
        // Initialize with empty summary - will be populated after transcript analysis
        summaryContent.innerHTML = `
            <div class="text-center text-gray-400 p-8">
                <i class="fas fa-upload text-4xl mb-4"></i>
                <p class="text-lg mb-2">No transcript analyzed yet</p>
                <p class="text-sm">Upload or paste a transcript to see its summary and sentiment analysis here.</p>
            </div>
        `;
        
        fetchAgentStats(); // Still show dataset agent stats for reference
    }

    function showLogin() { 
        loginModal.classList.remove("hidden"); 
        loginModal.classList.add("flex");
    }
    
    function hideLogin() { 
        loginModal.classList.add("hidden"); 
        loginModal.classList.remove("flex");
    }

    loginBtn.addEventListener("click", showLogin);
    closeModal.addEventListener("click", hideLogin);

    // Add error message element to the login form
    const loginErrorDiv = document.createElement("div");
    loginErrorDiv.id = "login-error";
    loginErrorDiv.className = "text-red-500 text-center mt-4 hidden";
    document.querySelector("#login-form").insertAdjacentElement('afterend', loginErrorDiv);
    
    function showLoginError(message) {
        const loginError = document.getElementById("login-error");
        loginError.textContent = message;
        loginError.classList.remove("hidden");
    }
    
    function hideLoginError() {
        const loginError = document.getElementById("login-error");
        loginError.classList.add("hidden");
    }
    
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById("username-input").value;
        const passwordInput = document.getElementById("password-input").value;
        
        // Hide any previous error
        hideLoginError();
        
        try {
            const res = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: usernameInput, password: passwordInput })
            });
            
            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || "Login failed");
            }
            
            const data = await res.json();
            token = data.access_token;
            user = data.user_info.username;
            localStorage.setItem("token", token);
            localStorage.setItem("user", user);
            hideLogin();
            showDashboard();
        } catch (err) {
            showLoginError("Login failed: " + err.message);
        }
    });

    logoutBtn.addEventListener("click", () => {
        localStorage.clear();
        location.reload();
    });

    async function fetchSummary() {
        summaryContent.innerHTML = '<div class="text-center text-gray-400"><i class="fas fa-spinner fa-spin text-2xl mb-2"></i><p>Loading summary...</p></div>';
        
        try {
            const res = await fetch("/api/summary", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            if (!res.ok) throw new Error("Failed to fetch summary");
            
            const { data: d } = await res.json();
            document.getElementById("total-transcripts").innerText = d.total_transcripts;
            document.getElementById("total-messages").innerText = d.total_messages;
            document.getElementById("unique-articles").innerText = d.unique_articles;
            document.getElementById("avg-messages").innerText = d.avg_messages_per_transcript;
            
            // Build the summary content
            let summaryHtml = '<div class="space-y-4">';
            
            // Add dataset summary if available
            if (d.dataset_summary) {
                summaryHtml += `
                    <div class="bg-gradient-to-r from-blue-800 to-purple-800 rounded-lg p-4 shadow-lg">
                        <h4 class="text-white font-semibold mb-2">Dataset Summary</h4>
                        <p class="text-gray-200">${d.dataset_summary}</p>
                    </div>
                `;
            }
            
            // Always add sentiment distribution
            summaryHtml += `
                <div class="bg-gray-700 rounded-lg p-4">
                    <h4 class="text-white font-semibold mb-2">Sentiment Distribution</h4>
                    <div class="space-y-2">
                        ${Object.entries(d.sentiment_distribution).map(([sentiment, count]) => {
                            // Format the sentiment for display (capitalize words, replace underscores)
                            const formattedSentiment = sentiment
                                .split('_')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                            
                            return `<div class="flex justify-between text-gray-300">
                                <span>${formattedSentiment}</span>
                                <span>${count}</span>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            `;
            
            summaryHtml += '</div>';
            summaryContent.innerHTML = summaryHtml;
        } catch (err) {
            summaryContent.innerHTML = `<p class="text-red-500">Error: ${err.message}</p>`;
        }
    }

    async function fetchAgentStats() {
        agentStatsDiv.innerHTML = '<div class="text-center text-gray-400"><i class="fas fa-spinner fa-spin text-2xl mb-2"></i><p>Loading agent statistics...</p></div>';
        
        try {
            const res = await fetch("/api/stats/agents", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            
            if (!res.ok) throw new Error("Failed to fetch agent stats");
            
            const data = await res.json();
            agentStatsDiv.innerHTML = "";
            
            for (const [agent, stats] of Object.entries(data.agent_statistics)) {
                const card = document.createElement("div");
                card.className = "card-hover p-6 bg-gray-700 rounded-lg border border-gray-600";
                // No sentiment distribution formatting needed
                
                card.innerHTML = `
                    <h3 class="text-white font-bold text-lg mb-4">${agent}</h3>
                    <div class="space-y-2 text-gray-300">
                        <p><span class="font-medium">Messages:</span> ${stats.total_messages}</p>
                        <p><span class="font-medium">Avg Words:</span> ${stats.avg_word_count}</p>
                        <p><span class="font-medium">Avg Sentiment:</span> ${stats.avg_sentiment_score}</p>
                        <p><span class="font-medium">Transcripts:</span> ${stats.unique_transcripts}</p>
                    </div>
                `;
                agentStatsDiv.appendChild(card);
            }
        } catch (err) {
            agentStatsDiv.innerHTML = `<p class="text-red-500">Error: ${err.message}</p>`;
        }
    }

    // File upload handling
    const inputMethodRadios = document.querySelectorAll('input[name="input-method"]');
    const pasteContainer = document.getElementById("paste-container");
    const uploadContainer = document.getElementById("upload-container");
    const fileInput = document.getElementById("file-input");
    const browseBtn = document.getElementById("browse-btn");
    const fileName = document.getElementById("file-name");
    
    let fileContent = null;
    
    // Toggle between paste and upload methods
    inputMethodRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "paste") {
                pasteContainer.classList.remove("hidden");
                uploadContainer.classList.add("hidden");
            } else {
                pasteContainer.classList.add("hidden");
                uploadContainer.classList.remove("hidden");
            }
        });
    });
    
    // Handle file browsing
    browseBtn.addEventListener("click", () => {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileName.classList.remove("hidden");
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    // Store the raw text content
                    fileContent = event.target.result;
                    // Try parsing it to validate it's proper JSON
                    JSON.parse(fileContent);
                    console.log("File loaded successfully and validated as JSON");
                } catch (err) {
                    console.error("Error parsing JSON file:", err);
                    alert("The selected file does not contain valid JSON data");
                    fileContent = null;
                    fileName.classList.add("hidden");
                }
            };
            reader.onerror = () => {
                console.error("Error reading file");
                alert("Error reading file");
                fileContent = null;
                fileName.classList.add("hidden");
            };
            reader.readAsText(file);
        }
    });
    
    // Handle drag and drop
    const dropZone = uploadContainer.querySelector("div");
    
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("border-blue-500");
    });
    
    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("border-blue-500");
    });
    
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-blue-500");
        
        const file = e.dataTransfer.files[0];
        if (file) {
            // Accept any file extension but validate content as JSON
            fileInput.files = e.dataTransfer.files;
            fileName.textContent = file.name;
            fileName.classList.remove("hidden");
            
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    // Store the raw text content
                    fileContent = event.target.result;
                    // Try parsing it to validate it's proper JSON
                    JSON.parse(fileContent);
                    console.log("File loaded successfully and validated as JSON");
                } catch (err) {
                    console.error("Error parsing JSON file:", err);
                    alert("The dropped file does not contain valid JSON data");
                    fileContent = null;
                    fileName.classList.add("hidden");
                }
            };
            reader.onerror = () => {
                console.error("Error reading file");
                alert("Error reading file");
                fileContent = null;
                fileName.classList.add("hidden");
            };
            reader.readAsText(file);
        } else {
            alert("Please upload a file");
        }
    });
    
    // Analyze button click handler
    analyzeBtn.addEventListener("click", async () => {
        // Get the selected input method
        const inputMethod = document.querySelector('input[name="input-method"]:checked').value;
        
        let jsonContent;
        let jsonString;
        
        if (inputMethod === "paste") {
            if (!transcriptInput.value.trim()) {
                return alert("Please paste transcript JSON");
            }
            
            jsonString = transcriptInput.value.trim();
            try { 
                jsonContent = JSON.parse(jsonString); 
            } catch (e) { 
                console.error("JSON parse error:", e);
                return alert("Invalid JSON format: " + e.message); 
            }
        } else {
            if (!fileContent) {
                return alert("Please upload a JSON file");
            }
            
            jsonString = fileContent;
            try {
                jsonContent = JSON.parse(jsonString);
            } catch (e) {
                console.error("JSON file parse error:", e);
                return alert("Invalid JSON file format: " + e.message);
            }
        }

        // Log the JSON content for debugging
        console.log("JSON content type:", typeof jsonContent);
        console.log("JSON content is array:", Array.isArray(jsonContent));
        
        // Show loading overlay
        loadingOverlay.classList.remove("hidden");
        loadingOverlay.classList.add("flex");
        
        try {
            // Prepare the request body
            const requestBody = JSON.stringify({ transcript_data: jsonContent });
            console.log("Request body:", requestBody);
            
            // Make the API request
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: requestBody
            });
            
            // Check for non-OK response
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                console.error("API error response:", errorData);
                throw new Error(errorData.detail || "Analysis failed");
            }
            
            // Parse the response
            const result = await res.json();
            console.log("API success response:", result);
            
            // Show transcript analysis result cards
            analysisResults.classList.remove("hidden");
            
            const analysis = result.analysis;
            resultsContent.innerHTML = `
                <div class="space-y-4">
                    <div class="result-card p-4 rounded-lg bg-gradient-to-r from-blue-800 to-blue-900 border border-blue-700">
                        <h4 class="text-white font-semibold mb-2 flex items-center">
                            <i class="fas fa-newspaper mr-2"></i>Article Information
                        </h4>
                        <p class="text-blue-100">${analysis.article_url || 'N/A'}</p>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="result-card p-4 rounded-lg bg-gradient-to-r from-green-800 to-green-900 border border-green-700">
                            <h4 class="text-white font-semibold mb-2 flex items-center">
                                <i class="fas fa-user mr-2"></i>Agent 1
                            </h4>
                            <p class="text-green-100">Messages: ${analysis.agent_1_messages}</p>
                            <p class="text-green-100">Sentiment: ${analysis.agent_1_sentiment.overall_sentiment}</p>
                            <p class="text-green-100">Confidence: ${(analysis.agent_1_sentiment.confidence * 100).toFixed(1)}%</p>
                        </div>
                        <div class="result-card p-4 rounded-lg bg-gradient-to-r from-purple-800 to-purple-900 border border-purple-700">
                            <h4 class="text-white font-semibold mb-2 flex items-center">
                                <i class="fas fa-user mr-2"></i>Agent 2
                            </h4>
                            <p class="text-purple-100">Messages: ${analysis.agent_2_messages}</p>
                            <p class="text-purple-100">Sentiment: ${analysis.agent_2_sentiment.overall_sentiment}</p>
                            <p class="text-purple-100">Confidence: ${(analysis.agent_2_sentiment.confidence * 100).toFixed(1)}%</p>
                        </div>
                    </div>
                    <div class="result-card p-4 rounded-lg bg-gradient-to-r from-orange-800 to-orange-900 border border-orange-700">
                        <h4 class="text-white font-semibold mb-2 flex items-center">
                            <i class="fas fa-chart-line mr-2"></i>Analysis Summary
                        </h4>
                        <p class="text-orange-100">Total Messages: ${analysis.total_messages}</p>
                        <p class="text-orange-100">Analysis Confidence: ${(analysis.analysis_confidence * 100).toFixed(1)}%</p>
                    </div>
                </div>
            `;
            
            // Update the summary panel with transcript-specific data
            let sumHtml = '<div class="space-y-4">';
            
            // Transcript summary
            if (analysis.transcript_summary) {
                sumHtml += `
                    <div class="bg-gradient-to-r from-blue-800 to-purple-800 rounded-lg p-4 shadow-lg border border-blue-600">
                        <h4 class="text-white font-semibold mb-3 flex items-center">
                            <i class="fas fa-file-alt mr-2"></i>Transcript Summary
                        </h4>
                        <p class="text-gray-200 leading-relaxed">${analysis.transcript_summary}</p>
                    </div>
                `;
            }
            
            // Sentiment distribution from the actual transcript
            if (analysis.sentiment_distribution) {
                sumHtml += `
                    <div class="bg-gray-700 rounded-lg p-4 border border-gray-600">
                        <h4 class="text-white font-semibold mb-3 flex items-center">
                            <i class="fas fa-heart mr-2"></i>Sentiment Distribution
                        </h4>
                        <div class="space-y-2">
                            ${Object.entries(analysis.sentiment_distribution).map(([sentiment, count]) => {
                                const formattedSentiment = sentiment
                                    .split('_')
                                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                    .join(' ');
                                
                                // Add color coding for different sentiments
                                let colorClass = 'text-gray-300';
                                if (sentiment.includes('positive')) colorClass = 'text-green-400';
                                else if (sentiment.includes('negative')) colorClass = 'text-red-400';
                                else if (sentiment === 'neutral') colorClass = 'text-blue-400';
                                
                                return `
                                    <div class="flex justify-between items-center ${colorClass}">
                                        <span class="flex items-center">
                                            <i class="fas fa-circle text-xs mr-2"></i>
                                            ${formattedSentiment}
                                        </span>
                                        <span class="font-semibold">${count}</span>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            }
            
            sumHtml += '</div>';
            summaryContent.innerHTML = sumHtml;
        } catch (err) {
            console.error("Analysis error:", err);
            // Show error in the results area instead of an alert
            analysisResults.classList.remove("hidden");
            resultsContent.innerHTML = `
                <div class="bg-red-900 bg-opacity-50 p-4 rounded-lg border border-red-700">
                    <h4 class="text-white font-semibold mb-2">Error</h4>
                    <p class="text-red-300">${err.message}</p>
                    <div class="mt-4 p-3 bg-gray-800 rounded text-xs text-gray-400 overflow-auto max-h-40">
                        <p>If you're uploading a file, please ensure:</p>
                        <ul class="list-disc pl-5 mt-2">
                            <li>The file contains valid JSON data</li>
                            <li>The JSON structure matches the expected transcript format</li>
                            <li>The file is not too large (max 10MB)</li>
                        </ul>
                    </div>
                </div>
            `;
        } finally {
            loadingOverlay.classList.add("hidden");
            loadingOverlay.classList.remove("flex");
        }
    });

    if (token && user) {
        showDashboard();
    }
});
