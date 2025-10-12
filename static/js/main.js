// Main JavaScript file for EDA Preprocessing Django App

// CSRF Token helper for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Setup CSRF token for AJAX requests
const csrftoken = getCookie('csrftoken');

// File upload drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const fileUploadArea = document.querySelector('.file-upload-area');
    if (fileUploadArea) {
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            fileUploadArea.classList.add('dragover');
        }

        function unhighlight(e) {
            fileUploadArea.classList.remove('dragover');
        }

        // Handle dropped files
        fileUploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            const fileInput = document.querySelector('#csv-file');
            if (fileInput && files.length > 0) {
                fileInput.files = files;
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.querySelector('.btn-close')) {
                alert.querySelector('.btn-close').click();
            } else {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });
});

// Chart generation functions
function generateChart(chartType, data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Chart container not found:', containerId);
        return;
    }

    // Show loading spinner
    showLoading(containerId);

    // AJAX request to generate chart
    fetch('/eda/generate-chart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            chart_type: chartType,
            data: data
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(containerId);
        if (data.success) {
            // Use Plotly to render the chart
            Plotly.newPlot(containerId, data.chart_data, data.layout, {responsive: true});
        } else {
            container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    })
    .catch(error => {
        hideLoading(containerId);
        console.error('Error generating chart:', error);
        container.innerHTML = '<div class="alert alert-danger">Error generating chart</div>';
    });
}

// Loading spinner functions
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="loading-spinner d-flex justify-content-center align-items-center" style="height: 300px;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span class="ms-2">Generating chart...</span>
            </div>
        `;
    }
}

function hideLoading(containerId) {
    const spinner = document.querySelector(`#${containerId} .loading-spinner`);
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Form validation
function validateCSVFile(input) {
    const file = input.files[0];
    if (file) {
        const fileName = file.name.toLowerCase();
        const isCSV = fileName.endsWith('.csv');
        const fileSize = file.size;
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!isCSV) {
            showAlert('Please select a CSV file.', 'danger');
            input.value = '';
            return false;
        }

        if (fileSize > maxSize) {
            showAlert('File size must be less than 10MB.', 'danger');
            input.value = '';
            return false;
        }

        showAlert(`File "${file.name}" selected successfully!`, 'success');
        return true;
    }
    return false;
}

// Alert helper function
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.alert-container') || 
                          document.querySelector('.container-fluid .row .col-lg-9');
    
    if (alertContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertDiv.querySelector('.btn-close')) {
                alertDiv.querySelector('.btn-close').click();
            }
        }, 5000);
    }
}

// Data analysis functions
function analyzeData(analysisType, options = {}) {
    showLoading('analysis-results');
    
    fetch('/eda/analyze/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            analysis_type: analysisType,
            options: options
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('analysis-results');
        const container = document.getElementById('analysis-results');
        if (container) {
            if (data.success) {
                container.innerHTML = data.html;
            } else {
                container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            }
        }
    })
    .catch(error => {
        hideLoading('analysis-results');
        console.error('Error analyzing data:', error);
        const container = document.getElementById('analysis-results');
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">Error analyzing data</div>';
        }
    });
}

// Preprocessing functions
function applyPreprocessing(operation, data) {
    fetch('/preprocessing/apply/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            operation: operation,
            data: data
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Preprocessing applied successfully!', 'success');
            // Refresh the data display if needed
            location.reload();
        } else {
            showAlert(result.error || 'Error applying preprocessing', 'danger');
        }
    })
    .catch(error => {
        console.error('Error applying preprocessing:', error);
        showAlert('Error applying preprocessing', 'danger');
    });
}

// Utility functions
function formatNumber(num) {
    if (typeof num !== 'number') return num;
    return num.toLocaleString();
}

function formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Export functions
function exportData(format = 'csv') {
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Exporting...';
    }

    fetch(`/preprocessing/export/${format}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Export failed');
        }
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `processed_data.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showAlert(`Data exported successfully as ${format.toUpperCase()}!`, 'success');
    })
    .catch(error => {
        console.error('Error exporting data:', error);
        showAlert('Error exporting data', 'danger');
    })
    .finally(() => {
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = `<i class="bi bi-download"></i> Export ${format.toUpperCase()}`;
        }
    });
}