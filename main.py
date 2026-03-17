<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TuyTam Store | DonutSMP</title>

<style>
body{
    margin:0;
    font-family:Arial;
    background:#0f0f0f;
    color:white;
    text-align:center;
}

header{
    background:#ff9900;
    padding:20px;
    font-size:28px;
    font-weight:bold;
}

.container{
    padding:30px;
}

.card{
    background:#1e1e1e;
    padding:25px;
    border-radius:10px;
    max-width:800px;
    margin:auto;
}

button{
    background:#ff9900;
    border:none;
    padding:12px 20px;
    font-size:16px;
    border-radius:8px;
    cursor:pointer;
}

button:hover{
    background:#ff7700;
}

/* POPUP */
#popup{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:rgba(0,0,0,0.8);
display:flex;
justify-content:center;
align-items:center;
z-index:9999;
opacity:0;
animation:fadeIn 0.5s forwards;
}

#popup-content{
background:#1e1e1e;
padding:30px;
border-radius:10px;
text-align:center;
max-width:400px;
transform:scale(0.7);
animation:zoomIn 0.4s forwards;
}

@keyframes fadeIn{to{opacity:1;}}
@keyframes zoomIn{to{transform:scale(1);}}

.fadeOut{
animation:fadeOut 0.5s forwards;
}
@keyframes fadeOut{to{opacity:0;}}

/* neon credit */
.credit{
margin-top:15px;
font-size:13px;
color:#00fff7;
font-weight:bold;
text-shadow:
0 0 5px #00fff7,
0 0 10px #00fff7,
0 0 20px #00fff7,
0 0 40px #00fff7;
animation:neonGlow 1.5s infinite alternate;
}

@keyframes neonGlow{
from{
text-shadow:0 0 5px #00fff7;
}
to{
text-shadow:
0 0 10px #00fff7,
0 0 20px #00fff7,
0 0 40px #00fff7;
}
}

ul{
text-align:left;
max-width:350px;
margin:auto;
}

.ad{
margin:30px 0;
padding:20px;
background:#222;
border-radius:10px;
}
</style>

</head>

<body>

<header>
✨ TUYTAM STORE ✨
</header>

<div class="container">

<div class="card">

<h2>Shop uy tín hàng đầu trong server DONUTSMP</h2>

<p>Chuyên mua bán – trao đổi nhanh chóng, an toàn.</p>

<h3>🛒 Mặt hàng hiện có:</h3>

<ul>
<li>
🦴 <b>Spawner Skeleton</b><br>
<span style="color:#aaa;">Spawner xương, farm mob nhanh</span><br>
<span style="color:#00ff99;">Giá: 4.500đ</span><br>
<span style="color:#00bfff;">Đã bán: <span id="sold1"></span></span>
</li>

<br>

<li>
💰 <b>Money</b><br>
<span style="color:#aaa;">Nhận tiền nhanh trong server</span><br>
<span style="color:#00ff99;">Giá: 900đ / 1M</span><br>
<span style="color:#00bfff;">Đã bán: <span id="sold2"></span></span>
</li>
</ul>

<br>

<a href="redirect.html">
<button>VÀO DISCORD GIAO DỊCH</button>
</a>

</div>

<!-- QUẢNG CÁO -->
<div class="ad">
<h3>Quảng cáo</h3>

<script src="https://pl28928436.effectivegatecpm.com/e0/ce/e7/e0cee741254541fa379b3b6f55d4be7c.js"></script>

</div>

</div>

<!-- POPUP -->
<div id="popup">
<div id="popup-content">

<h2>✨ TuyTam Store ✨</h2>

<p>🔥 Dịch vụ:</p>

<p>🦴 Spawner Skeleton</p>
<p>💰 Money</p>

<br>

<a href="https://discord.gg/kYmPCKJ3X">
<button>Vào Discord</button>
</a>

<br>

<button onclick="showDonate()">💚 Donate</button>

<div id="donateBox" style="display:none; margin-top:15px;">
<p>💖 Ủng hộ shop:</p>
<img src="zalopay.png" width="180" style="border-radius:10px;">
<p style="font-size:12px;color:#aaa;">Quét QR ZaloPay</p>
</div>

<button onclick="closePopup()">Đóng</button>

<div class="credit">Code by Rubynek209</div>

</div>
</div>

<script>
// popup
function closePopup(){
let popup = document.getElementById("popup");
popup.classList.add("fadeOut");
setTimeout(()=>{popup.style.display="none";},500);
}

setTimeout(closePopup,5000);

// donate
function showDonate(){
let box = document.getElementById("donateBox");
box.style.display = box.style.display==="none"?"block":"none";
}

// fake sold
let sold1 = 27;
let sold2 = 142;

sold1 += Math.floor(Math.random()*2);
sold2 += Math.floor(Math.random()*5);

document.getElementById("sold1").innerText = sold1;
document.getElementById("sold2").innerText = sold2;

</script>

</body>
</html>
