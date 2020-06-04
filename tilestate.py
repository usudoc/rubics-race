import numpy as np
import random
import collections


class State(object):

    TILE_TYPES = [
        'Y',  # 0: イエロー
        'O',  # 1: オレンジ
        'B',  # 2: ブルー
        'R',  # 3: レッド
        'G',  # 4: グリーン
        'W',  # 5: ホワイト
        'F'   # 6: フリータイル
    ]
    INIT_BOARD = np.array([
        [6, 0, 0, 0, 0],  # "FYYYY"
        [1, 2, 3, 4, 5],  # "OBRGW"
        [1, 2, 3, 4, 5],  # "OBRGW"
        [1, 2, 3, 4, 5],  # "OBRGW"
        [1, 2, 3, 4, 5]   # "OBRGW"
    ])

    SOLVED_SIZE = [3, 3]

    def __init__(self, n_action=8):
        self.n_action = n_action
        self.board = self.INIT_BOARD
        self.scramble(n_scramble=30)
        self.solved_state = np.zeros(tuple(self.SOLVED_SIZE))  # ゴールとなる状態
        self.solved_scramble()  # ゴールの状態をスクランブルして決定
        # print(' - solved_state - ')
        # print(self.solved_state)
        # print(self._get_free_spot())

    # 行動は横方向→縦方向の順番
    # 行える行動のうち
    # 左から順に 0,1,2,3
    # 上から順に 4,5,6,7
    def action(self, action=0, pos=None, click_mode=False):
        if self._can_action(action, pos, click_mode):
            # クリックによって行動操作を行う場合
            if click_mode:
                action = self._change_pos_to_action(pos=pos)
        else:
            # print('Please select correct action.')
            return
        self._move_tile(action)

    def _move_tile(self, action=0):
        free_spot = self._get_free_spot()
        free_x, free_y = free_spot
        # print(free_x, free_y)
        # シフトする回数n
        # x軸方向のシフト
        if action <= 3:
            n_shift = -1 if free_x <= action else 1
            start_x = min(free_x, action)
            end_x = max(free_x+1, action+2)
            # print('start_x', start_x)
            # print('end_x', end_x)
            # print(self.board[free_y, start_x:end_x])
            # print(np.roll(self.board[free_y, start_x:end_x], n_shift))
            self.board[free_y, start_x:end_x] = np.roll(self.board[free_y, start_x:end_x], n_shift)
        # y軸方向のシフト
        else:
            action_y = action - 4
            n_shift = -1 if free_y <= action_y else 1
            start_y = min(free_y, action_y)
            end_y = max(free_y+1, action_y+2)
            # print('start_y', start_y)
            # print('end_y', end_y)
            # print(self.board[start_y:end_y, free_x])
            # print(np.roll(self.board[start_y:end_y, free_x], n_shift))
            self.board[start_y:end_y, free_x] = np.roll(self.board[start_y:end_y, free_x], n_shift)

        # print(self.board)

    def scramble(self, n_scramble=30):
        scramble_list = []
        for i in range(n_scramble):
            scramble_list.append(random.randint(0, 7))
        # print('* scramble: ', scramble_list)
        for action in scramble_list:
            self._move_tile(action)

    # ゴールの状態を表す
    def solved_scramble(self):
        _solved_state = self.solved_state
        # 色の種類の範囲でサイコロを振る

        for i in range(len(_solved_state)):
            for j in range(len(_solved_state[0])):
                _solved_state[i, j] = random.randint(0, 5)
        unique_arr = np.unique(_solved_state, return_counts=True)
        max_counts = max(unique_arr[1])
        # もし一色のタイルの最大個数よりも多くなってしまったらスクランブルし直す
        if max_counts > 4:
            self.solved_scramble()
        else:
            self.solved_state = _solved_state
            # return _solved_state

    # 現在のボードの状態がゴールの状態と一致するかどうか
    def is_solved(self):
        if (self.board[1:4, 1:4] == self.solved_state).all():
            return True
        else:
            return False

    # フリータイルの座標を取得
    def _get_free_spot(self):
        # 座標としたら[x, y]の形になる
        return [np.where(self.board == 6)[1][0], np.where(self.board == 6)[0][0]]

    # 現在のボード上の状態を取得
    def _get_cur_board(self):
        return self.board

    # 選択されたタイルの位置が実際に行動を行うことができるかどうかを判定して返す
    def _can_action(self, action, pos=None, click_mode=False):
        free_spot = self._get_free_spot()
        # クリックによる操作である場合
        if click_mode:
            # 選択されたタイルのx座標かy座標のどちらか一方がフリータイルの座標と一致する場合
            if bool(pos[0] == free_spot[0]) != bool(pos[1] == free_spot[1]):
                return True
            else:
                return False
        # 行動を直接入力によって受け取るような操作の場合
        else:
            # 選択された行動が望ましいものである場合
            if action < self.n_action:
                return True
            else:
                return False

    # 座標pos([x, y])から行動値(int)に変換
    # if bool(pos[0] == free_spot[0]) != bool(pos[1] == free_spot[1]): がTrueであることが前提条件
    def _change_pos_to_action(self, pos):
        action = None
        free_spot = self._get_free_spot()
        if pos[1] == free_spot[1]:
            diff = 1 if pos[0] > free_spot[0] else 0  # 選択された座標がフリースポットよりも大きかった場合1タイル分の座標を加味
            action = pos[0] - diff
        else:
            diff = 1 if pos[1] > free_spot[1] else 0  # 選択された座標がフリースポットよりも大きかった場合1タイル分の座標を加味
            action = pos[1] + (len(self.board[0]) - 1) - diff

        return action

