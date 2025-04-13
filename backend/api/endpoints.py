from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from block_game import Player, Board, PIECE_COLORS

router = APIRouter()

# ゲーム状態の初期化
class GameState:
    def __init__(self):
        self.board = Board(10, 10)
        self.players = [Player("Player1", PIECE_COLORS[0]), Player("Player2", PIECE_COLORS[1])]
        self.current_turn = 0

    def get_current_player(self):
        return self.players[self.current_turn]

    def get_piece_by_id(self, player, piece_id):
        for piece in player.pieces:
            if piece.id == piece_id:
                return piece
        return None

    def place_piece(self, x: int, y: int, piece_id: int):
        player = self.get_current_player()
        piece = self.get_piece_by_id(player, piece_id)
        if piece is None:
            return False
        if self.board.place_piece(x, y, piece, player.name):
            player.pieces = [p for p in player.pieces if p.id != piece_id]
            self.current_turn = (self.current_turn + 1) % len(self.players)
            return True
        return False

    def get_board_state(self):
        return self.board.grid

    def get_pieces(self):
        return [
            {"player": p.name, "pieces": [
                {"shape": piece.shape, "id": piece.id, "color": piece.color} for piece in p.pieces
            ]} for p in self.players
        ]

    def get_turn(self):
        return self.get_current_player().name

# グローバルなゲーム状態
state = GameState()

# リクエストモデル
class PlaceRequest(BaseModel):
    x: int
    y: int
    piece_id: Optional[int] = None

# エンドポイント定義
@router.get("/board")
def get_board():
    return {"board": state.get_board_state()}

@router.get("/pieces")
def get_pieces():
    return {"pieces": state.get_pieces()}

@router.get("/turn")
def get_turn():
    return {"turn": state.get_turn()}

@router.post("/place")
def place_piece(req: PlaceRequest):
    if req.piece_id is None:
        raise HTTPException(status_code=400, detail="piece_id is required")
    success = state.place_piece(req.x, req.y, req.piece_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot place piece")
    return {"result": "ok"}
