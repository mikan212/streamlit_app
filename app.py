import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1316290140167209011/5LiO-XQW7G15UI0F1C6cB16-aS9FkiqygqL2r5HW8uV77v9DBa75uMDpKrrar0dkSYoz'


def fb_send(send_contents, img):
    data = {
        "content": send_contents
    }
    files = {
        "file": ("image.png", img, "image/png")
    }
    response = requests.post(WEBHOOK_URL, data=data, files=files)

    if response.status_code == 204 or response.status_code == 200:
        st.success("フィードバックを送信しました！ご協力ありがとうございます。")
    else:
        st.error("送信に失敗しました。再度お試しください。")


# 軌道を計算する関数
def trajectory(x_vals, v, theta, h_r, g):
    return h_r / 1000 + x_vals * math.tan(theta) - (g * x_vals**2) / (2 * v**2 * math.cos(theta)**2)


def orbit(r_x, r_y, r_h, angle):
    g = 9.80665  # 重力加速度
    g_x, g_y = 0.35, 3.15  # タルの座標

    # 計算
    x, y = r_x - g_x, r_y - g_y
    z = math.sqrt(x ** 2 + y ** 2)  # ロボットからタルまでの距離
    yaw = math.acos(x / z)  # 水平方向の回転角
    theta = math.radians(angle)  # 仰角をラジアンに変換
    h = (345 - r_h) / 1000  # タルの高さ [m]

    # 初速を計算
    v = math.sqrt((g * z ** 2) / (2 * math.cos(theta) ** 2 * (z * math.tan(theta) - h)))

    v_x = v * math.cos(theta)  # 水平速度
    v_y = v * math.sin(theta) - g * x / v_x  # 垂直速度（時間 t = x / v_x を利用
    impact_angle = math.degrees(math.atan2(v_y, v_x))

    # 軌道描画用データ生成
    x_vals = np.linspace(0, z, 500)  # 0 から z までの範囲で 500 点を計算
    y_vals = trajectory(x_vals, v, theta, r_h, g)

    # 軌跡の描画
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_vals, y_vals, label="Projectile Trajectory", color="blue")
    ax.scatter([z], [0.345], color="red", label="Target", zorder=5)  # タルの座標を描画
    ax.axhline(0, color="black", linewidth=0.5, linestyle="--")  # 地面
    ax.set_title("Trajectory")
    ax.set_xlabel("Altitude (m)")
    ax.set_ylabel("Flying distance (m)")
    ax.legend()
    ax.grid()

    st.pyplot(fig)
    st.write(f"### 結果")
    value1, value2, value3, value4 = st.columns(4)
    with value1:
        st.write(f"- **回転角度**: {math.degrees(yaw):.2f} 度")
    with value2:
        st.write(f"- **飛距離**: {z:.2f} m")
    with value3:
        if not check_box:
            st.write(f"- **発射速度**: {v:.2f} m/s")
        elif v >= 331:
            st.write(f"- **発射速度**: {v * 1000 / 3600:.2f}km/h")
            st.write(f"- **発射速度**: マッハ{v / 340:.2f}")
        else:
            st.write(f"- **発射速度**: {v * 1000 / 3600:.2f} km/h")
    with value4:
        st.write(f"- **到達時の角度**: {impact_angle:.2f} 度")


def clear_text_area():
    st.session_state.text_area_content = ""  # セッションステートをクリア


# ページ作成
st.set_page_config(
    page_title="計算ソフト",
    layout="wide",    # wideにすると横長なレイアウトに
    initial_sidebar_state="expanded"
)

label = ['軌道計算', 'フィードバック', '更新情報', 'coming soon']
choice = st.sidebar.selectbox('メニュー', label)

match choice:
    case '軌道計算':
        MIN_VALUE = 0.00
        MAX_ANGLE = 89.00
        DEFAULT_VALUE = 0.00
        VALUE_STEP = 1.00

        st.sidebar.title("軌道計算")

        col1, col2 = st.sidebar.columns(2)

        with col1:
            input_x = st.number_input(
                'ロボットのX座標[m]',
                step=VALUE_STEP,
                value=DEFAULT_VALUE,
                min_value=MIN_VALUE
            )

        with col2:
            input_y = st.number_input(
                'ロボットのY座標[m]',
                step=VALUE_STEP,
                value=DEFAULT_VALUE,
                min_value=MIN_VALUE
            )

        input_h = st.sidebar.number_input(
            '発射機構の高さ[mm]',
            step=VALUE_STEP,
            value=DEFAULT_VALUE,
            min_value=MIN_VALUE
        )

        input_angle = st.sidebar.number_input(
            '発射角度[度]',
            step=VALUE_STEP,
            value=DEFAULT_VALUE,
            min_value=MIN_VALUE,
            max_value=MAX_ANGLE
        )

        check_box = st.sidebar.checkbox('km/h表示')

        try:
            orbit(input_x, input_y, input_h, input_angle)
        except ValueError:
            st.markdown('# 数値を変更してください。')
            st.markdown('# 物理的に不可能です。')
        except ZeroDivisionError:
            st.markdown('# 射出角度を変更してください。')

    case 'フィードバック':
        if "text_area_content" not in st.session_state:
            st.session_state.text_area_content = ""
        st.markdown('## フィードバックを送信する')
        st.markdown('##### ※個人情報など個人を特定できる情報を含めないでください。')
        st.text_area(
            label="ここにテキストを入力してください",
            value=st.session_state.text_area_content,  # セッションステートの値を使用
            key="text_area_content",
            height=350
        )
        fb_img = st.file_uploader(
            label="スクリーンショットを追加していただくと、フィードバックを把握するうえで役立ちます。",
            type=['jpg', 'jpeg', 'png'],
        )
        col1, col2 = st.columns(2)
        with col1:
            clear_btn = st.button('クリア', on_click=clear_text_area, use_container_width=True)
        with col2:
            feedback_btn = st.button('送信', type='primary', icon=":material/send:", use_container_width=True)

        if feedback_btn:
            fb_send(st.session_state.text_area_content, fb_img)

    case '更新情報':
        with st.expander("**軌道計算機能の細かい修正-更新日:2024/12/11**"):
            st.markdown('''
                速度の表記に[km/h]を追加しました。単位はチェックボックスにて随時変更可能です。\n
                グラフを表示する仕様を変更し、継続的にグラフが変化するようにしました。\n
                数値を変えるたびに毎度ボタンを押す必要がなくなりました。
            ''')
        with st.expander("**フィードバック機能の追加-更新日:2024/12/11**"):
            st.markdown('''
                バグ修正や機能向上を目的としたフィードバック機能を追加しました。\n
                本機能ではテキストの送信と画像ファイルの添付ができるようになっています。\n
                バグなど問題が見つかった際はご利用ください。
            ''')
        with st.expander("**更新情報の掲示-更新日:2024/12/11**"):
            st.markdown('''
                バグ修正や新機能を追加した際には、この更新情報機能でお知らせします。\n
            ''')

    case 'coming soon':
        st.sidebar.title("coming soon")
