const now=new Date();
js_minute=now.getMinutes();
js_second=now.getSeconds();

django_minute=parseInt(document.getElementById('minute').textContent)+1;
django_second=parseInt(document.getElementById('second').textContent);

end_second=(django_minute*60)+django_second;
start_second=(js_minute*60)+js_second;
total_time=end_second-start_second;

if(total_time<0)
{
    total_time=0;
}
function startTimer(duration) {

    function updateTimerDisplay(timeLeft) {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      }
    var timeout = setTimeout(function () {
        var time = duration;
        var i = 1;
        var k = ((i/duration) * 100);
        var l = 100 - k;
        i++;
        document.getElementById("c1").style.strokeDasharray = [l,k];
        document.getElementById("c2").style.strokeDasharray = [k,l];
        document.getElementById("c1").style.strokeDashoffset = l;
        document.getElementById("counterText").innerHTML = updateTimerDisplay(duration);
        var interval = setInterval(function() {
            if (i > time) {
                clearInterval(interval);
                clearTimeout(timeout);
                return;
            }
            k = ((i/duration) * 100);
            l = 100 - k;
            document.getElementById("c1").style.strokeDasharray = [l,k];
            document.getElementById("c2").style.strokeDasharray = [k,l];
            document.getElementById("c1").style.strokeDashoffset = l;
            //console.log(k, l);
            val=(duration +1)-i;
            document.getElementById("counterText").innerHTML = updateTimerDisplay(val);
            i++;
        }, 1000);
    },0);
}
startTimer(total_time);
  


