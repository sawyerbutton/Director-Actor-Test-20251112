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
        displayFullReport(result);  // New: Full report tab
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

function displayFullReport(result) {
    const fullReportContent = document.getElementById('fullReportContent');
    const discoverer = result.discoverer_output;
    const auditor = result.auditor_output;
    const modifier = result.modifier_output;

    let html = '';

    // ===== 基本信息 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-info-circle text-primary"></i> 基本信息</h4>';
    html += '<div class="row">';
    html += '<div class="col-md-6"><p><strong>分析时间:</strong> ' + new Date().toLocaleString('zh-CN') + '</p></div>';
    html += '<div class="col-md-6"><p><strong>系统版本:</strong> v2.10.0</p></div>';
    html += '</div></div>';

    // ===== 执行概况 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-speedometer2 text-success"></i> 执行概况</h4>';
    html += '<table class="table table-sm table-bordered">';
    html += '<tbody>';
    if (result.metrics) {
        if (result.metrics.total_duration_seconds) {
            html += `<tr><td>总执行时间</td><td><strong>${result.metrics.total_duration_seconds.toFixed(2)} 秒</strong></td></tr>`;
        }
        if (result.metrics.total_tokens) {
            html += `<tr><td>总 Token 数</td><td><strong>${result.metrics.total_tokens.toLocaleString()}</strong></td></tr>`;
        }
    }
    html += `<tr><td>识别的 TCC 数</td><td><strong>${discoverer?.tccs?.length || 0}</strong></td></tr>`;
    html += `<tr><td>发现的问题数</td><td><strong>${modifier?.validation?.total_issues || 0}</strong></td></tr>`;
    html += '</tbody></table></div>';

    // ===== 阶段1: TCC 识别 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-search text-primary"></i> 阶段一：戏剧冲突链（TCC）识别</h4>';

    if (discoverer && discoverer.tccs && discoverer.tccs.length > 0) {
        const avgConfidence = discoverer.tccs.reduce((sum, tcc) => sum + tcc.confidence, 0) / discoverer.tccs.length;
        html += `<p>共识别出 <strong>${discoverer.tccs.length}</strong> 个独立的戏剧冲突链，平均置信度 <strong>${(avgConfidence * 100).toFixed(1)}%</strong></p>`;

        discoverer.tccs.forEach((tcc, index) => {
            html += `<div class="card mb-3 border-start border-4 ${index === 0 ? 'border-warning' : 'border-info'}">`;
            html += `<div class="card-body">`;
            html += `<h5 class="card-title">${tcc.tcc_id} <span class="badge ${tcc.confidence >= 0.9 ? 'bg-success' : tcc.confidence >= 0.7 ? 'bg-warning' : 'bg-danger'}">${(tcc.confidence * 100).toFixed(0)}%</span></h5>`;
            html += `<h6 class="card-subtitle mb-2 text-muted">超级目标</h6>`;
            html += `<p>${tcc.super_objective}</p>`;

            // 冲突类型
            if (tcc.core_conflict_type) {
                html += `<p><strong>核心冲突类型:</strong> ${tcc.core_conflict_type}</p>`;
            }

            // Forces/驱动力
            if (tcc.forces && tcc.forces.length > 0) {
                html += `<p><strong>力量:</strong></p><ul>`;
                tcc.forces.forEach(f => html += `<li>${f}</li>`);
                html += `</ul>`;
            }

            // Evidence scenes
            if (tcc.evidence && tcc.evidence.length > 0) {
                html += `<p><strong>证据场景:</strong> `;
                tcc.evidence.forEach(e => html += `<span class="badge bg-secondary me-1">${e}</span>`);
                html += `</p>`;
            }

            html += `</div></div>`;
        });
    } else {
        html += '<p class="text-muted">未识别到 TCC</p>';
    }
    html += '</div>';

    // ===== 阶段2: A/B/C 线分级 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-bar-chart text-success"></i> 阶段二：A/B/C 线分级</h4>';

    if (auditor && auditor.rankings) {
        const rankings = auditor.rankings;

        // A-line
        html += '<div class="mb-3">';
        html += '<h5><span class="badge bg-warning text-dark">A 线（主线 / Spine）</span></h5>';
        if (rankings.a_line) {
            html += `<p><strong>${rankings.a_line.tcc_id}:</strong> ${rankings.a_line.super_objective || '未指定'}</p>`;
            html += `<ul>`;
            html += `<li><strong>Spine 评分:</strong> ${rankings.a_line.spine_score?.toFixed(1) || 'N/A'} / 10</li>`;
            if (rankings.a_line.reasoning) {
                html += `<li><strong>场景数:</strong> ${rankings.a_line.reasoning.scene_count || 'N/A'}</li>`;
            }
            html += `</ul>`;
            if (rankings.a_line.reasoning?.reasoning) {
                html += `<p><strong>评估理由:</strong> ${rankings.a_line.reasoning.reasoning}</p>`;
            }
        }
        html += '</div>';

        // B-lines
        html += '<div class="mb-3">';
        html += '<h5><span class="badge bg-info">B 线（副线 / Heart）</span></h5>';
        if (rankings.b_lines && rankings.b_lines.length > 0) {
            rankings.b_lines.forEach(line => {
                html += `<p><strong>${line.tcc_id}:</strong> ${line.super_objective || '未指定'}</p>`;
                html += `<ul>`;
                html += `<li><strong>Heart 评分:</strong> ${line.heart_score?.toFixed(1) || 'N/A'} / 10</li>`;
                html += `</ul>`;
            });
        } else {
            html += '<p class="text-muted">未识别到 B 线</p>';
        }
        html += '</div>';

        // C-lines
        html += '<div class="mb-3">';
        html += '<h5><span class="badge bg-secondary">C 线（次线 / Flavor）</span></h5>';
        if (rankings.c_lines && rankings.c_lines.length > 0) {
            rankings.c_lines.forEach(line => {
                html += `<p><strong>${line.tcc_id}:</strong> ${line.super_objective || '未指定'}</p>`;
                html += `<ul>`;
                html += `<li><strong>Flavor 评分:</strong> ${line.flavor_score?.toFixed(1) || 'N/A'} / 10</li>`;
                html += `</ul>`;
            });
        } else {
            html += '<p class="text-muted">未识别到 C 线</p>';
        }
        html += '</div>';
    } else {
        html += '<p class="text-muted">无排序数据</p>';
    }
    html += '</div>';

    // ===== 阶段3: 结构修正 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-wrench text-warning"></i> 阶段三：结构修正</h4>';

    if (modifier && modifier.validation) {
        const validation = modifier.validation;
        html += '<div class="row mb-3">';
        html += `<div class="col-md-4"><div class="card text-center"><div class="card-body"><h3>${validation.total_issues}</h3><small>发现问题</small></div></div></div>`;
        html += `<div class="col-md-4"><div class="card text-center bg-success text-white"><div class="card-body"><h3>${validation.fixed}</h3><small>已修复</small></div></div></div>`;
        html += `<div class="col-md-4"><div class="card text-center bg-secondary text-white"><div class="card-body"><h3>${validation.skipped}</h3><small>已跳过</small></div></div></div>`;
        html += '</div>';

        if (modifier.modification_log && modifier.modification_log.length > 0) {
            html += '<h6>修正详情:</h6>';
            html += '<table class="table table-sm">';
            html += '<thead><tr><th>#</th><th>问题ID</th><th>场景</th><th>操作</th><th>状态</th></tr></thead>';
            html += '<tbody>';
            modifier.modification_log.forEach((mod, index) => {
                const statusBadge = mod.applied
                    ? '<span class="badge bg-success">已应用</span>'
                    : '<span class="badge bg-secondary">已跳过</span>';
                html += `<tr>`;
                html += `<td>${index + 1}</td>`;
                html += `<td>${mod.issue_id}</td>`;
                html += `<td>${mod.scene_id || 'N/A'}</td>`;
                html += `<td>${mod.change_type || 'N/A'}</td>`;
                html += `<td>${statusBadge}</td>`;
                html += `</tr>`;
            });
            html += '</tbody></table>';
        }
    } else {
        html += '<div class="alert alert-success"><i class="bi bi-check-circle"></i> 未发现需要修正的结构性问题</div>';
    }
    html += '</div>';

    // ===== 关键发现 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-lightbulb text-info"></i> 关键发现</h4>';
    html += '<ul class="list-group list-group-flush">';

    // 自动生成关键发现
    const findings = generateKeyFindings(discoverer, auditor, modifier);
    findings.forEach(finding => {
        html += `<li class="list-group-item"><i class="bi bi-check2-circle text-success me-2"></i>${finding}</li>`;
    });
    html += '</ul></div>';

    // ===== 建议 =====
    html += '<div class="report-section mb-4">';
    html += '<h4 class="border-bottom pb-2 mb-3"><i class="bi bi-flag text-danger"></i> 建议</h4>';
    html += '<ul class="list-group list-group-flush">';

    // 自动生成建议
    const recommendations = generateRecommendations(discoverer, auditor, modifier);
    recommendations.forEach(rec => {
        html += `<li class="list-group-item"><i class="bi bi-arrow-right-circle text-primary me-2"></i>${rec}</li>`;
    });
    html += '</ul></div>';

    // Footer
    html += '<hr><p class="text-muted text-center small">本报告由 AI 自动生成，建议结合人工审核使用</p>';

    fullReportContent.innerHTML = html;
}

function generateKeyFindings(discoverer, auditor, modifier) {
    const findings = [];

    // TCC 数量分析
    const tccCount = discoverer?.tccs?.length || 0;
    if (tccCount === 1) {
        findings.push('剧本为单线叙事，结构简洁清晰');
    } else if (tccCount === 2) {
        findings.push('剧本采用双线叙事，主副线并行发展');
    } else if (tccCount >= 3) {
        findings.push(`剧本为多线叙事（${tccCount}条线），结构复杂度较高`);
    }

    // 线级分布
    if (auditor?.rankings) {
        if (auditor.rankings.a_line) {
            const objective = auditor.rankings.a_line.super_objective || '';
            findings.push(`主线（A线）明确：${objective.substring(0, 40)}...`);
        }

        const bCount = auditor.rankings.b_lines?.length || 0;
        if (bCount > 0) {
            findings.push(`副线（B线）数量: ${bCount}条，提供情感深度`);
        }

        const cCount = auditor.rankings.c_lines?.length || 0;
        if (cCount > 0) {
            findings.push(`次线（C线）数量: ${cCount}条，增加叙事层次`);
        }
    }

    // 修正情况
    const totalIssues = modifier?.validation?.total_issues || 0;
    if (totalIssues === 0) {
        findings.push('剧本结构完整，未发现需修正的结构性问题');
    } else {
        const fixed = modifier?.validation?.fixed || 0;
        findings.push(`发现${totalIssues}个结构性问题，已修复${fixed}个`);
    }

    return findings;
}

function generateRecommendations(discoverer, auditor, modifier) {
    const recommendations = [];

    // 检查 B 线
    if (auditor?.rankings?.a_line) {
        const bCount = auditor.rankings.b_lines?.length || 0;
        if (bCount === 0) {
            recommendations.push('考虑增加B线（副线），为主线提供情感深度和人物内部冲突');
        }
    }

    // 检查低置信度 TCC
    const lowConfidenceTccs = discoverer?.tccs?.filter(tcc => tcc.confidence < 0.7) || [];
    if (lowConfidenceTccs.length > 0) {
        const ids = lowConfidenceTccs.map(t => t.tcc_id).join(', ');
        recommendations.push(`部分TCC置信度较低（<70%），建议审核以下TCC的独立性: ${ids}`);
    }

    // 检查问题数量
    const totalIssues = modifier?.validation?.total_issues || 0;
    if (totalIssues > 5) {
        recommendations.push('结构性问题较多，建议重点检查场景的setup-payoff因果链完整性');
    }

    // 默认建议
    if (recommendations.length === 0) {
        recommendations.push('剧本结构良好，建议维持当前设计');
        recommendations.push('可考虑进一步深化角色冲突和情感弧线');
    }

    return recommendations;
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
    html += `<h6>${line.tcc_id} - ${line.super_objective || 'Unknown'}</h6>`;
    html += `<div class="row">`;
    html += `<div class="col-md-4"><small class="text-muted">Spine Score:</small> <strong>${line.spine_score ? line.spine_score.toFixed(1) : 'N/A'}</strong></div>`;

    // Get density from reasoning.setup_payoff_density if available
    const density = line.reasoning?.setup_payoff_density;
    html += `<div class="col-md-4"><small class="text-muted">Setup-Payoff Density:</small> <strong>${density !== undefined ? density.toFixed(2) : 'N/A'}</strong></div>`;

    // Get scene count from reasoning
    const sceneCount = line.reasoning?.scene_count;
    html += `<div class="col-md-4"><small class="text-muted">Scene Count:</small> <strong>${sceneCount || 'N/A'}</strong></div>`;
    html += `</div>`;

    // Display forces if available
    if (line.forces) {
        html += `<div class="mt-2 small">`;
        html += `<strong>Forces:</strong><br>`;
        if (line.forces.protagonist) html += `<span class="text-muted">Protagonist:</span> ${line.forces.protagonist}<br>`;
        if (line.forces.primary_antagonist) html += `<span class="text-muted">Antagonist:</span> ${line.forces.primary_antagonist}`;
        html += `</div>`;
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
        const badgeClass = mod.applied ? 'bg-success' : 'bg-secondary';
        const icon = mod.applied ? 'check-circle' : 'x-circle';
        const statusText = mod.applied ? '已应用' : '已跳过';

        // Generate meaningful description for applied modifications
        let description = '';
        if (mod.applied) {
            const changeTypeMap = {
                'add': '添加',
                'append': '追加',
                'update': '更新',
                'remove': '移除',
                'delete': '删除'
            };
            const actionText = changeTypeMap[mod.change_type] || mod.change_type || '修改';
            const fieldText = mod.field || '字段';
            description = `${actionText}了 ${fieldText}`;
            if (mod.new_value) {
                const valueStr = typeof mod.new_value === 'object'
                    ? JSON.stringify(mod.new_value).substring(0, 50)
                    : String(mod.new_value).substring(0, 50);
                description += `: ${valueStr}`;
            }
        } else {
            description = mod.reason || '未知原因';
        }

        html += `<div class="card mb-3">`;
        html += `<div class="card-body">`;
        html += `<div class="d-flex justify-content-between align-items-start mb-2">`;
        html += `<h6 class="mb-0">#${index + 1} ${mod.issue_id} - ${mod.scene_id || 'N/A'}</h6>`;
        html += `<span class="badge ${badgeClass}"><i class="bi bi-${icon}"></i> ${statusText}</span>`;
        html += `</div>`;
        html += `<p class="mb-2"><strong>操作:</strong> ${mod.change_type || 'N/A'}</p>`;
        html += `<p class="mb-0"><strong>详情:</strong> ${description}</p>`;
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

    const diagramElement = document.getElementById('mermaidDiagram');
    const tccs = discoverer.tccs || [];
    const rankings = auditor.rankings;

    if (tccs.length === 0) {
        diagramElement.innerHTML = '<div class="alert alert-info">没有TCC数据可供可视化</div>';
        return;
    }

    // Build TCC info map for easy access
    const tccMap = {};
    tccs.forEach(tcc => {
        tccMap[tcc.tcc_id] = tcc;
    });

    // Build line type map (A/B/C)
    const lineTypeMap = {};
    if (rankings) {
        if (rankings.a_line) lineTypeMap[rankings.a_line.tcc_id] = 'A';
        (rankings.b_lines || []).forEach(line => lineTypeMap[line.tcc_id] = 'B');
        (rankings.c_lines || []).forEach(line => lineTypeMap[line.tcc_id] = 'C');
    }

    // Generate Mermaid diagram
    let diagram = 'flowchart TD\n';
    diagram += '    %% TCC 关系图 - 自动生成\n\n';

    // Add nodes with rich info
    diagram += '    %% === TCC 节点 ===\n';
    tccs.forEach(tcc => {
        const lineType = lineTypeMap[tcc.tcc_id] || '';
        const lineLabel = lineType ? `【${lineType}线】` : '';
        const objective = truncateText(tcc.super_objective || '未知目标', 25);
        const confidence = ((tcc.confidence || 0) * 100).toFixed(0);

        // Create rich node label
        const label = `${lineLabel}${tcc.tcc_id}<br/>${objective}<br/>置信度: ${confidence}%`;
        diagram += `    ${tcc.tcc_id}["${label}"]\n`;
    });
    diagram += '\n';

    // === 关键：添加 TCC 之间的关系连接 ===
    diagram += '    %% === TCC 关系连接 ===\n';

    // 1. 基于证据场景重叠建立关系
    const sceneToTccs = {};
    tccs.forEach(tcc => {
        const scenes = tcc.evidence_scenes || tcc.evidence || [];
        scenes.forEach(sceneId => {
            if (!sceneToTccs[sceneId]) sceneToTccs[sceneId] = [];
            sceneToTccs[sceneId].push(tcc.tcc_id);
        });
    });

    // 找出共享场景的TCC对
    const connections = new Set();
    Object.entries(sceneToTccs).forEach(([sceneId, tccIds]) => {
        if (tccIds.length >= 2) {
            // 这些TCC共享同一个场景，建立关系
            for (let i = 0; i < tccIds.length; i++) {
                for (let j = i + 1; j < tccIds.length; j++) {
                    const pair = [tccIds[i], tccIds[j]].sort().join('|');
                    if (!connections.has(pair)) {
                        connections.add(pair);
                        diagram += `    ${tccIds[i]} <-->|"场景交织"| ${tccIds[j]}\n`;
                    }
                }
            }
        }
    });

    // 2. 如果没有场景重叠，基于叙事层级建立关系 (A线->B线->C线)
    if (connections.size === 0 && rankings) {
        const aLine = rankings.a_line;
        const bLines = rankings.b_lines || [];
        const cLines = rankings.c_lines || [];

        // A线连接到所有B线 (主线影响副线)
        if (aLine) {
            bLines.forEach(bLine => {
                diagram += `    ${aLine.tcc_id} -->|"主线驱动"| ${bLine.tcc_id}\n`;
            });
            // 如果没有B线，A线连接C线
            if (bLines.length === 0) {
                cLines.forEach(cLine => {
                    diagram += `    ${aLine.tcc_id} -.->|"情节点缀"| ${cLine.tcc_id}\n`;
                });
            }
        }

        // B线连接到C线 (副线呼应次线)
        bLines.forEach(bLine => {
            cLines.forEach(cLine => {
                diagram += `    ${bLine.tcc_id} -.->|"情节呼应"| ${cLine.tcc_id}\n`;
            });
        });
    }

    // 3. 如果仍然没有连接，添加基于角色冲突的推断连接
    if (connections.size === 0 && tccs.length >= 2) {
        // 将所有TCC连接到主线（如果存在）
        const mainTcc = rankings?.a_line?.tcc_id || tccs[0].tcc_id;
        tccs.forEach(tcc => {
            if (tcc.tcc_id !== mainTcc) {
                diagram += `    ${mainTcc} -->|"叙事关联"| ${tcc.tcc_id}\n`;
            }
        });
    }

    diagram += '\n';

    // Add styles for A/B/C lines
    diagram += '    %% === 样式定义 ===\n';
    diagram += '    classDef aline fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff\n';
    diagram += '    classDef bline fill:#4ecdc4,stroke:#20a99e,stroke-width:2px,color:#fff\n';
    diagram += '    classDef cline fill:#95e1d3,stroke:#52b69a,stroke-width:2px,color:#000\n';
    diagram += '    classDef default fill:#e9ecef,stroke:#495057,stroke-width:1px\n';
    diagram += '\n';

    // Apply styles to nodes
    tccs.forEach(tcc => {
        const lineType = lineTypeMap[tcc.tcc_id];
        if (lineType === 'A') {
            diagram += `    class ${tcc.tcc_id} aline\n`;
        } else if (lineType === 'B') {
            diagram += `    class ${tcc.tcc_id} bline\n`;
        } else if (lineType === 'C') {
            diagram += `    class ${tcc.tcc_id} cline\n`;
        }
    });

    // Render Mermaid diagram
    if (window.mermaid) {
        try {
            const diagramId = 'mermaid-' + Date.now();
            mermaid.render(diagramId, diagram).then(renderResult => {
                // 添加图例说明
                let legendHtml = `
                    <div class="mb-3 p-3 bg-light rounded">
                        <h6 class="mb-2"><i class="bi bi-info-circle"></i> 图例说明</h6>
                        <div class="d-flex flex-wrap gap-3">
                            <span><span class="badge" style="background-color:#ff6b6b">■</span> A线 (主线/Spine)</span>
                            <span><span class="badge" style="background-color:#4ecdc4">■</span> B线 (副线/Heart)</span>
                            <span><span class="badge" style="background-color:#95e1d3;color:#000">■</span> C线 (次线/Flavor)</span>
                        </div>
                        <div class="mt-2 small text-muted">
                            <strong>连接关系：</strong>
                            <code>──▶</code> 主线驱动 |
                            <code>◀──▶</code> 场景交织 |
                            <code>- - -▶</code> 情节呼应
                        </div>
                    </div>
                `;
                diagramElement.innerHTML = legendHtml + renderResult.svg;
            }).catch(err => {
                console.error('Mermaid rendering error:', err);
                diagramElement.innerHTML = `<div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    图表渲染失败: ${err.message || err}
                    <br><br>
                    <details>
                        <summary>Mermaid 代码</summary>
                        <pre class="bg-dark text-light p-2">${escapeHtml(diagram)}</pre>
                    </details>
                </div>`;
            });
        } catch (err) {
            console.error('Mermaid error:', err);
            diagramElement.innerHTML = `<div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                Mermaid 初始化失败: ${err.message || err}
            </div>`;
        }
    } else {
        console.error('Mermaid library not loaded');
        diagramElement.innerHTML = `<div class="alert alert-danger">
            Mermaid 库未加载，无法渲染图表
        </div>`;
    }
}

// Helper function to truncate text
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
