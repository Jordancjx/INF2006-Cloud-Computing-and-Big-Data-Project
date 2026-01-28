fetch("http://127.0.0.1:5000/analytics/employment-trends")
    .then(res => res.json())
    .then(data => {
        // const years = data.map(d => d.year);
        // const overall = data.map(d => d.employment_rate_overall);
        // const ft = data.map(d => d.employment_rate_ft_perm);

        const trend = data.trend;
        const kpis = data.kpis;

        const years = trend.map(d => d.year);
        const overall = trend.map(d => d.employment_rate_overall);
        const ft = trend.map(d => d.employment_rate_ft_perm);

        // KPI stuff
        if (kpis.avg_employment_rate_overall !== null) {
            document.getElementById("avgEmploymentRateOverall").textContent =
                (kpis.avg_employment_rate_overall).toFixed(1) + "%";
        } else {
            document.getElementById("avgEmploymentRateOverall").textContent = "N/A";
        }
        if (kpis.avg_employment_rate_ft_perm !== null) {
            document.getElementById("avgEmploymentRateFT").textContent =
                (kpis.avg_employment_rate_ft_perm).toFixed(1) + "%";
        } else {
            document.getElementById("avgEmploymentRateFT").textContent = "N/A";
        }
        if (kpis.stability_ratio !== null) {
            document.getElementById("stabilityRatio").textContent =
                (kpis.stability_ratio * 100).toFixed(1) + "%";
        } else {
            document.getElementById("stabilityRatio").textContent = "N/A";
        }
        if (kpis.trend_strength !== null) {
            document.getElementById("trendStrength").textContent =
                kpis.trend_strength.toFixed(2);
        } else {
            document.getElementById("trendStrength").textContent = "N/A";
        }

        new Chart(document.getElementById("employmentTrendChart"), {
            type: "line",
            data: {
                labels: years,
                datasets: [
                    {
                        label: "Overall Employment Rate",
                        data: overall,
                        borderWidth: 2
                    },
                    {
                        label: "Full-Time Permanent Employment Rate",
                        data: ft,
                        borderWidth: 2
                    }
                ]
            }
        });
    });
