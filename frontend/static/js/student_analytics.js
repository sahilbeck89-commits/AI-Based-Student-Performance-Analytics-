// Student Analytics Logic - Handles CSV Upload and Real-Time Dashboard Rendering

let currentDataset = [];
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    initDropzone();
});

function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('csv-file-input');
    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFile(files[0]);
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) handleFile(this.files[0]);
    });
}

async function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
        showToast('Please upload a valid .csv file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const progWrap = document.getElementById('upload-progress');
    const progBar = document.getElementById('upload-bar');
    const statusTxt = document.getElementById('upload-status');
    
    progWrap.style.display = 'block';
    progBar.style.width = '30%';
    statusTxt.innerText = 'Uploading...';

    try {
        const res = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        
        progBar.style.width = '70%';
        statusTxt.innerText = 'Processing data...';

        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        progBar.style.width = '100%';
        statusTxt.innerText = 'Rendering dashboard...';

        setTimeout(() => {
            progWrap.style.display = 'none';
            showToast('Data processed successfully!', 'success');
            // Backend returns parse_summary (not metadata) and records live inside it
            const metadata = {
                filename:       data.filename || data.parse_summary?.filename || '',
                row_count:      data.parse_summary?.row_count || 0,
                warnings:       data.parse_summary?.warnings || [],
                column_mapping: data.parse_summary?.column_mapping || {},
            };
            const records = data.parse_summary?.records || [];
            renderAnalytics(data.analytics, records, metadata);
        }, 500);

    } catch (err) {
        progWrap.style.display = 'none';
        showToast(err.message, 'error');
    }
}

function renderAnalytics(analytics, records, metadata) {
    currentDataset = records;
    document.getElementById('analytics-dashboard').style.display = 'block';

    // Parse Warnings
    const warnSec = document.getElementById('warnings-section');
    if (metadata.warnings && metadata.warnings.length) {
        warnSec.style.display = 'block';
        document.getElementById('warnings-list').innerHTML = metadata.warnings.map(w => `<p style="color:var(--clr-red);font-size:0.9rem;margin-bottom:4px">⚠️ ${w}</p>`).join('');
    } else {
        warnSec.style.display = 'none';
    }

    // Summary
    document.getElementById('summary-content').innerHTML = `
        <p><strong>File:</strong> ${metadata.filename}</p>
        <p><strong>Rows Parsed:</strong> ${metadata.row_count}</p>
        <p style="margin-top:8px;font-size:0.85rem;color:var(--clr-muted)">
            Columns mapped: ${Object.entries(metadata.column_mapping).map(([k,v]) => `${k}→${v}`).join(', ')}
        </p>
    `;

    // Stats
    const stats = analytics.class_stats;
    document.querySelector('#stat-total-students h3').innerText = stats.total_students || 0;
    document.querySelector('#stat-avg-marks h3').innerText = (stats.avg_percentage || 0) + '%';
    document.querySelector('#stat-avg-att h3').innerText = stats.avg_attendance ? stats.avg_attendance + '%' : 'N/A';
    document.querySelector('#stat-pass-rate h3').innerText = (stats.pass_rate || 0) + '%';

    // Charts
    renderChart('subjectBarChart', 'bar', analytics.subject_stats.map(s => s.subject), [{
        label: 'Average %',
        data: analytics.subject_stats.map(s => s.avg_percentage),
        backgroundColor: 'rgba(52,211,153,0.7)'
    }], { y: { max: 100 } });

    renderChart('subjectAttChart', 'bar', analytics.subject_stats.map(s => s.subject), [{
        label: 'Attendance %',
        data: analytics.subject_stats.map(s => s.avg_attendance || 0),
        backgroundColor: 'rgba(167,139,250,0.7)'
    }], { y: { max: 100 } });

    if (analytics.attendance_correlation && analytics.attendance_correlation.data) {
        renderChart('correlationChart', 'scatter', null, [{
            label: 'Students',
            data: analytics.attendance_correlation.data.map(d => ({x: d.attendance, y: d.marks})),
            backgroundColor: 'rgba(251,191,36,0.7)'
        }], {
            x: { title: { display: true, text: 'Attendance %' }, max: 100 },
            y: { title: { display: true, text: 'Marks' } }
        });
    }

    // Risk chart
    const risks = analytics.risk_assessment;
    const riskCounts = { critical: 0, warning: 0, watch: 0, safe: 0 };
    risks.forEach(r => { if(riskCounts[r.risk_level] !== undefined) riskCounts[r.risk_level]++; });
    renderChart('riskChart', 'doughnut', ['Critical', 'Warning', 'Watch', 'Safe'], [{
        data: [riskCounts.critical, riskCounts.warning, riskCounts.watch, riskCounts.safe],
        backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e']
    }], null);

    // Lists
    document.getElementById('toppers-list').innerHTML = analytics.toppers.map(t => `
        <div class="stat-card" style="padding:12px">
            <div style="font-size:1.2rem;font-weight:bold">#${t.rank} ${t.name}</div>
            <div style="color:var(--clr-muted);font-size:0.9rem">Avg: ${t.avg_percentage}%</div>
        </div>
    `).join('');

    document.getElementById('weak-list').innerHTML = analytics.weak_students.map(w => `
        <div style="padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05)">
            <strong>${w.name}</strong> (${w.avg_percentage}%) 
            <span class="badge badge-danger" style="font-size:0.7rem">${w.severity}</span>
        </div>
    `).join('');

    document.getElementById('recs-list').innerHTML = analytics.recommendations.map(r => `
        <div class="rec-card ${r.type}" style="margin-bottom:8px">
            <h4 style="margin-bottom:4px">${r.title}</h4>
            <p style="font-size:0.9rem">${r.text}</p>
        </div>
    `).join('');

    // Table
    renderTable();
}

function renderChart(id, type, labels, datasets, scales) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    if (charts[id]) charts[id].destroy();
    
    const config = {
        type: type,
        data: { labels: labels, datasets: datasets },
        options: { responsive: true, maintainAspectRatio: false }
    };
    if (scales) config.options.scales = scales;
    if (type === 'doughnut') config.options.plugins = { legend: { position: 'right' } };

    charts[id] = new Chart(ctx, config);
}

function renderTable() {
    const q = document.getElementById('table-search').value.toLowerCase();
    let data = currentDataset;
    if (q) {
        data = data.filter(r => 
            (r.student_name && r.student_name.toLowerCase().includes(q)) || 
            (r.usn && r.usn.toLowerCase().includes(q)) ||
            (r.subject && r.subject.toLowerCase().includes(q))
        );
    }
    
    const cols = ['usn', 'student_name', 'subject', 'marks', 'max_marks', 'attendance', 'grade'];
    document.getElementById('table-head').innerHTML = cols.map(c => `<th>${c.toUpperCase()}</th>`).join('');
    
    document.getElementById('table-body').innerHTML = data.slice(0, 100).map(r => `
        <tr>${cols.map(c => `<td>${r[c] !== null && r[c] !== undefined ? r[c] : '-'}</td>`).join('')}</tr>
    `).join('');
}

function filterDataTable() {
    renderTable();
}

function exportDataset() {
    if (!currentDataset.length) return;
    const cols = Object.keys(currentDataset[0]);
    let csv = cols.join(',') + '\n';
    currentDataset.forEach(r => {
        csv += cols.map(c => `"${r[c] !== null && r[c] !== undefined ? r[c] : ''}"`).join(',') + '\n';
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'exported_dataset.csv';
    a.click();
}
