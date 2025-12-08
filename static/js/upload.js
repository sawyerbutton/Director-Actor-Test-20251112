/**
 * Upload page JavaScript
 * Handles file upload and analysis job submission
 * Supports both JSON and TXT file formats
 * Enhanced with real-time progress tracking for TXT parsing
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const fileInput = document.getElementById('scriptFile');
    const fileLabel = document.getElementById('fileLabel');
    const hintText = document.getElementById('hintText');
    const llmEnhancementDiv = document.getElementById('llmEnhancementDiv');
    const providerSelect = document.getElementById('provider');
    const geminiModelDiv = document.getElementById('geminiModelDiv');
    const geminiModelSelect = document.getElementById('geminiModel');
    const providerHint = document.getElementById('providerHint');

    // Progress elements
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressStage = document.getElementById('progressStage');
    const progressMessage = document.getElementById('progressMessage');
    const progressSpinner = document.getElementById('progressSpinner');
    const sceneProgressSection = document.getElementById('sceneProgressSection');
    const sceneProgressList = document.getElementById('sceneProgressList');

    // Step indicators
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');

    // File type radio buttons
    const fileTypeJSON = document.getElementById('fileTypeJSON');
    const fileTypeTXT = document.getElementById('fileTypeTXT');

    // WebSocket connection
    let ws = null;
    let currentJobId = null;
    let pollingInterval = null;

    // Provider hint messages
    const providerHints = {
        'deepseek': 'DeepSeek 提供最佳性价比，响应快速',
        'anthropic': 'Claude 提供高质量分析，适合复杂场景',
        'openai': 'OpenAI GPT-4 系列，广泛适用',
        'gemini': 'Gemini 提供 64K 输出 + 1M 上下文，可选择不同模型版本'
    };

    // Handle provider change - show/hide Gemini model selector
    providerSelect.addEventListener('change', function() {
        const selectedProvider = this.value;

        // Update hint text
        if (providerHint && providerHints[selectedProvider]) {
            providerHint.textContent = providerHints[selectedProvider];
        }

        // Show/hide Gemini model selection
        if (geminiModelDiv) {
            if (selectedProvider === 'gemini') {
                geminiModelDiv.style.display = 'block';
            } else {
                geminiModelDiv.style.display = 'none';
            }
        }
    });

    // Handle file type change
    fileTypeJSON.addEventListener('change', function() {
        if (this.checked) {
            fileInput.setAttribute('accept', '.json');
            fileLabel.textContent = '选择剧本文件 (JSON 格式)';
            hintText.textContent = '支持的格式：JSON (符合 Script 数据模型)';
            llmEnhancementDiv.style.display = 'none';
            fileInput.value = ''; // Clear file selection
        }
    });

    fileTypeTXT.addEventListener('change', function() {
        if (this.checked) {
            fileInput.setAttribute('accept', '.txt');
            fileLabel.textContent = '选择剧本文件 (TXT 格式)';
            hintText.textContent = '支持的格式：TXT (纯文本剧本)';
            llmEnhancementDiv.style.display = 'block';
            fileInput.value = ''; // Clear file selection
        }
    });

    // ==================== Progress Display Functions ====================

    function showProgressSection() {
        progressSection.classList.remove('d-none');
        // Scroll to progress section
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideProgressSection() {
        progressSection.classList.add('d-none');
    }

    function updateProgress(percent, stage, message) {
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);

        if (stage) {
            progressStage.textContent = stage;
        }
        if (message) {
            progressMessage.textContent = message;
        }
    }

    function setStepStatus(stepElement, status) {
        // status: 'pending', 'active', 'completed'
        const icon = stepElement.querySelector('i');
        stepElement.classList.remove('text-muted', 'text-primary', 'text-success');

        if (status === 'pending') {
            stepElement.classList.add('text-muted');
            icon.className = 'bi bi-circle';
        } else if (status === 'active') {
            stepElement.classList.add('text-primary');
            icon.className = 'bi bi-arrow-right-circle-fill';
        } else if (status === 'completed') {
            stepElement.classList.add('text-success');
            icon.className = 'bi bi-check-circle-fill';
        }
    }

    function updateSceneProgress(currentScene, totalScenes, sceneName) {
        sceneProgressSection.classList.remove('d-none');

        // Build scene progress HTML
        let html = '';
        for (let i = 1; i <= totalScenes; i++) {
            const status = i < currentScene ? 'completed' : (i === currentScene ? 'active' : 'pending');
            const icon = status === 'completed' ? 'bi-check-circle-fill text-success' :
                        (status === 'active' ? 'bi-arrow-right-circle-fill text-primary' : 'bi-circle text-muted');
            const name = i === currentScene ? sceneName : `场景 ${i}`;
            html += `<span class="me-2"><i class="bi ${icon}"></i> ${name}</span>`;
        }
        sceneProgressList.innerHTML = html;
    }

    function showCompletionState(sceneCount, characterCount) {
        // Update progress bar to success state
        progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
        progressBar.classList.add('bg-success');
        updateProgress(100, '解析完成!', `成功解析 ${sceneCount} 个场景，${characterCount} 个角色`);

        // Hide spinner, show checkmark
        progressSpinner.classList.add('d-none');
        progressStage.innerHTML = '<i class="bi bi-check-circle-fill text-success me-2"></i>解析完成!';

        // Update all steps to completed
        setStepStatus(step1, 'completed');
        setStepStatus(step2, 'completed');
        setStepStatus(step3, 'completed');
        setStepStatus(step4, 'completed');
    }

    function showErrorState(errorMsg) {
        progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
        progressBar.classList.add('bg-danger');
        progressStage.innerHTML = '<i class="bi bi-x-circle-fill text-danger me-2"></i>解析失败';
        progressMessage.textContent = errorMsg;
        progressSpinner.classList.add('d-none');
    }

    // ==================== WebSocket Connection ====================

    function connectWebSocket(jobId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        // Handle VS Code port forwarding: if on port 8001, connect WebSocket to 8000
        let wsHost = window.location.host;
        if (wsHost.includes(':8001')) {
            wsHost = wsHost.replace(':8001', ':8000');
            console.log('[DEBUG] Detected port forwarding, redirecting WebSocket to:', wsHost);
        }

        const wsUrl = `${protocol}//${wsHost}/ws/progress/${jobId}`;

        console.log('Connecting to WebSocket:', wsUrl);
        ws = new WebSocket(wsUrl);

        ws.onopen = function() {
            console.log('WebSocket connected for job:', jobId);
            updateProgress(5, '已连接服务器', '正在等待解析开始...');
        };

        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            console.log('WebSocket message:', message);
            handleProgressMessage(message);
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            // Start polling as fallback
            startPolling(jobId);
        };

        ws.onclose = function() {
            console.log('WebSocket disconnected');
            // If not completed, start polling
            if (currentJobId) {
                startPolling(jobId);
            }
        };
    }

    function handleProgressMessage(message) {
        console.log('[DEBUG] handleProgressMessage called:', message.type, message);

        try {
        if (message.type === 'progress') {
            const progress = message.progress || 0;
            const stage = message.stage || 'parsing';
            const msg = message.message || '';

            // Update step indicators based on progress
            if (progress >= 5) {
                setStepStatus(step1, 'completed');
            }
            if (progress >= 15) {
                setStepStatus(step2, 'active');
            }
            if (progress >= 20) {
                setStepStatus(step2, 'completed');
                setStepStatus(step3, 'active');
            }
            if (progress >= 90) {
                setStepStatus(step3, 'completed');
                setStepStatus(step4, 'active');
            }

            // Update progress display
            let stageName = '解析中...';
            if (progress < 15) {
                stageName = '上传文件中...';
            } else if (progress < 20) {
                stageName = '解析基础结构...';
            } else if (progress < 90) {
                stageName = 'LLM 语义增强中...';

                // Try to extract scene info from message
                const sceneMatch = msg.match(/Enhancing scene (\w+)/i) ||
                                  msg.match(/增强场景 (\w+)/i) ||
                                  msg.match(/场景 (\d+)\/(\d+)/);
                if (sceneMatch) {
                    // Show scene-level progress
                    const currentScene = parseInt(msg.match(/(\d+)\/\d+/)?.[1] || '1');
                    const totalScenes = parseInt(msg.match(/\d+\/(\d+)/)?.[1] || '1');
                    if (currentScene && totalScenes) {
                        updateSceneProgress(currentScene, totalScenes, sceneMatch[1] || `场景 ${currentScene}`);
                    }
                }
            } else {
                stageName = '正在完成...';
            }

            updateProgress(progress, stageName, msg);

        } else if (message.type === 'complete') {
            const sceneCount = message.scene_count || 0;
            const characterCount = message.character_count || 0;

            showCompletionState(sceneCount, characterCount);

            // Stop polling if running
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }

            // Close WebSocket
            if (ws) {
                ws.close();
                ws = null;
            }

            // Redirect to preview page after a short delay
            setTimeout(() => {
                window.location.href = `/parse-preview/${currentJobId}`;
            }, 1500);

        } else if (message.type === 'error') {
            showErrorState(message.message || '解析失败');

            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始分析';

            // Stop polling
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }
        }
        } catch (error) {
            console.error('[DEBUG] Error in handleProgressMessage:', error);
            // Still try to redirect on complete even if UI update fails
            if (message.type === 'complete' && currentJobId) {
                console.log('[DEBUG] Forcing redirect despite error');
                window.location.href = `/parse-preview/${currentJobId}`;
            }
        }
    }

    // ==================== Helper: Get API Base URL ====================

    function getApiBaseUrl() {
        // Handle VS Code port forwarding: if on port 8001, API is on 8000
        let host = window.location.host;
        if (host.includes(':8001')) {
            host = host.replace(':8001', ':8000');
            console.log('[DEBUG] Detected port forwarding, redirecting API to:', host);
        }
        const protocol = window.location.protocol;
        return `${protocol}//${host}`;
    }

    // ==================== Polling Fallback ====================

    function startPolling(jobId) {
        if (pollingInterval) return; // Already polling

        console.log('[DEBUG] Starting polling for job:', jobId);
        const apiBaseUrl = getApiBaseUrl();
        let pollErrorCount = 0;
        const maxPollErrors = 60; // 60 errors * 500ms = 30 seconds max
        let isPollingActive = true;

        // Define the polling function
        const pollOnce = async () => {
            if (!isPollingActive) return;

            try {
                const apiUrl = `${apiBaseUrl}/api/parsed-script/${jobId}`;
                console.log('[DEBUG] Polling #' + (++pollErrorCount) + ' request:', apiUrl);
                pollErrorCount--; // Reset (we're reusing the counter briefly)

                const response = await fetch(apiUrl);
                console.log('[DEBUG] Response status:', response.status);

                // Handle 404 - job not found
                if (response.status === 404) {
                    console.error('[DEBUG] Job not found (404)');
                    pollErrorCount++;
                    if (pollErrorCount >= 10) {
                        isPollingActive = false;
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                        handleProgressMessage({
                            type: 'error',
                            message: '任务未找到，请返回首页重新上传'
                        });
                    }
                    return;
                }

                // Reset error count on successful response
                pollErrorCount = 0;

                const responseText = await response.text();
                console.log('[DEBUG] Response text length:', responseText.length);

                let data;
                try {
                    data = JSON.parse(responseText);
                } catch (parseError) {
                    console.error('[DEBUG] JSON parse error:', parseError.message);
                    console.error('[DEBUG] First 200 chars:', responseText.substring(0, 200));
                    return;
                }

                console.log('[DEBUG] Parsed response:', data.status, data.progress);

                if (data.status === 'complete') {
                    console.log('[DEBUG] *** COMPLETE DETECTED *** Stopping polling and redirecting...');
                    console.log('[DEBUG] Parsing complete! Processing result...');
                    isPollingActive = false;
                    clearInterval(pollingInterval);
                    pollingInterval = null;

                    // Calculate counts from script
                    const script = data.script;
                    const sceneCount = script.scenes ? script.scenes.length : 0;
                    const allCharacters = new Set();
                    if (script.scenes) {
                        script.scenes.forEach(scene => {
                            if (scene.characters) {
                                scene.characters.forEach(char => allCharacters.add(char));
                            }
                        });
                    }

                    console.log('[DEBUG] Calling handleProgressMessage with complete');
                    handleProgressMessage({
                        type: 'complete',
                        scene_count: sceneCount,
                        character_count: allCharacters.size
                    });

                } else if (data.status === 'parsing') {
                    const progress = data.progress || 10;
                    console.log('[DEBUG] Parsing in progress, progress =', progress);
                    handleProgressMessage({
                        type: 'progress',
                        progress: progress,
                        message: data.message || '解析中...'
                    });
                } else if (data.status === 'failed') {
                    console.log('[DEBUG] Parsing failed');
                    isPollingActive = false;
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    handleProgressMessage({
                        type: 'error',
                        message: data.error || '解析失败'
                    });
                } else {
                    console.log('[DEBUG] Unknown status:', data.status);
                }
            } catch (error) {
                console.error('[DEBUG] Polling error:', error);
                pollErrorCount++;
                if (pollErrorCount >= maxPollErrors) {
                    isPollingActive = false;
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    handleProgressMessage({
                        type: 'error',
                        message: '网络错误，请刷新页面重试'
                    });
                }
            }
        };

        // Poll immediately first (don't wait for interval)
        console.log('[DEBUG] Executing immediate first poll');
        pollOnce();

        // Then set up interval for subsequent polls (faster: 500ms)
        pollingInterval = setInterval(pollOnce, 500);
    }

    // ==================== Form Submission ====================

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form values
        const provider = document.getElementById('provider').value;
        let model = document.getElementById('model').value;
        const exportMarkdown = document.getElementById('exportMarkdown').checked;
        const useLLMEnhancement = document.getElementById('useLLMEnhancement').checked;
        const fileType = document.querySelector('input[name="fileType"]:checked').value;

        // If Gemini is selected and no custom model specified, use the Gemini model selector
        if (provider === 'gemini' && !model && geminiModelSelect) {
            model = geminiModelSelect.value;
            console.log('Using Gemini model:', model);
        }

        // Validate file
        if (!fileInput.files.length) {
            showError('请选择一个文件');
            return;
        }

        const file = fileInput.files[0];

        // Validate file type
        if (fileType === 'json' && !file.name.endsWith('.json')) {
            showError('请选择 JSON 格式的文件');
            return;
        }

        if (fileType === 'txt' && !file.name.endsWith('.txt')) {
            showError('请选择 TXT 格式的文件');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('文件大小不能超过 10MB');
            return;
        }

        // Hide error
        hideError();

        // Disable submit button
        submitBtn.disabled = true;

        try {
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);

            let endpoint, params;

            if (fileType === 'txt') {
                // ==================== TXT Upload with Progress ====================

                // Show progress section immediately
                showProgressSection();
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>上传中...';

                // Initialize progress display
                updateProgress(0, '正在上传文件...', `文件: ${file.name}`);
                setStepStatus(step1, 'active');
                setStepStatus(step2, 'pending');
                setStepStatus(step3, 'pending');
                setStepStatus(step4, 'pending');

                // Build endpoint
                endpoint = '/api/parse-txt';
                params = new URLSearchParams({
                    provider: provider,
                    use_llm_enhancement: useLLMEnhancement
                });

                if (model) {
                    params.append('model', model);
                }

                const apiBaseUrl = getApiBaseUrl();
                const fullUrl = `${apiBaseUrl}${endpoint}?${params}`;
                console.log('Uploading TXT file to:', fullUrl);

                // Upload file
                const response = await fetch(fullUrl, {
                    method: 'POST',
                    body: formData
                });

                console.log('[DEBUG] Response received, parsing JSON...');
                const data = await response.json();
                console.log('[DEBUG] Upload response:', data);

                if (!response.ok) {
                    throw new Error(data.detail || '上传失败');
                }

                if (!data.job_id) {
                    throw new Error('服务器响应缺少 job_id');
                }

                // Store job ID and connect WebSocket
                currentJobId = data.job_id;
                console.log('[DEBUG] New job ID:', currentJobId);

                // Stop any existing polling/WebSocket from previous jobs
                console.log('[DEBUG] Cleaning up previous connections...');
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                    pollingInterval = null;
                    console.log('[DEBUG] Cleared previous polling interval');
                }
                if (ws) {
                    ws.close();
                    ws = null;
                    console.log('[DEBUG] Closed previous WebSocket');
                }

                // Update progress - upload complete
                console.log('[DEBUG] Updating progress to 5%...');
                updateProgress(5, '文件上传完成', '正在连接服务器...');
                setStepStatus(step1, 'completed');

                // Update button
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>解析中...';

                // Connect WebSocket for real-time updates
                console.log('[DEBUG] Connecting WebSocket...');
                connectWebSocket(currentJobId);

                // Start polling immediately as backup (will complement WebSocket)
                // Polling is always safe because it just checks status
                console.log('[DEBUG] Starting polling for job:', currentJobId);
                startPolling(currentJobId);
                console.log('[DEBUG] Polling started, pollingInterval =', pollingInterval);

            } else {
                // ==================== JSON Upload (Original Flow) ====================

                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>上传中...';

                endpoint = '/api/upload';
                params = new URLSearchParams({
                    provider: provider,
                    export_markdown: exportMarkdown
                });

                if (model) {
                    params.append('model', model);
                }

                // Upload file with correct port handling
                const apiBaseUrl = getApiBaseUrl();
                const fullUrl = `${apiBaseUrl}${endpoint}?${params}`;
                console.log('Uploading JSON file to:', fullUrl);
                const response = await fetch(fullUrl, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || '上传失败');
                }

                // Redirect to analysis page
                window.location.href = `/analysis/${data.job_id}`;
            }

        } catch (error) {
            console.error('Upload error:', error);
            showError(error.message || '上传失败，请重试');

            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-play-circle"></i> 开始分析';

            // Hide progress section on error
            if (progressSection) {
                hideProgressSection();
            }
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
    }

    function hideError() {
        errorAlert.classList.add('d-none');
    }
});
