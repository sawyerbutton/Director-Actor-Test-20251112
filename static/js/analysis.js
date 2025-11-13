/**
 * Analysis page JavaScript
 * Handles real-time progress updates via WebSocket
 */

document.addEventListener('DOMContentLoaded', function() {
    const jobId = document.getElementById('jobId').value;
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const currentStage = document.getElementById('currentStage');

    // Stage icons
    const stageIcons = {
        stage1: document.getElementById('stage1-icon'),
        stage2: document.getElementById('stage2-icon'),
        stage3: document.getElementById('stage3-icon'),
        export: document.getElementById('export-icon')
    };

    // Stage items
    const stageItems = {
        stage1: document.getElementById('stage1-item'),
        stage2: document.getElementById('stage2-item'),
        stage3: document.getElementById('stage3-item'),
        export: document.getElementById('export-item')
    };

    // Connect to WebSocket
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/progress/${jobId}`;

    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = function() {
        console.log('WebSocket connected');
    };

    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        console.log('WebSocket message:', message);

        if (message.type === 'progress') {
            updateProgress(message);
        } else if (message.type === 'complete') {
            handleComplete(message);
        } else if (message.type === 'error') {
            handleError(message);
        } else if (message.type === 'status') {
            // Initial status update
            if (message.data.status === 'running') {
                updateProgress({
                    progress: message.data.progress,
                    stage: message.data.stage,
                    message: '分析进行中...'
                });
            }
        }

        // Send ping to keep connection alive
        ws.send('ping');
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        showError('WebSocket 连接错误，请刷新页面重试');
    };

    ws.onclose = function() {
        console.log('WebSocket closed');
    };

    function updateProgress(data) {
        // Update progress bar
        const progress = data.progress || 0;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressPercent.textContent = `${progress}%`;

        // Update stage message
        currentStage.textContent = data.message || '处理中...';

        // Update stage icons
        const stage = data.stage;
        if (stage === 'stage1') {
            setStageStatus('stage1', 'active');
        } else if (stage === 'stage2') {
            setStageStatus('stage1', 'complete');
            setStageStatus('stage2', 'active');
        } else if (stage === 'stage3') {
            setStageStatus('stage1', 'complete');
            setStageStatus('stage2', 'complete');
            setStageStatus('stage3', 'active');
        } else if (stage === 'export') {
            setStageStatus('stage1', 'complete');
            setStageStatus('stage2', 'complete');
            setStageStatus('stage3', 'complete');
            setStageStatus('export', 'active');
        }
    }

    function setStageStatus(stage, status) {
        const icon = stageIcons[stage];
        const item = stageItems[stage];

        if (!icon || !item) return;

        if (status === 'active') {
            icon.className = 'bi bi-hourglass-split me-3 text-primary';
            item.classList.add('active');
        } else if (status === 'complete') {
            icon.className = 'bi bi-check-circle-fill me-3 text-success';
            item.classList.remove('active');
        }
    }

    function handleComplete(data) {
        // Update to 100%
        progressBar.style.width = '100%';
        progressBar.setAttribute('aria-valuenow', 100);
        progressPercent.textContent = '100%';
        currentStage.textContent = data.message || '分析完成！';

        // Mark all stages complete
        setStageStatus('stage1', 'complete');
        setStageStatus('stage2', 'complete');
        setStageStatus('stage3', 'complete');
        setStageStatus('export', 'complete');

        // Change progress bar color
        progressBar.classList.remove('progress-bar-animated', 'progress-bar-striped');
        progressBar.classList.add('bg-success');

        // Redirect to results after 2 seconds
        setTimeout(() => {
            window.location.href = data.result_url || `/results/${jobId}`;
        }, 2000);
    }

    function handleError(data) {
        showError(data.message || '分析失败');
        progressBar.classList.remove('progress-bar-animated');
        progressBar.classList.add('bg-danger');
    }

    function showError(message) {
        const alertHtml = `
            <div class="alert alert-danger mt-4" role="alert">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>错误:</strong> ${message}
                <hr>
                <a href="/" class="btn btn-sm btn-outline-danger">返回首页</a>
            </div>
        `;
        document.querySelector('.col-md-8').insertAdjacentHTML('beforeend', alertHtml);
    }
});
