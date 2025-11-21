import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def make_weather_plot(hours, temps, wind_speeds, precipitation, resort_name, elevation, output_path):
    plt.figure(figsize=(12, 6))

    # --------------------------
    # 1) ОСАДКИ — СТОЛБИКИ
    # --------------------------
    plt.bar(
        hours,
        precipitation,
        width=0.6,
        alpha=0.4,
        label="Осадки (мм)",
    )

    # Подписи осадков над столбиками
    for h, p in zip(hours, precipitation):
        if p > 0:
            plt.text(h, p + 0.1, f"{p}", ha="center", va="bottom", fontsize=8)

    # --------------------------
    # 2) ТЕМПЕРАТУРА — ЛЕВАЯ ОСЬ
    # --------------------------
    plt.plot(hours, temps, linewidth=2, label="Температура (°C)")

    plt.ylabel("Температура (°C)")
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(8))

    # --------------------------
    # 3) ВЕТЕР — ПРАВАЯ ОСЬ
    # --------------------------
    ax2 = plt.gca().twinx()
    ax2.plot(hours, wind_speeds, linewidth=2, linestyle="--", label="Ветер (м/с)")
    ax2.set_ylabel("Ветер (м/с)")
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(8))

    # --------------------------
    # Ось X — часы
    # --------------------------
    plt.xticks(hours, rotation=45, fontsize=9)
    plt.xlabel("Часы")

    # --------------------------
    # Заголовок
    # --------------------------
    plt.title(f"Прогноз для {resort_name} (высота {elevation} м) — 24 часа")

    # --------------------------
    # Легенды
    # --------------------------
    # Объединяем легенды с двух осей
    lines1, labels1 = plt.gca().get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()