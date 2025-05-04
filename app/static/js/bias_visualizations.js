/**
 * EthicAI Bias Visualization Library
 * Provides interactive charts for bias analysis
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a report view page
    const reportIdElem = document.getElementById('report-id');
    if (!reportIdElem) return;
    
    const reportId = reportIdElem.dataset.reportId;
    
    // Initialize charts if the container exists
    initDemographicParityCharts();
    initRocCurves();
    initBiasHeatmap();
    
    // Check if explainability images exist and initialize tooltips
    initExplainabilityImages();
});

/**
 * Initialize demographic parity bar charts
 */
function initDemographicParityCharts() {
    const demographicParityContainers = document.querySelectorAll('[id$="-demographic-parity-chart"]');
    
    demographicParityContainers.forEach(container => {
        const biasType = container.id.replace('-demographic-parity-chart', '');
        const chartData = JSON.parse(container.dataset.chartData || '{}');
        
        if (!chartData.labels || !chartData.datasets) return;
        
        new Chart(container, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Positive Outcome Rate',
                    data: chartData.datasets[0].data,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Positive Outcome Rate'
                        },
                        max: 1.0
                    },
                    x: {
                        title: {
                            display: true,
                            text: `${biasType.charAt(0).toUpperCase() + biasType.slice(1)} Group`
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Demographic Parity for ${biasType.charAt(0).toUpperCase() + biasType.slice(1)}`
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Positive rate: ${(context.raw * 100).toFixed(1)}%`;
                            }
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}

/**
 * Initialize ROC curve charts
 */
function initRocCurves() {
    const rocCurveContainers = document.querySelectorAll('[id$="-roc-curve-chart"]');
    
    rocCurveContainers.forEach(container => {
        const biasType = container.id.replace('-roc-curve-chart', '');
        const chartData = JSON.parse(container.dataset.chartData || '{}');
        
        if (!chartData.labels || !chartData.datasets) return;
        
        new Chart(container, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.datasets[0].label,
                    data: chartData.datasets[0].data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                },
                // Add diagonal line for random classifier reference
                {
                    label: 'Random Classifier',
                    data: chartData.labels, // Same as FPR values
                    backgroundColor: 'rgba(200, 200, 200, 0.2)',
                    borderColor: 'rgba(200, 200, 200, 1)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'True Positive Rate'
                        },
                        max: 1.0
                    },
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'False Positive Rate'
                        },
                        max: 1.0
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `ROC Curve for ${biasType.charAt(0).toUpperCase() + biasType.slice(1)} Analysis`
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}

/**
 * Initialize bias heatmap visualizations
 */
function initBiasHeatmap() {
    const heatmapContainer = document.getElementById('bias-heatmap-chart');
    if (!heatmapContainer) return;
    
    const reportId = document.getElementById('report-id').dataset.reportId;
    
    // Fetch heatmap data
    fetch(`/bias_analyzer/report/${reportId}/heatmap`)
        .then(response => response.json())
        .then(data => {
            if (data.x_labels && data.y_labels && data.data) {
                // Multi-dimensional heatmap
                createMultidimensionalHeatmap(heatmapContainer, data);
            } else if (data.labels && data.datasets) {
                // Single dimension heatmap
                createSingleDimensionHeatmap(heatmapContainer, data);
            }
        })
        .catch(error => {
            console.error('Error fetching heatmap data:', error);
            heatmapContainer.innerHTML = '<div class="alert alert-danger">Failed to load heatmap data</div>';
        });
}

/**
 * Create a multidimensional heatmap for intersectional bias
 */
function createMultidimensionalHeatmap(container, data) {
    const ctx = container.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'matrix',
        data: {
            datasets: [{
                label: 'Intersectional Bias',
                data: generateHeatmapData(data.x_labels, data.y_labels, data.data),
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    const alpha = value;
                    return getColorForValue(value);
                },
                borderColor: 'white',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / data.x_labels.length - 1,
                height: ({ chart }) => (chart.chartArea || {}).height / data.y_labels.length - 1
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        title() {
                            return '';
                        },
                        label(context) {
                            const v = context.dataset.data[context.dataIndex];
                            return [
                                `${data.x_labels[v.x]} (X-axis)`,
                                `${data.y_labels[v.y]} (Y-axis)`,
                                `Bias: ${(v.v * 100).toFixed(1)}%`
                            ];
                        }
                    }
                },
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Intersectional Bias Heatmap'
                }
            },
            scales: {
                x: {
                    type: 'category',
                    labels: data.x_labels,
                    offset: true,
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: data.y_labels,
                    offset: true,
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Create a single dimension heatmap when only one bias type is analyzed
 */
function createSingleDimensionHeatmap(container, data) {
    new Chart(container, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Bias Score',
                data: data.datasets.map(d => d.data[0]), // Use diagonal values as bias score
                backgroundColor: data.labels.map((_, i) => getColorForValue(data.datasets[i].data[0])),
                borderColor: 'rgba(255, 255, 255, 0.5)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bias Score'
                    },
                    max: 0.5 // Cap at 50% bias for better visibility
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Bias Scores by Group'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Bias score: ${(context.raw * 100).toFixed(1)}%`;
                        }
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Generate heatmap data structure from raw data
 */
function generateHeatmapData(xLabels, yLabels, data) {
    const result = [];
    for (let y = 0; y < yLabels.length; y++) {
        for (let x = 0; x < xLabels.length; x++) {
            result.push({
                x,
                y,
                v: data[y][x]
            });
        }
    }
    return result;
}

/**
 * Get color for heatmap based on value
 * Red = high bias, Green = low bias
 */
function getColorForValue(value) {
    // Value should be between 0-1
    // Convert to HSL color (120 = green for low bias, 0 = red for high bias)
    const hue = (1 - value) * 120;
    return `hsla(${hue}, 80%, 60%, 0.8)`;
}

/**
 * Initialize explainability images and tooltips
 */
function initExplainabilityImages() {
    const explainabilityImages = document.querySelectorAll('.explainability-image');
    
    explainabilityImages.forEach(img => {
        // Add click handler to show larger version in modal
        img.addEventListener('click', function() {
            const modal = document.getElementById('explainabilityModal');
            const modalImg = document.getElementById('explainabilityModalImg');
            const modalTitle = document.getElementById('explainabilityModalTitle');
            
            if (modal && modalImg) {
                modalImg.src = this.src;
                modalTitle.textContent = this.alt;
                
                // Show modal (using Bootstrap's modal interface)
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
            }
        });
    });
}

/**
 * Export recommendations to JSON
 */
function exportRecommendations(reportId) {
    window.location.href = `/bias_analyzer/report/${reportId}/export_recommendations`;
} 