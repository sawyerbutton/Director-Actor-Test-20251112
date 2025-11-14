/**
 * Upload page JavaScript
 * Handles file upload and analysis job submission
 * Supports both JSON and TXT file formats
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

    // File type radio buttons
    const fileTypeJSON = document.getElementById('fileTypeJSON');
    const fileTypeTXT = document.getElementById('fileTypeTXT');

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

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form values
        const provider = document.getElementById('provider').value;
        const model = document.getElementById('model').value;
        const exportMarkdown = document.getElementById('exportMarkdown').checked;
        const useLLMEnhancement = document.getElementById('useLLMEnhancement').checked;
        const fileType = document.querySelector('input[name="fileType"]:checked').value;

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
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>上传中...';

        try {
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);

            let endpoint, params;

            if (fileType === 'txt') {
                // TXT upload - goes to parse endpoint
                endpoint = '/api/parse-txt';
                params = new URLSearchParams({
                    provider: provider,
                    use_llm_enhancement: useLLMEnhancement
                });

                if (model) {
                    params.append('model', model);
                }

                // Upload and parse TXT file
                console.log('Uploading TXT file to:', `${endpoint}?${params}`);
                const response = await fetch(`${endpoint}?${params}`, {
                    method: 'POST',
                    body: formData
                });

                console.log('Upload response status:', response.status);
                const data = await response.json();
                console.log('Upload response data:', data);

                if (!response.ok) {
                    console.error('Upload failed with error:', data.detail);
                    throw new Error(data.detail || '上传失败');
                }

                // Redirect to parse preview page
                console.log('Redirecting to:', `/parse-preview/${data.job_id}`);
                window.location.href = `/parse-preview/${data.job_id}`;

            } else {
                // JSON upload - goes to analysis endpoint
                endpoint = '/api/upload';
                params = new URLSearchParams({
                    provider: provider,
                    export_markdown: exportMarkdown
                });

                if (model) {
                    params.append('model', model);
                }

                // Upload file
                const response = await fetch(`${endpoint}?${params}`, {
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
            console.error('Upload error (caught in catch block):', error);
            console.error('Error stack:', error.stack);
            showError(error.message || '上传失败，请重试');

            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
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
