import React, { useEffect, useRef } from "react";

export default function HeroAnimation() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let animationFrameId;

    // Handle resizing
    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight || window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Node Types
    // 0: Circular entity, 1: Legal Paper Document
    const nodes = [];
    const nodeCount = 38;
    const maxDistance = 120; // Edge connection distance
    const mouse = { x: null, y: null, radius: 150 };

    // Track mouse movement
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    };

    const handleMouseLeave = () => {
      mouse.x = null;
      mouse.y = null;
    };

    canvas.addEventListener("mousemove", handleMouseMove);
    canvas.addEventListener("mouseleave", handleMouseLeave);

    // Initial Node Creation
    for (let i = 0; i < nodeCount; i++) {
      const isPaper = Math.random() > 0.55;
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        size: isPaper ? 28 : Math.random() * 6 + 4,
        type: isPaper ? 1 : 0,
        label: isPaper
          ? ["قانون", "ظهير", "دستور", "مرسوم", "قرار"][Math.floor(Math.random() * 5)]
          : ["وزارة", "محكمة", "قاضي", "حقوق", "ضريبة", "ملكية"][Math.floor(Math.random() * 6)],
        angle: Math.random() * Math.PI * 2,
        rotSpeed: (Math.random() - 0.5) * 0.005,
        pulse: Math.random() * Math.PI,
      });
    }

    // Animation Loop
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const isDarkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;

      // Color scheme based on clean light theme
      const edgeColor = "rgba(184, 144, 71, 0.12)"; // Gold-ish transparent
      const activeEdgeColor = "rgba(37, 99, 235, 0.3)"; // Blue-ish transparent
      const paperBg = "#FFFFFF";
      const paperBorder = "#E2E8F0";
      const goldAccent = "#B89047";
      const navyAccent = "#0F172A";
      const saasBlue = "#2563EB";

      // 1. Draw connections (Edges)
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dx * dy); // Manhattan style distort or simple Euclidean
          const realDist = Math.sqrt(dx * dx + dy * dy);

          if (realDist < maxDistance) {
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);

            // Highlight connections close to mouse
            const nearMouse =
              mouse.x !== null &&
              ((Math.abs(nodes[i].x - mouse.x) < mouse.radius && Math.abs(nodes[i].y - mouse.y) < mouse.radius) ||
                (Math.abs(nodes[j].x - mouse.x) < mouse.radius && Math.abs(nodes[j].y - mouse.y) < mouse.radius));

            ctx.strokeStyle = nearMouse ? activeEdgeColor : edgeColor;
            ctx.lineWidth = nearMouse ? 1.5 : 0.8;
            ctx.stroke();
          }
        }
      }

      // 2. Draw Nodes
      nodes.forEach((node) => {
        // Update positions
        node.x += node.vx;
        node.y += node.vy;
        node.angle += node.rotSpeed;
        node.pulse += 0.02;

        // Bounce off canvas boundaries
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

        // Interactive mouse physics: repel or attract
        if (mouse.x !== null) {
          const dx = node.x - mouse.x;
          const dy = node.y - mouse.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance < mouse.radius) {
            const force = (mouse.radius - distance) / mouse.radius;
            // Push away gently
            node.x += (dx / distance) * force * 1.5;
            node.y += (dy / distance) * force * 1.5;
          }
        }

        ctx.save();
        ctx.translate(node.x, node.y);

        if (node.type === 1) {
          // Type 1: Draw Legal Paper Document
          ctx.rotate(node.angle);

          // Card Background
          ctx.fillStyle = paperBg;
          ctx.shadowColor = "rgba(15, 23, 42, 0.05)";
          ctx.shadowBlur = 8;
          ctx.shadowOffsetX = 2;
          ctx.shadowOffsetY = 4;
          
          ctx.beginPath();
          const w = 24;
          const h = 32;
          ctx.roundRect(-w / 2, -h / 2, w, h, 3);
          ctx.fill();

          // Card Border
          ctx.strokeStyle = paperBorder;
          ctx.lineWidth = 1;
          ctx.stroke();

          // Draw "lines of text" on the paper
          ctx.shadowBlur = 0; // Reset shadow for internal lines
          ctx.shadowOffsetX = 0;
          ctx.shadowOffsetY = 0;
          ctx.strokeStyle = "rgba(15, 23, 42, 0.2)";
          ctx.lineWidth = 1.5;

          // Header line (Gold)
          ctx.strokeStyle = goldAccent;
          ctx.beginPath();
          ctx.moveTo(-7, -9);
          ctx.lineTo(4, -9);
          ctx.stroke();

          // Body lines (Slate)
          ctx.strokeStyle = "rgba(15, 23, 42, 0.15)";
          for (let row = 0; row < 3; row++) {
            const yOffset = -3 + row * 5;
            ctx.beginPath();
            ctx.moveTo(-7, yOffset);
            ctx.lineTo(7, yOffset);
            ctx.stroke();
          }

          // Small tag / emblem on the document
          ctx.fillStyle = goldAccent;
          ctx.beginPath();
          ctx.arc(6, 11, 2, 0, Math.PI * 2);
          ctx.fill();

          // Text label (Arabic) floating right next to it
          ctx.rotate(-node.angle); // Render text upright
          ctx.fillStyle = "rgba(15, 23, 42, 0.5)";
          ctx.font = "bold 9px Inter, sans-serif";
          ctx.textAlign = "left";
          ctx.fillText(node.label, w / 2 + 4, 3);

        } else {
          // Type 0: Standard Glowing Node
          const pulseScale = 1 + Math.sin(node.pulse) * 0.12;
          const r = node.size * pulseScale;

          // Glow effect
          ctx.shadowColor = "rgba(184, 144, 71, 0.4)";
          ctx.shadowBlur = 12;

          // Outer glowing layer
          ctx.fillStyle = "rgba(184, 144, 71, 0.15)";
          ctx.beginPath();
          ctx.arc(0, 0, r * 1.8, 0, Math.PI * 2);
          ctx.fill();

          // Core
          ctx.fillStyle = goldAccent;
          ctx.beginPath();
          ctx.arc(0, 0, r, 0, Math.PI * 2);
          ctx.fill();

          // Node Text label
          ctx.shadowBlur = 0;
          ctx.fillStyle = "rgba(15, 23, 42, 0.4)";
          ctx.font = "9px JetBrains Mono, monospace";
          ctx.textAlign = "center";
          ctx.fillText(node.label, 0, r + 11);
        }

        ctx.restore();
      });

      // 3. Connect mouse to nearby nodes (Interactive search effect)
      if (mouse.x !== null) {
        nodes.forEach((node) => {
          const dx = node.x - mouse.x;
          const dy = node.y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < mouse.radius) {
            ctx.beginPath();
            ctx.moveTo(mouse.x, mouse.y);
            ctx.lineTo(node.x, node.y);
            ctx.strokeStyle = `rgba(37, 99, 235, ${0.2 * (1 - dist / mouse.radius)})`;
            ctx.lineWidth = 1.2;
            ctx.stroke();
          }
        });

        // Draw a small target pointer at the mouse
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#2563eb";
        ctx.fill();

        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 16, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(37, 99, 235, 0.2)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resizeCanvas);
      canvas.removeEventListener("mousemove", handleMouseMove);
      canvas.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-auto block"
      style={{ background: "transparent" }}
    />
  );
}
