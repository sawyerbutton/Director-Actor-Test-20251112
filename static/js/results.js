/**
 * Results page JavaScript
 * Displays analysis results with interactive visualizations
 */

document.addEventListener('DOMContentLoaded', async function() {
    const jobId = document.getElementById('jobId').value;

    // Toggle raw data
    document.getElementById('toggleRawData').addEventListener('click', function() {
        const rawDataCard = document.getElementById('rawDataCard');
        rawDataCard.classList.toggle('d-none');
    });

    // Fetch and display results
    try {
        const response = await fetch(`/api/job/${jobId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }

        const job = await response.json();

        if (job.status !== 'completed') {
            showError('分析尚未完成');
            return;
        }

        const result = job.result;

        // Display results
        displaySummary(result);
        displayOverview(result);
        displayTCCs(result);
        displayRankings(result);
        displayModifications(result);
        displayMermaidDiagram(result);
        displayRawData(result);

    } catch (error) {
        console.error('Error loading results:', error);
        showError('加载结果失败: ' + error.message);
    }
});

function displaySummary(result) {
    // Update summary statistics
    const discoverer = result.discoverer_output;
    const auditor = result.auditor_output;

    if (discoverer && discoverer.tccs) {
        document.getElementById('tccCount').textContent = discoverer.tccs.length;
    }

    if (auditor && auditor.rankings) {
        const rankings = auditor.rankings;
        document.getElementById('aLineCount').textContent = rankings.a_line ? 1 : 0;
        document.getElementById('bLineCount').textContent = rankings.b_lines ? rankings.b_lines.length : 0;
        document.getElementById('cLineCount').textContent = rankings.c_lines ? rankings.c_lines.length : 0;
    }
}

function displayOverview(result) {
    const overviewContent = document.getElementById('overviewContent');
    const discoverer = result.discoverer_output;
    const auditor = result.auditor_output;
    const modifier = result.modifier_output;

    let html = '<div class="row">';

    // Stage 1 Summary
    html += '<div class="col-md-4 mb-3">';
    html += '<div class="card h-100">';
    html += '<div class="card-body">';
    html += '<h6 class="card-title text-primary"><i class="bi bi-search"></i> 阶段 1: 发现</h6>';
    if (discoverer && discoverer.tccs) {
        html += `<p>识别了 <strong>${discoverer.tccs.length}</strong> 个戏剧冲突链（TCC）</p>`;
        const avgConfidence = discoverer.tccs.reduce((sum, tcc) => sum + tcc.confidence, 0) / discoverer.tccs.length;
        html += `<p class="small text-muted">平均置信度: ${(avgConfidence * 100).toFixed(1)}%</p>`;
    } else {
        html += '<p class="text-muted">无数据</p>';
    }
    html += '</div></div></div>';

    // Stage 2 Summary
    html += '<div class="col-md-4 mb-3">';
    html += '<div class="card h-100">';
    html += '<div class="card-body">';
    html += '<h6 class="card-title text-success"><i class="bi bi-bar-chart"></i> 阶段 2: 审计</h6>';
    if (auditor && auditor.rankings) {
        const rankings = auditor.rankings;
        html += '<ul class="list-unstyled mb-0">';
        html += `<li><strong>A 线:</strong> ${rankings.a_line.tcc_id}</li>`;
        html += `<li><strong>B 线:</strong> ${rankings.b_lines.length} 条</li>`;
        html += `<li><strong>C 线:</strong> ${rankings.c_lines.length} 条</li>`;
        html += '</ul>';
    } else {
        html += '<p class="text-muted">无数据</p>';
    }
    html += '</div></div></div>';

    // Stage 3 Summary
    html += '<div class="col-md-4 mb-3">';
    html += '<div class="card h-100">';
    html += '<div class="card-body">';
    html += '<h6 class="card-title text-warning"><i class="bi bi-wrench"></i> 阶段 3: 修正</h6>';
    if (modifier && modifier.validation) {
        const validation = modifier.validation;
        html += `<p>发现 <strong>${validation.total_issues}</strong> 个问题</p>`;
        html += `<p class="mb-0">`;
        html += `<span class="badge bg-success">${validation.fixed} 已修复</span> `;
        html += `<span class="badge bg-secondary">${validation.skipped} 已跳过</span>`;
        html += `</p>`;
    } else {
        html += '<p class="text-muted">无数据</p>';
    }
    html += '</div></div></div>';

    html += '</div>';

    // Performance metrics
    if (result.metrics) {
        html += '<hr><h6 class="mt-3"><i class="bi bi-speedometer2"></i> 性能指标</h6>';
        html += '<div class="row">';
        if (result.metrics.total_duration_seconds) {
            html += `<div class="col-md-3 mb-2"><small class="text-muted">总耗时:</small><br><strong>${result.metrics.total_duration_seconds.toFixed(2)}s</strong></div>`;
        }
        if (result.metrics.total_tokens) {
            html += `<div class="col-md-3 mb-2"><small class="text-muted">总 Token:</small><br><strong>${result.metrics.total_tokens.toLocaleString()}</strong></div>`;
        }
        if (result.metrics.estimated_cost_usd) {
            html += `<div class="col-md-3 mb-2"><small class="text-muted">预估成本:</small><br><strong>$${result.metrics.estimated_cost_usd.toFixed(4)}</strong></div>`;
        }
        html += '</div>';
    }

    overviewContent.innerHTML = html;
}

function displayTCCs(result) {
    const tccList = document.getElementById('tccList');
    const discoverer = result.discoverer_output;

    if (!discoverer || !discoverer.tccs || discoverer.tccs.length === 0) {
        tccList.innerHTML = '<p class="text-muted">未发现 TCC</p>';
        return;
    }

    let html = '<div class="accordion" id="tccAccordion">';

    discoverer.tccs.forEach((tcc, index) => {
        const collapseId = `collapse${index}`;
        const headingId = `heading${index}`;

        html += `<div class="accordion-item">`;
        html += `<h2 class="accordion-header" id="${headingId}">`;
        html += `<button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}">`;
        html += `<strong class="me-2">${tcc.tcc_id}</strong>`;
        html += `<span class="badge bg-primary me-2">${(tcc.confidence * 100).toFixed(0)}%</span>`;
        html += `<span class="text-truncate">${tcc.super_objective.substring(0, 80)}...</span>`;
        html += `</button></h2>`;

        html += `<div id="${collapseId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" data-bs-parent="#tccAccordion">`;
        html += `<div class="accordion-body">`;

        // Super Objective
        html += `<div class="mb-3">`;
        html += `<h6 class="text-primary">超级目标</h6>`;
        html += `<p>${tcc.super_objective}</p>`;
        html += `</div>`;

        // Forces
        if (tcc.forces && tcc.forces.length > 0) {
            html += `<div class="mb-3">`;
            html += `<h6 class="text-success">力量</h6>`;
            html += `<ul>`;
            tcc.forces.forEach(force => {
                html += `<li>${force}</li>`;
            });
            html += `</ul></div>`;
        }

        // Evidence
        if (tcc.evidence && tcc.evidence.length > 0) {
            html += `<div class="mb-3">`;
            html += `<h6 class="text-info">证据场景</h6>`;
            html += `<p class="mb-0">`;
            tcc.evidence.forEach(sceneId => {
                html += `<span class="badge bg-info me-1">${sceneId}</span>`;
            });
            html += `</p></div>`;
        }

        html += `</div></div></div>`;
    });

    html += '</div>';
    tccList.innerHTML = html;
}

function displayRankings(result) {
    const rankingsContent = document.getElementById('rankingsContent');
    const auditor = result.auditor_output;

    if (!auditor || !auditor.rankings) {
        rankingsContent.innerHTML = '<p class="text-muted">无排序数据</p>';
        return;
    }

    const rankings = auditor.rankings;
    let html = '';

    // A-line
    html += '<div class="card mb-3 border-warning">';
    html += '<div class="card-header bg-warning text-dark">';
    html += '<h5 class="mb-0"><i class="bi bi-star-fill"></i> A 线（主线）</h5>';
    html += '</div><div class="card-body">';
    if (rankings.a_line) {
        html += formatRankingCard(rankings.a_line);
    }
    html += '</div></div>';

    // B-lines
    if (rankings.b_lines && rankings.b_lines.length > 0) {
        html += '<div class="card mb-3 border-info">';
        html += '<div class="card-header bg-info text-white">';
        html += `<h5 class="mb-0"><i class="bi bi-star-half"></i> B 线（副线） - ${rankings.b_lines.length} 条</h5>`;
        html += '</div><div class="card-body">';
        rankings.b_lines.forEach(line => {
            html += formatRankingCard(line);
            html += '<hr>';
        });
        html += '</div></div>';
    }

    // C-lines
    if (rankings.c_lines && rankings.c_lines.length > 0) {
        html += '<div class="card mb-3 border-secondary">';
        html += '<div class="card-header bg-secondary text-white">';
        html += `<h5 class="mb-0"><i class="bi bi-star"></i> C 线（点缀） - ${rankings.c_lines.length} 条</h5>`;
        html += '</div><div class="card-body">';
        rankings.c_lines.forEach(line => {
            html += formatRankingCard(line);
            html += '<hr>';
        });
        html += '</div></div>';
    }

    rankingsContent.innerHTML = html;
}

function formatRankingCard(line) {
    let html = `<div class="mb-2">`;
    html += `<h6>${line.tcc_id}</h6>`;
    html += `<div class="row">`;
    html += `<div class="col-md-4"><small class="text-muted">Spine Score:</small> <strong>${line.spine_score.toFixed(1)}</strong></div>`;
    html += `<div class="col-md-4"><small class="text-muted">Density:</small> <strong>${line.density_score.toFixed(1)}</strong></div>`;
    html += `<div class="col-md-4"><small class="text-muted">Coherence:</small> <strong>${line.coherence_score.toFixed(1)}</strong></div>`;
    html += `</div>`;
    if (line.rationale) {
        html += `<p class="small text-muted mt-2 mb-0">${line.rationale}</p>`;
    }
    html += `</div>`;
    return html;
}

function displayModifications(result) {
    const modificationsContent = document.getElementById('modificationsContent');
    const modifier = result.modifier_output;

    if (!modifier || !modifier.modification_log || modifier.modification_log.length === 0) {
        modificationsContent.innerHTML = '<div class="alert alert-success"><i class="bi bi-check-circle"></i> 未发现需要修正的问题</div>';
        return;
    }

    let html = '';

    modifier.modification_log.forEach((mod, index) => {
        const badgeClass = mod.status === 'fixed' ? 'bg-success' : 'bg-secondary';
        const icon = mod.status === 'fixed' ? 'check-circle' : 'x-circle';

        html += `<div class="card mb-3">`;
        html += `<div class="card-body">`;
        html += `<div class="d-flex justify-content-between align-items-start mb-2">`;
        html += `<h6 class="mb-0">#${index + 1} ${mod.tcc_id} - ${mod.scene_id || 'N/A'}</h6>`;
        html += `<span class="badge ${badgeClass}"><i class="bi bi-${icon}"></i> ${mod.status}</span>`;
        html += `</div>`;
        html += `<p class="mb-2"><strong>类型:</strong> ${mod.change_type}</p>`;
        html += `<p class="mb-0"><strong>理由:</strong> ${mod.rationale}</p>`;
        html += `</div></div>`;
    });

    modificationsContent.innerHTML = html;
}

function displayMermaidDiagram(result) {
    const discoverer = result.discoverer_output;
    const auditor = result.auditor_output;

    if (!discoverer || !auditor) {
        return;
    }

    // Generate simple Mermaid diagram
    let diagram = 'graph LR\n';

    // Add A-line
    if (auditor.rankings && auditor.rankings.a_line) {
        const aLine = auditor.rankings.a_line;
        diagram += `    ${aLine.tcc_id}[${aLine.tcc_id}]:::aline\n`;
    }

    // Add B-lines
    if (auditor.rankings && auditor.rankings.b_lines) {
        auditor.rankings.b_lines.forEach(line => {
            diagram += `    ${line.tcc_id}[${line.tcc_id}]:::bline\n`;
        });
    }

    // Add C-lines
    if (auditor.rankings && auditor.rankings.c_lines) {
        auditor.rankings.c_lines.forEach(line => {
            diagram += `    ${line.tcc_id}[${line.tcc_id}]:::cline\n`;
        });
    }

    // Add styles
    diagram += '\n    classDef aline fill:#ffc107,stroke:#ff9800,stroke-width:3px\n';
    diagram += '    classDef bline fill:#17a2b8,stroke:#138496,stroke-width:2px\n';
    diagram += '    classDef cline fill:#6c757d,stroke:#495057,stroke-width:1px\n';

    document.getElementById('mermaidDiagram').textContent = diagram;

    // Re-initialize Mermaid
    if (window.mermaid) {
        mermaid.init(undefined, document.getElementById('mermaidDiagram'));
    }
}

function displayRawData(result) {
    const rawDataCode = document.getElementById('rawDataCode');
    rawDataCode.textContent = JSON.stringify(result, null, 2);
}

function showError(message) {
    document.querySelector('.col-12').innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle"></i>
            <strong>错误:</strong> ${message}
            <hr>
            <a href="/" class="btn btn-outline-danger">返回首页</a>
        </div>
    `;
}
