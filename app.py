import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Flappy Bird Retro Deluxe",
    page_icon="🐤",
    layout="centered"
)

st.title("🐤 Flappy Bird Deluxe")
st.caption("Nhấn **Phím Cách (Space)** hoặc **Click chuột / Chạm màn hình** để nhảy. Có âm thanh & nhạc nền!")

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <style>
    body {
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      background: transparent;
      user-select: none;
      -webkit-user-select: none;
      font-family: 'Courier New', Courier, monospace, sans-serif;
    }
    #game-container {
      position: relative;
    }
    canvas {
      border: 4px solid #1e3d14;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.35);
      background: #70c5ce;
      cursor: pointer;
    }
    .sound-toggle {
      position: absolute;
      top: 15px;
      right: 15px;
      background: rgba(255, 255, 255, 0.85);
      border: 2px solid #333;
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 14px;
      font-weight: bold;
      cursor: pointer;
      user-select: none;
    }
  </style>
</head>
<body>
  <div id="game-container">
    <canvas id="gameCanvas" width="360" height="600"></canvas>
    <button id="muteBtn" class="sound-toggle">🔊 Âm thanh: BẬT</button>
  </div>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const muteBtn = document.getElementById("muteBtn");

    let isMuted = false;
    muteBtn.onclick = (e) => {
      e.stopPropagation();
      isMuted = !isMuted;
      muteBtn.innerText = isMuted ? "🔇 Âm thanh: TẮT" : "🔊 Âm thanh: BẬT";
    };

    // --- HỆ THỐNG ÂM THANH WEB AUDIO SYNTHESIZER ---
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function initAudio() {
      if (!audioCtx) {
        audioCtx = new AudioContext();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    }

    function playTone(freq, type, duration, startVol = 0.15, endVol = 0.01) {
      if (isMuted || !audioCtx) return;
      try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(startVol, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(endVol, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      } catch(e){}
    }

    function soundFlap() {
      if (isMuted || !audioCtx) return;
      try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(320, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(540, audioCtx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.12);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.12);
      } catch(e){}
    }

    function soundScore() {
      playTone(587.33, "square", 0.1, 0.12); // D5
      setTimeout(() => playTone(880, "square", 0.18, 0.15), 100); // A5
    }

    function soundHit() {
      playTone(160, "sawtooth", 0.25, 0.3, 0.01);
    }

    // Nhạc nền 8-bit nhẹ nhàng
    let bgmStep = 0;
    const bgmNotes = [261.63, 293.66, 329.63, 392.00, 329.63, 293.66];
    function tickBGM() {
      if (currentState === STATE.PLAYING && !isMuted && audioCtx) {
        if (frames % 24 === 0) {
          playTone(bgmNotes[bgmStep % bgmNotes.length] * 0.5, "triangle", 0.15, 0.05, 0.005);
          bgmStep++;
        }
      }
    }

    // --- GAME ENGINE ---
    let frames = 0;
    const STATE = { START: 0, PLAYING: 1, GAMEOVER: 2 };
    let currentState = STATE.START;
    let score = 0;
    let highScore = localStorage.getItem("flappy_high_score") || 0;

    // Con chim
    const bird = {
      x: 75,
      y: 260,
      radius: 15,
      gravity: 0.26,
      jump: -5.4,
      velocity: 0,
      rotation: 0,
      wingStage: 0,

      draw: function () {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        // Đổ bóng chim
        ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
        ctx.beginPath();
        ctx.ellipse(0, 16, 12, 6, 0, 0, Math.PI * 2);
        ctx.fill();

        // 1. Thân chim hình oval bầu dục
        ctx.fillStyle = "#FFD700";
        ctx.beginPath();
        ctx.ellipse(0, 0, 16, 13, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = "#533804";
        ctx.stroke();

        // 2. Bụng chim màu cam nhạt
        ctx.fillStyle = "#FFA726";
        ctx.beginPath();
        ctx.ellipse(-2, 4, 10, 7, 0, 0, Math.PI * 2);
        ctx.fill();

        // 3. Mắt to lòng trắng viền đen phong cách retro
        ctx.fillStyle = "#FFFFFF";
        ctx.beginPath();
        ctx.arc(6, -4, 6.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Tròng đen & chấm sáng mắt
        ctx.fillStyle = "#000000";
        ctx.beginPath();
        ctx.arc(8, -4, 3, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#FFFFFF";
        ctx.beginPath();
        ctx.arc(9, -6, 1.2, 0, Math.PI * 2);
        ctx.fill();

        // 4. Mỏ chim đỏ/cam đậm đặc trưng
        ctx.fillStyle = "#E64A19";
        ctx.beginPath();
        ctx.moveTo(9, 1);
        ctx.lineTo(21, 5);
        ctx.lineTo(9, 10);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        ctx.strokeStyle = "#533804";
        ctx.beginPath();
        ctx.moveTo(9, 5);
        ctx.lineTo(18, 5);
        ctx.stroke();

        // 5. Cánh chim vỗ chuyển động (3 nấc vỗ cánh)
        let wingY = 0;
        let wingTilt = 0;
        if (this.wingStage === 0) { wingY = -4; wingTilt = -0.3; }
        else if (this.wingStage === 1) { wingY = 1; wingTilt = 0; }
        else { wingY = 5; wingTilt = 0.35; }

        ctx.save();
        ctx.translate(-7, wingY);
        ctx.rotate(wingTilt);
        ctx.fillStyle = "#FFF9C4";
        ctx.beginPath();
        ctx.ellipse(0, 0, 8.5, 5.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        ctx.restore();
      },

      update: function () {
        // Vỗ cánh theo frame
        if (frames % 5 === 0) {
          this.wingStage = (this.wingStage + 1) % 3;
        }

        if (currentState === STATE.START) {
          this.y = 260 + Math.sin(frames * 0.08) * 8;
          this.rotation = 0;
        } else if (currentState === STATE.PLAYING) {
          this.velocity += this.gravity;
          this.y += this.velocity;

          // Xoay góc chúi xuống
          if (this.velocity >= this.jump) {
            this.rotation = Math.min(Math.PI / 2.2, (this.velocity / 9) * (Math.PI / 3));
          } else {
            this.rotation = -0.35;
          }

          // Chạm đất
          if (this.y + this.radius >= canvas.height - 100) {
            this.y = canvas.height - 100 - this.radius;
            soundHit();
            gameOver();
          }
          // Chạm mép trần
          if (this.y - this.radius <= 0) {
            this.y = this.radius;
            this.velocity = 0;
          }
        }
      },

      flap: function () {
        this.velocity = this.jump;
        this.wingStage = 2;
        soundFlap();
      },

      reset: function () {
        this.y = 260;
        this.velocity = 0;
        this.rotation = 0;
      }
    };

    // Đường chân trời (Thành phố xa & Đám mây)
    const background = {
      clouds: [
        { x: 30, y: 80, scale: 1 },
        { x: 190, y: 130, scale: 0.8 },
        { x: 290, y: 70, scale: 1.1 }
      ],
      draw: function() {
        // Vẽ mây
        ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
        this.clouds.forEach(c => {
          ctx.beginPath();
          ctx.arc(c.x, c.y, 18 * c.scale, 0, Math.PI * 2);
          ctx.arc(c.x + 16 * c.scale, c.y - 6 * c.scale, 22 * c.scale, 0, Math.PI * 2);
          ctx.arc(c.x + 36 * c.scale, c.y, 18 * c.scale, 0, Math.PI * 2);
          ctx.fill();
        });

        // Vẽ dãy cao ốc mờ nền retro
        ctx.fillStyle = "#87d9b9";
        const buildings = [
          {x: 0, w: 45, h: 90}, {x: 45, w: 35, h: 120}, {x: 80, w: 50, h: 80},
          {x: 130, w: 40, h: 140}, {x: 170, w: 55, h: 95}, {x: 225, w: 45, h: 110},
          {x: 270, w: 50, h: 85}, {x: 320, w: 45, h: 130}
        ];
        buildings.forEach(b => {
          ctx.fillRect(b.x, canvas.height - 100 - b.h, b.w, b.h);
          ctx.fillStyle = "#72c4a4";
          // Cửa sổ pixel
          for(let wy = canvas.height - 95 - b.h; wy < canvas.height - 110; wy += 15) {
            ctx.fillRect(b.x + 6, wy, b.w - 12, 6);
          }
          ctx.fillStyle = "#87d9b9";
        });
      },
      update: function() {
        if (currentState === STATE.PLAYING) {
          this.clouds.forEach(c => {
            c.x -= 0.4;
            if (c.x + 60 < 0) c.x = canvas.width + 20;
          });
        }
      }
    };

    // Hệ thống Ống cản (Pipes)
    const pipes = {
      items: [],
      gap: 130,
      dx: 2.3,

      reset: function () {
        this.items = [];
      },

      draw: function () {
        for (let i = 0; i < this.items.length; i++) {
          let p = this.items[i];
          let topY = p.y;
          let bottomY = p.y + this.gap;

          // Hiệu ứng bóng sáng ống (Gradient giả lập pixel)
          const drawPipeBody = (x, y, w, h) => {
            ctx.fillStyle = "#74BF2E";
            ctx.fillRect(x, y, w, h);
            // Sọc sáng
            ctx.fillStyle = "#9EE642";
            ctx.fillRect(x + 5, y, 6, h);
            // Sọc tối
            ctx.fillStyle = "#558022";
            ctx.fillRect(x + w - 10, y, 8, h);
            // Viền ngoài
            ctx.lineWidth = 2.5;
            ctx.strokeStyle = "#1e3d14";
            ctx.strokeRect(x, y, w, h);
          };

          const drawPipeHead = (x, y, w, h) => {
            ctx.fillStyle = "#74BF2E";
            ctx.fillRect(x, y, w, h);
            ctx.fillStyle = "#9EE642";
            ctx.fillRect(x + 5, y, 6, h);
            ctx.fillStyle = "#558022";
            ctx.fillRect(x + w - 10, y, 8, h);
            ctx.lineWidth = 2.5;
            ctx.strokeStyle = "#1e3d14";
            ctx.strokeRect(x, y, w, h);
          };

          // Ống trên
          drawPipeBody(p.x, 0, 54, topY);
          drawPipeHead(p.x - 4, topY - 24, 62, 24);

          // Ống dưới
          drawPipeBody(p.x, bottomY, 54, canvas.height - 100 - bottomY);
          drawPipeHead(p.x - 4, bottomY, 62, 24);
        }
      },

      update: function () {
        if (currentState !== STATE.PLAYING) return;

        if (frames % 105 === 0) {
          const maxY = canvas.height - 100 - this.gap - 60;
          const randomY = Math.floor(Math.random() * (maxY - 60 + 1)) + 60;
          this.items.push({
            x: canvas.width,
            y: randomY,
            passed: false
          });
        }

        for (let i = 0; i < this.items.length; i++) {
          let p = this.items[i];
          p.x -= this.dx;

          // Va chạm ống
          if (
            bird.x + bird.radius - 2 > p.x &&
            bird.x - bird.radius + 2 < p.x + 54 &&
            (bird.y - bird.radius + 3 < p.y || bird.y + bird.radius - 3 > p.y + this.gap)
          ) {
            soundHit();
            gameOver();
          }

          // Tính điểm
          if (!p.passed && p.x + 54 < bird.x) {
            score++;
            p.passed = true;
            soundScore();
          }

          if (p.x + 64 < 0) {
            this.items.splice(i, 1);
            i--;
          }
        }
      }
    };

    // Mặt đất chuyển động liên tục
    const ground = {
      h: 100,
      offset: 0,
      draw: function () {
        ctx.fillStyle = "#DDD894";
        ctx.fillRect(0, canvas.height - this.h, canvas.width, this.h);

        // Bãi cỏ xanh
        ctx.fillStyle = "#73BF2E";
        ctx.fillRect(0, canvas.height - this.h, canvas.width, 16);
        ctx.fillStyle = "#558022";
        ctx.fillRect(0, canvas.height - this.h + 16, canvas.width, 4);

        // Các gạch sọc chéo cuộn mặt đất
        ctx.fillStyle = "#CD853F";
        for (let i = -20; i < canvas.width + 20; i += 18) {
          let gx = i - (this.offset % 18);
          ctx.beginPath();
          ctx.moveTo(gx, canvas.height - this.h + 20);
          ctx.lineTo(gx + 10, canvas.height - this.h + 20);
          ctx.lineTo(gx, canvas.height - this.h + 34);
          ctx.closePath();
          ctx.fill();
        }

        ctx.strokeStyle = "#1e3d14";
        ctx.lineWidth = 3;
        ctx.strokeRect(0, canvas.height - this.h, canvas.width, this.h);
      },
      update: function () {
        if (currentState !== STATE.GAMEOVER) {
          this.offset += 2.3;
        }
      }
    };

    function gameOver() {
      currentState = STATE.GAMEOVER;
      if (score > highScore) {
        highScore = score;
        localStorage.setItem("flappy_high_score", highScore);
      }
    }

    function resetGame() {
      bird.reset();
      pipes.reset();
      score = 0;
      frames = 0;
      currentState = STATE.PLAYING;
    }

    function handleAction() {
      initAudio();
      if (currentState === STATE.START) {
        currentState = STATE.PLAYING;
        bird.flap();
      } else if (currentState === STATE.PLAYING) {
        bird.flap();
      } else if (currentState === STATE.GAMEOVER) {
        resetGame();
      }
    }

    window.addEventListener("keydown", function (e) {
      if (e.code === "Space") {
        e.preventDefault();
        handleAction();
      }
    });

    canvas.addEventListener("mousedown", handleAction);
    canvas.addEventListener("touchstart", function (e) {
      e.preventDefault();
      handleAction();
    });

    // Vẽ giao diện đồ họa (UI)
    function drawUI() {
      if (currentState === STATE.START) {
        // Hộp hướng dẫn
        ctx.fillStyle = "#E08031";
        ctx.beginPath();
        ctx.roundRect(40, 160, 280, 110, 12);
        ctx.fill();
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 4;
        ctx.stroke();

        ctx.fillStyle = "#FFFFFF";
        ctx.font = "bold 28px 'Courier New', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("FLAPPY BIRD", canvas.width / 2, 205);

        ctx.font = "bold 15px Arial, sans-serif";
        ctx.fillStyle = "#FFF";
        ctx.fillText("Chạm hoặc nhấn SPACE để bay", canvas.width / 2, 245);

      } else if (currentState === STATE.PLAYING) {
        // Điểm to giữa màn hình có viền đen
        ctx.textAlign = "center";
        ctx.font = "bold 44px 'Courier New', sans-serif";
        ctx.lineWidth = 5;
        ctx.strokeStyle = "#000";
        ctx.strokeText(score, canvas.width / 2, 80);
        ctx.fillStyle = "#FFF";
        ctx.fillText(score, canvas.width / 2, 80);

      } else if (currentState === STATE.GAMEOVER) {
        // Bảng Scoreboard Retro
        ctx.fillStyle = "#DED895";
        ctx.beginPath();
        ctx.roundRect(40, 150, 280, 200, 10);
        ctx.fill();
        ctx.lineWidth = 4;
        ctx.strokeStyle = "#533804";
        ctx.stroke();

        ctx.fillStyle = "#E64A19";
        ctx.font = "bold 30px 'Courier New', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", canvas.width / 2, 195);

        // Huy chương theo điểm
        let medalColor = "#CD7F32"; // Đồng
        if (score >= 20) medalColor = "#FFD700"; // Vàng
        else if (score >= 10) medalColor = "#C0C0C0"; // Bạc

        if (score >= 5) {
          ctx.beginPath();
          ctx.arc(85, 260, 22, 0, Math.PI * 2);
          ctx.fillStyle = medalColor;
          ctx.fill();
          ctx.lineWidth = 3;
          ctx.strokeStyle = "#FFF";
          ctx.stroke();

          ctx.fillStyle = "#FFF";
          ctx.font = "bold 13px sans-serif";
          ctx.fillText("MEDAL", 85, 265);
        }

        ctx.textAlign = "left";
        ctx.font = "bold 18px 'Courier New', sans-serif";
        ctx.fillStyle = "#1e3d14";
        ctx.fillText("ĐIỂM: " + score, 135, 250);
        ctx.fillText("KỶ LỤC: " + highScore, 135, 280);

        ctx.textAlign = "center";
        ctx.fillStyle = "#D32F2F";
        ctx.font = "bold 14px Arial, sans-serif";
        ctx.fillText("Nhấn để chơi lại ván mới 🔄", canvas.width / 2, 325);
      }
    }

    // Vòng lặp trò chơi
    function loop() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      background.update();
      background.draw();

      pipes.update();
      pipes.draw();

      ground.update();
      ground.draw();

      bird.update();
      bird.draw();

      drawUI();
      tickBGM();

      frames++;
      requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
"""

# Render mã Canvas vào giao diện Streamlit
components.html(game_code, height=640)
