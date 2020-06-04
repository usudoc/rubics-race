from pygame.locals import *
import pygame
import sys

from tilestate import State


window_size = (540, 400)  # 画面サイズの指定
tile_size = [5, 5]

# 1パーツの大きさ
tile_width = 50
tile_height = 50

x_start, y_start = 30, 30
x_gap, y_gap = 5, 5

color_list = [(255, 255, 0), (255, 165, 0), (0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 255), (0, 0, 0)]

N_ACTION = 8  # 行動の種類の数


solved_tile_size = [3, 3]
solved_tile_width = 30
solved_tile_height = 30
x_solved_start = x_start*2 + x_gap*(tile_size[0]-1) + tile_width*tile_size[0] + 60
y_solved_start = y_start + 100
x_solved_gap, y_solved_gap = 3, 3

timer_font_size = 90
timer_x, timer_y = 190, 340
timer_font_color_dict = {
    'measure': (255, 255, 255),
    'pause': (255, 255, 0),
    'dnf': (255, 0, 0)
}


def main():
    pygame.init()  # Pygameを初期化
    screen = pygame.display.set_mode(window_size)  # 画面を作成
    # screen.fill((0, 0, 0, 0))  # 画面の背景色
    pygame.display.set_caption("Rubik's Race")  # タイトルを作成
    # pygame.key.set_repeat(5, 5)

    font = pygame.font.Font(None, timer_font_size)
    timer_font_color = (255, 255, 255)
    clock = pygame.time.Clock()
    timer_sec = 0.0  # 計測中の秒数
    timer_min = 0  # 計測中の分数
    delta_time = 0.0
    is_started = False  # タイマーのカウントが始まっているかどうか
    is_reset = True  # タイマーがリセットされた状態かどうか
    start_ticks = 0.0

    max_pause_ticks = 5.0  # 計測開始までの最大カウントダウン
    pause_ticks = 0.0  # カウントダウン中の経過時間

    ts = State(n_action=N_ACTION)  # ボードオブジェクトを作成
    n_tile_ver, n_tile_hor = len(ts.board), len(ts.board[0])

    while True:  # 画面やイベントの更新処理
        # clock.tick(60)
        screen.fill((0, 0, 0, 0))  # 画面の背景色
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, x_start * 2 + tile_width * tile_size[0] + x_gap * (tile_size[0] - 1), y_start * 2 + tile_height * tile_size[1] + y_gap * (tile_size[1] - 1)))  # 盤面の土台背景

        board = ts.board
        solved_board = ts.solved_state
        for i in range(n_tile_ver):
            for j in range(n_tile_hor):
                x = j * (tile_width + x_gap) + x_start
                y = i * (tile_height + y_gap) + y_start
                pygame.draw.rect(screen, color_list[board[i, j]], (x, y, tile_width, tile_height))

        for i in range(solved_tile_size[1]):
            for j in range(solved_tile_size[0]):
                x = j * (solved_tile_width + x_solved_gap) + x_solved_start
                y = i * (solved_tile_height + y_solved_gap) + y_solved_start
                pygame.draw.rect(screen, color_list[int(solved_board[i, j])], (x, y, solved_tile_width, solved_tile_height))

        # タイマーが計測されてからどのくらい経ったか計算
        if is_started:
            # 計測開始前のカウントダウン中
            if is_reset:
                pause_timer = (pygame.time.get_ticks() - pause_ticks) / 1000
                # 計測開始前の停止時間が許容時間より超えていた場合、強制的に計測開始
                if pause_timer > max_pause_ticks:
                    start_ticks = pygame.time.get_ticks()  # 計測開始時点
                    timer_font_color = timer_font_color_dict['measure']
                    is_reset = False
            # 計測中
            else:
                timer = (pygame.time.get_ticks() - start_ticks) / 1000
                timer_sec = timer % 60.0
                timer_min = int(timer / 60.0)

        # タイマーの表示
        timer_str = ''
        # 60秒以内であれば分数は表示しない
        if timer_min == 0:
            timer_str = '{:.5}'.format(timer_sec)
        # 60秒を過ぎたら分数表示を追加
        else:
            # 秒数が一桁であれば前に0を追加
            if timer_sec < 10.0:
                timer_str = '{}:0{:.4}'.format(timer_min, timer_sec)
            else:
                timer_str = '{}:{:.5}'.format(timer_min, timer_sec)
        timer_text = font.render(timer_str, True, timer_font_color)  # 描画する文字列の設定
        screen.blit(timer_text, [timer_x, timer_y])

        for event in pygame.event.get():  # イベントを取得
            # マウスクリックで画像移動
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                # print('x =', x, 'y =', y)
                pos = [x, y]

                tile_x = (x - x_start + x_gap / 2) / (tile_width + x_gap)
                tile_y = (y - y_start + y_gap / 2) / (tile_height + y_gap)
                # print(tile_x, tile_y)
                # print(int(tile_x), int(tile_y))
                # ボードの範囲内をクリックした場合だけactionを呼び出す
                if (0 <= tile_x and tile_x < tile_size[0]) and (0 <= tile_y and tile_y < tile_size[1]):
                    # 計測中だけ動かせる
                    if is_started and not(is_reset):
                        ts.action(pos=[int(tile_x), int(tile_y)], click_mode=True)
            # ×ボタンや、終了イベントが発生した時の処理
            if event.type == QUIT:
                pygame.quit()  # これを書いていないと、例外やエラーで終了する
                sys.exit()
            # イベントの種類がキーダウンだったら
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:  # 押されたキーがスペースキーだったら
                    # print('input space')
                    # タイマーが始まっている（計測中）状態で計測を停止する
                    if is_started:
                        if is_reset:
                            # paused_ticks = timer  # カウントダウン中に経過した時間
                            start_ticks = pygame.time.get_ticks()  # 計測開始時点
                            timer_font_color = timer_font_color_dict['measure']
                            is_reset = False
                        else:
                            # 完成状態である場合
                            if ts.is_solved():
                                print('FINISHED')
                            # 未完成な場合
                            else:
                                print('DNF')
                                timer_font_color = timer_font_color_dict['dnf']
                            is_started = False
                            print(timer_str)
                    # タイマーが始まっていない かつ リセットされている（計測開始直前）状態で計測を開始する
                    elif not(is_started) and is_reset:
                        # 開始時にスクランブルを実行
                        ts.scramble()
                        ts.solved_scramble()
                        # タイマーの計測
                        # start_ticks = pygame.time.get_ticks()
                        pause_ticks = pygame.time.get_ticks()  # カウントダウン中の経過時間の計測開始時点
                        timer_font_color = timer_font_color_dict['pause']
                        is_started = True
                        # is_reset = False
                    # タイマーが始まっていない かつ リセットされていない（計測停止直後）状態で計測タイムを初期化する
                    elif not(is_started) and not(is_reset):
                        timer_sec, timer_min = 0.0, 0
                        timer_font_color = timer_font_color_dict['measure']
                        is_reset = True

        pygame.display.update()


main()
