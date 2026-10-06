Chart.defaults.color = '#64748B';
Chart.defaults.font.family = 'Inter, system-ui, -apple-system, sans-serif';

document.addEventListener('DOMContentLoaded', () => {
  const analytics = window.dashboardAnalytics || {};
  const marketData = window.marketData || (analytics.marketData || {});
  const competitors = window.competitors || (analytics.competitors || []);
  const riskScores = window.riskScores || (analytics.riskScores || {});
  const riskTrend = window.riskTrend || (analytics.riskTrend || {});

  // ──────────────────────────────────────────────────────────────────────────
  // 1. Success Probability Gauge (Half-Doughnut / Radial Chart)
  // ──────────────────────────────────────────────────────────────────────────
  const successGaugeCanvas = document.getElementById('successGaugeChart');
  if (successGaugeCanvas) {
    const successProb = analytics.successProbability != null ? analytics.successProbability : (window.successProbability || 55);
    const remainder = Math.max(0, 100 - successProb);
    
    // Determine color based on probability
    let gaugeColor = '#059669'; // Emerald
    if (successProb < 40) gaugeColor = '#DC2626'; // Red
    else if (successProb < 65) gaugeColor = '#2563EB'; // Blue

    new Chart(successGaugeCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Success Probability', 'Risk Exposure'],
        datasets: [{
          data: [successProb, remainder],
          backgroundColor: [gaugeColor, '#E2E8F0'],
          borderWidth: 0,
          circumference: 180,
          rotation: 270,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '78%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` ${context.label}: ${context.raw}%`;
              }
            }
          }
        },
      },
    });
  }

  // ──────────────────────────────────────────────────────────────────────────
  // 2. Risk Distribution Chart (Radar / Multi-Bar Chart)
  // ──────────────────────────────────────────────────────────────────────────
  const riskDistCanvas = document.getElementById('riskDistributionChart');
  if (riskDistCanvas && riskScores) {
    const labels = ['Financial', 'Competition', 'Technical', 'Operational', 'Market'];
    const dataValues = [
      riskScores.financial_risk || analytics.financialRisk || 50,
      riskScores.competition_risk || analytics.competitionRisk || 50,
      riskScores.technical_risk || analytics.technicalRisk || 50,
      riskScores.operational_risk || analytics.operationalRisk || 45,
      riskScores.market_risk || analytics.marketRisk || 40,
    ];

    new Chart(riskDistCanvas, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Risk Exposure (%)',
          data: dataValues,
          backgroundColor: 'rgba(220, 38, 38, 0.15)',
          borderColor: '#DC2626',
          borderWidth: 2,
          pointBackgroundColor: '#DC2626',
          pointBorderColor: '#FFFFFF',
          pointHoverBackgroundColor: '#FFFFFF',
          pointHoverBorderColor: '#DC2626',
          pointRadius: 4,
        }, {
          label: 'Safe Benchmark (< 40%)',
          data: [35, 35, 35, 35, 35],
          backgroundColor: 'rgba(5, 150, 105, 0.08)',
          borderColor: '#059669',
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, font: { size: 10, weight: '600' }, color: '#475569' }
          },
        },
        scales: {
          r: {
            angleLines: { color: '#E2E8F0' },
            grid: { color: '#F1F5F9' },
            pointLabels: { font: { size: 10, weight: '600' }, color: '#334155' },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { display: false, stepSize: 20 },
          },
        },
      },
    });
  }

  // ──────────────────────────────────────────────────────────────────────────
  // 3. 6-Month Risk Trajectory Trend Chart (Unmitigated vs Mitigated)
  // ──────────────────────────────────────────────────────────────────────────
  const riskTrendCanvas = document.getElementById('riskTrendTrajectoryChart');
  if (riskTrendCanvas && riskTrend && riskTrend.labels) {
    const ctx = riskTrendCanvas.getContext('2d');
    const gradMitigated = ctx.createLinearGradient(0, 0, 0, 200);
    gradMitigated.addColorStop(0, 'rgba(5, 150, 105, 0.25)');
    gradMitigated.addColorStop(1, 'rgba(5, 150, 105, 0.01)');

    new Chart(riskTrendCanvas, {
      type: 'line',
      data: {
        labels: riskTrend.labels,
        datasets: [
          {
            label: 'With AI Mitigation Plan',
            data: riskTrend.mitigated,
            borderColor: '#059669',
            backgroundColor: gradMitigated,
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#059669',
            pointRadius: 4,
          },
          {
            label: 'Unmitigated Trajectory',
            data: riskTrend.unmitigated,
            borderColor: '#DC2626',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            tension: 0.35,
            pointBackgroundColor: '#DC2626',
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { size: 11, weight: '600' }, color: '#334155' },
          },
        },
        scales: {
          x: { grid: { color: '#F1F5F9' }, ticks: { color: '#64748B', font: { size: 11 } } },
          y: {
            min: 0,
            max: 100,
            grid: { color: '#F1F5F9' },
            ticks: {
              color: '#64748B',
              font: { size: 11 },
              callback: (v) => v + '%',
            },
          },
        },
      },
    });
  }

  // ──────────────────────────────────────────────────────────────────────────
  // 4. Market Growth Trend Chart
  // ──────────────────────────────────────────────────────────────────────────
  const trendCanvas = document.getElementById('marketTrendChart');
  if (trendCanvas && marketData && marketData.market_trend) {
    const ctx = trendCanvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 180);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.25)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.02)');

    new Chart(trendCanvas, {
      type: 'line',
      data: {
        labels: marketData.market_trend.map((p) => p.year),
        datasets: [
          {
            label: 'Market Size',
            data: marketData.market_trend.map((p) => p.value),
            borderColor: '#2563EB',
            borderWidth: 2,
            backgroundColor: gradient,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#2563EB',
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#F1F5F9' }, ticks: { color: '#64748B', font: { size: 10 } } },
          y: { grid: { color: '#F1F5F9' }, ticks: { color: '#64748B', font: { size: 10 } } },
        },
      },
    });
  }

  // ──────────────────────────────────────────────────────────────────────────
  // 5. Competitor Landscape Doughnut Chart
  // ──────────────────────────────────────────────────────────────────────────
  const compCanvas = document.getElementById('competitorChart');
  if (compCanvas && competitors && competitors.length > 0) {
    new Chart(compCanvas, {
      type: 'doughnut',
      data: {
        labels: competitors.map((c) => c.name),
        datasets: [
          {
            data: competitors.map((c) => c.market_share),
            backgroundColor: ['#2563EB', '#7C3AED', '#EC4899', '#10B981'],
            borderWidth: 2,
            borderColor: '#FFFFFF',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#475569', boxWidth: 10, font: { size: 10 } } },
        },
      },
    });
  }
});
