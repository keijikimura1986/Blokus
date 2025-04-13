import React, { useEffect, useRef, useState } from 'react';

const CELL_SIZE = 40;
const BOARD_SIZE = 10;

export default function BlockGame() {
  const canvasRef = useRef(null);
  const [board, setBoard] = useState([]);
  const [turn, setTurn] = useState('');
  const [pieces, setPieces] = useState([]);
  const [selectedId, setSelectedId] = useState(null);

  const fetchBoard = async () => {
    const [boardRes, turnRes, piecesRes] = await Promise.all([
      fetch('http://localhost:8000/board'),
      fetch('http://localhost:8000/turn'),
      fetch('http://localhost:8000/pieces')
    ]);
    const boardData = await boardRes.json();
    const turnData = await turnRes.json();
    const piecesData = await piecesRes.json();
    setBoard(boardData.board);
    setTurn(turnData.turn);
    setPieces(piecesData.pieces);
  };

  const drawBoard = () => {
    const canvas = canvasRef.current;
    if (!canvas || board.length === 0) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < BOARD_SIZE; y++) {
      for (let x = 0; x < BOARD_SIZE; x++) {
        ctx.strokeRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
        const cell = board[y][x];
        if (cell) {
          ctx.fillStyle = cell[1];
          ctx.fillRect(x * CELL_SIZE + 4, y * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8);
        }
      }
    }
  };

  const handleCanvasClick = async (event) => {
    if (selectedId === null) {
      alert('ピースを選択してください');
      return;
    }
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / CELL_SIZE);
    const y = Math.floor((event.clientY - rect.top) / CELL_SIZE);

    const res = await fetch('http://localhost:8000/place', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x, y, piece_id: selectedId })
    });

    if (res.ok) {
      await fetchBoard();
    } else {
      const data = await res.json();
      alert('配置できません: ' + data.detail);
    }
  };

  const renderPieceShape = (shape, color) => {
    const size = 20;
    const offset = 1;
    const grid = new Array(3).fill(null).map(() => new Array(3).fill(false));
    shape.forEach(([dx, dy]) => {
      if (dy + offset >= 0 && dy + offset < 3 && dx + offset >= 0 && dx + offset < 3) {
        grid[dy + offset][dx + offset] = true;
      }
    });
    return (
      <div style={{ display: 'inline-block', margin: '5px' }}>
        <svg width={size * 3} height={size * 3}>
          {grid.map((row, y) => row.map((filled, x) => (
            <rect
              key={`${x}-${y}`}
              x={x * size}
              y={y * size}
              width={size}
              height={size}
              fill={filled ? color : 'white'}
              stroke="black"
            />
          )))}
        </svg>
      </div>
    );
  };

  useEffect(() => {
    fetchBoard();
  }, []);

  useEffect(() => {
    drawBoard();
  }, [board]);

  return (
    <div>
      <h1>ブロック型ボードゲーム（React版）</h1>
      <p>現在のターン: <strong>{turn}</strong></p>
      <canvas
        ref={canvasRef}
        width={CELL_SIZE * BOARD_SIZE}
        height={CELL_SIZE * BOARD_SIZE}
        onClick={handleCanvasClick}
        style={{ border: '1px solid black' }}
      />
      <div style={{ marginTop: '10px' }}>
        <button onClick={fetchBoard}>再読み込み</button>
      </div>
      <h2>残りピース</h2>
      <div>
        {pieces.map(p => (
          <div key={p.player}>
            <h3>{p.player}</h3>
            {p.pieces.map(piece => (
              <div
                key={piece.id}
                onClick={() => setSelectedId(piece.id)}
                style={{ display: 'inline-block', border: selectedId === piece.id ? '2px solid blue' : '1px solid gray' }}
              >
                {renderPieceShape(piece.shape, piece.color)}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
