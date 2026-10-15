import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Flappy Bird",
    page_icon="🐥",
    layout="centered"
)

st.title("🐥 Flappy Bird Classic")
st.caption("Nhấn **Phím Cách (Space)** hoặc **Click / Chạm vào màn hình** để điều khiển chim bay.")

# Mã nguồn game HTML5 + JavaScript Canvas
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
      font-family: 'Courier New', Courier, monospace;
    }
    canvas {
      border: 3px solid #2e7d32;
      border-radius: 8px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      background-color: #70c5ce;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="360" height="580"></canvas>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let frames = 0;
    const STATE = { START: 0, PLAYING: 1, GAMEOVER: 2 };
    let currentState = STATE.START;
    let score = 0;
    let highScore = 0;

    // Đối tượng Con chim
    const bird = {
      x: 70,
      y: 250,
      radius: 14,
      gravity: 0.28,
      jump: -5.8,
      velocity: 0,
      rotation: 0,
      draw: function () {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);

        // Thân chim
        ctx.fillStyle = "#f8e71c";
        ctx.beginPath();
        ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#000";
        ctx.stroke();

        // Mắt chim
        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.arc(5, -5, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#000";
        ctx.beginPath();
        ctx.arc(7, -5, 2, 0, Math.PI * 2);
        ctx.fill();

        // Mỏ chim
        ctx.fillStyle = "#f5a623";
        ctx.beginPath();
        ctx.moveTo(8, 0);
        ctx.lineTo(18, 4);
        ctx.lineTo(8, 8);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Cánh chim
        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.ellipse(-5, 2, 6, 4, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.restore();
      },
      update: function () {
        if (currentState === STATE.START) {
          this.y = 250 + Math.sin(frames * 0.08) * 6;
          this.rotation = 0;
        } else if (currentState === STATE.PLAYING) {
          this.velocity += this.gravity;
          this.y += this.velocity;

          if (this.velocity >= this.jump) {
            this.rotation = Math.min(Math.PI / 3, (this.velocity / 10) * (Math.PI / 3));
          } else {
            this.rotation = -Math.PI / 6;
          }

          // Chạm đất
          if (this.y + this.radius >= canvas.height - 90) {
            this.y = canvas.height - 90 - this.radius;
            gameOver();
          }
          // Chạm trần
          if (this.y - this.radius <= 0) {
            this.y = this.radius;
            this.velocity = 0;
          }
        }
      },
      flap: function () {
        this.velocity = this.jump;
      },
      reset: function () {
        this.y = 250;
        this.velocity = 0;
        this.rotation = 0;
      }
    };

    // Các ống cản
    const pipes = {
      items: [],
      gap: 135,
      dx: 2.2,
      reset: function () {
        this.items = [];
      },
      draw: function () {
        ctx.fillStyle = "#73bf2e";
        ctx.strokeStyle = "#385e13";
        ctx.lineWidth = 3;

        for (let i = 0; i < this.items.length; i++) {
          let p = this.items[i];
          let topY = p.y;
          let bottomY = p.y + this.gap;

          // Ống trên
          ctx.fillRect(p.x, 0, 52, topY);
          ctx.strokeRect(p.x, 0, 52, topY);
          ctx.fillRect(p.x - 3, topY - 20, 58, 20);
          ctx.strokeRect(p.x - 3, topY - 20, 58, 20);

          // Ống dưới
          ctx.fillRect(p.x, bottomY, 52, canvas.height - 90 - bottomY);
          ctx.strokeRect(p.x, bottomY, 52, canvas.height - 90 - bottomY);
          ctx.fillRect(p.x - 3, bottomY, 58, 20);
          ctx.strokeRect(p.x - 3, bottomY, 58, 20);
        }
      },
      update: function () {
        if (currentState !== STATE.PLAYING) return;

        if (frames % 110 === 0) {
          const maxY = canvas.height - 90 - this.gap - 60;
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

          // Kiểm tra va chạm
          if (
            bird.x + bird.radius > p.x &&
            bird.x - bird.radius < p.x + 52 &&
            (bird.y - bird.radius < p.y || bird.y + bird.radius > p.y + this.gap)
          ) {
            gameOver();
          }

          // Tính điểm
          if (!p.passed && p.x + 52 < bird.x) {
            score++;
            p.passed = true;
          }

          if (p.x + 58 < 0) {
            this.items.splice(i, 1);
            i--;
          }
        }
      }
    };

    // Đất và nền
    const ground = {
      h: 90,
      draw: function () {
        ctx.fillStyle = "#ded895";
        ctx.fillRect(0, canvas.height - this.h, canvas.width, this.h);

        ctx.fillStyle = "#73bf2e";
        ctx.fillRect(0, canvas.height - this.h, canvas.width, 16);

        ctx.fillStyle = "#53801b";
        ctx.fillRect(0, canvas.height - this.h + 16, canvas.width, 4);
      }
    };

    function gameOver() {
      currentState = STATE.GAMEOVER;
      if (score > highScore) {
        highScore = score;
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

    canvas.addEventListener("click", function () {
      handleAction();
    });

    function drawUI() {
      if (currentState === STATE.START) {
        ctx.fillStyle = "#fff";
        ctx.font = "bold 26px Arial, sans-serif";
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 4;
        ctx.strokeText("GET READY!", 100, 190);
        ctx.fillText("GET READY!", 100, 190);

        ctx.font = "16px Arial, sans-serif";
        ctx.fillStyle = "#333";
        ctx.fillText("Nhấn Space hoặc Click để bay", 55, 340);
      } else if (currentState === STATE.PLAYING) {
        ctx.fillStyle = "#fff";
        ctx.font = "bold 38px Arial, sans-serif";
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 4;
        ctx.strokeText(score, canvas.width / 2 - 12, 60);
        ctx.fillText(score, canvas.width / 2 - 12, 60);
      } else if (currentState === STATE.GAMEOVER) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
        ctx.fillRect(30, 150, 300, 220);

        ctx.fillStyle = "#f44336";
        ctx.font = "bold 32px Arial, sans-serif";
        ctx.fillText("GAME OVER", 78, 205);

        ctx.fillStyle = "#fff";
        ctx.font = "20px Arial, sans-serif";
        ctx.fillText("Điểm: " + score, 85, 255);
        ctx.fillText("Kỷ lục: " + highScore, 85, 290);

        ctx.font = "15px Arial, sans-serif";
        ctx.fillStyle = "#ffeb3b";
        ctx.fillText("Bấm vào màn hình để chơi lại", 75, 340);
      }
    }

    function loop() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      bird.update();
      pipes.update();

      pipes.draw();
      ground.draw();
      bird.draw();
      drawUI();

      frames++;
      requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
"""

# Nhúng vào Streamlit
components.html(game_code, height=620)
