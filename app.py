import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt


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

    graph, num_value = st.columns(2)
    with graph:
        st.pyplot(fig)
    with num_value:
        st.write(f"### 結果")
        st.write(f"- **回転角度**: {math.degrees(yaw):.2f} 度")
        st.write(f"- **飛距離**: {z:.2f} m")
        st.write(f"- **発射速度**: {v:.2f} m/s")
        st.write(f"- **弾着時の角度**: {impact_angle:.2f} 度")


# ページ作成
st.set_page_config(
    page_title = "計算ソフト",
    layout = "wide", # wideにすると横長なレイアウトに
    initial_sidebar_state = "expanded"
)

label = ['軌道計算', 'coming soon']
choice = st.sidebar.selectbox('セレクタ', label)

match choice:
    case '軌道計算':
        st.sidebar.title("軌道計算")

        MIN_VALUE = 0.00
        MAX_ANGLE = 89.00
        DEFAULT_VALUE = 0.00
        VALUE_STEP = 1.00

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

        try:
            orbit(input_x, input_y, input_h, input_angle)
        except ValueError:
            st.markdown('# 数値を変更してください。')
            st.markdown('# 物理的に不可能です。')

    case 'coming soon':
        st.sidebar.title("coming soon")
