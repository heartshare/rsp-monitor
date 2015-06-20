window.onload = function() {
        var CPUSeries = new TimeSeries();
        var MEMSeries = new TimeSeries();
        var smoothieChart = new SmoothieChart({
            minValue: 0.0,
            maxValue: 100.0,
            grid: {
                strokeStyle: 'rgb(223, 223, 223)',
                fillStyle: 'rgb(44,75,95)',
                lineWidth: 1,
                millisPerLine: 1000,
                verticalSections: 4
            }
        });
        smoothieChart.addTimeSeries(CPUSeries, {
            strokeStyle:'rgb(0, 220, 0)',
            fillStyle:'rgba(0, 220, 0, 0.4)',
            lineWidth:3
        });
        smoothieChart.addTimeSeries(MEMSeries, {
            strokeStyle:'rgb(171, 24, 82)',
            fillStyle:'rgba(171, 24, 82, 0.4)',
            lineWidth:3
        });
        smoothieChart.streamTo(document.getElementById("Chart"), 1000);
        if (window["WebSocket"]) {
            var conn = new WebSocket("ws://"+window.location.host+"/ws");
            conn.onmessage = function(e) {
                // console.log('message: ' + e.data);
                var data = JSON.parse(e.data);
                var cpuinfo = data.cpu;
                var meminfo = data.memory;
                var cpuused = 100 - cpuinfo.id;
                var memused = 100 - 100 * (parseFloat(meminfo.cache) + parseFloat(meminfo.buff) + parseFloat(meminfo.free) )/ parseFloat(meminfo.total);
                // console.log('mem',memused);
                document.getElementById("cpu-used").innerHTML = cpuused + " %";
                document.getElementById("mem-used").innerHTML = memused.toFixed(1) + " %";
                CPUSeries.append(new Date().getTime(), parseFloat(cpuused));
                MEMSeries.append(new Date().getTime(), memused);

                document.getElementById("uptime").innerHTML = data.uptime + " %";
                var temp = data.temp;
                document.getElementById("cputemp").innerHTML = temp.cpu;
                document.getElementById("gputemp").innerHTML = temp.gpu;

                var disk = data.disk;
                document.getElementById("disk_total").innerHTML = disk.total;
                document.getElementById("percent").style.width = disk.percent;
                document.getElementById("disk_used").innerHTML = disk.used + ', ' + disk.percent

            };
            conn.onclose = function(evt) {
                // log.innerHTML = "Connection closed";
            };
        } else {
            // log.innerHTML = "Your Browser does not support WebSockets";
        }
};