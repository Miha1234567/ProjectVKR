import pandas as pd
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

image = Image.open('images.jpg')

# Единая функция загрузки всех данных
@st.cache_data
def load_data():
    # Основные данные о зарплатах
    data = pd.read_csv("ПерДанные.csv", index_col=0, encoding='utf-8')
    data_RS = pd.read_csv("data_RS.csv", index_col=0, encoding='utf-8')
    
    # Данные индексов
    data_Ins = pd.read_csv("data_Ins.csv", index_col=0, encoding='utf-8')
    data_Irs = pd.read_csv("data_Irs.csv", index_col=0, encoding='utf-8')
    
    # Преобразование числовых данных
    for df in [data, data_RS, data_Ins, data_Irs]:
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.iloc[:, 1:] = df.iloc[:, 1:].ffill(axis=1).bfill(axis=1)
    
    return {
        'salaries': data,
        'real_salaries': data_RS,
        'nominal_index': data_Ins,
        'real_index': data_Irs
    }

def main():
    plt.switch_backend('Agg')  # Важно для работы в Streamlit
    
    # Загружаем все данные один раз
    data_dict = load_data()
    
    # Навигация
    page = st.sidebar.selectbox(
        "Выбрать исследование:", 
        ["Главная страница",
         "Анализ з/п по отраслям", 
         "Динамика номинальной и реальной з/п по отраслям",
         "Динамика индексов з\п по отраслям",
         "Прогнозирование з/п по отраслям"]
    )

    if page == "Главная страница":
        st.title("Добро пожаловать!")
        st.header("""Проект: Исследование заработной платы в России за период с 2000 по 2023 гг.(по отдельным отраслям) с помощью технологий анализа данных""")
        st.write(
        """    
        ### Представлен анализ заработной платы в России за период с 2000 по 2028 гг.(по отдельным отраслям) #### 
        """)
        st.image(image, width=700)

    elif page == "Анализ з/п по отраслям":
        st.title("📊 Изменения зарплат за 2000-2023 гг. по видам деятельности")
        
        sector = st.selectbox(
            "Выберите отрасль:",
            options=data_dict['salaries']['Economics_section'].unique(),
            index=1
        )
        
        if sector:
            austr = data_dict['salaries'].loc[data_dict['salaries']['Economics_section'].eq(sector)]
            years = [int(col) for col in austr.columns if col.startswith('20')]
            values = austr.filter(regex=r'^20\d{2}$').values[0]
            values2 = values/1000

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(years, values2, linewidth=3)
            ax.set_title(f'Динамика зарплат: {sector.strip()}', fontsize=14)
            ax.set_ylabel('Зарплата, тыс. руб.', fontsize=12)
            ax.set_xlabel('Год', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xticks(np.arange(2000, 2024, 2))
            
            st.pyplot(fig, clear_figure=True)
            st.subheader("Данные")
            df_show = pd.DataFrame({
                'Год': years,
                'Зарплата (руб)': values})
            
            st.dataframe(
                df_show.style.format({"Зарплата (руб)": "{:.0f}"}),
                use_container_width=True
            )

    elif page == "Динамика номинальной и реальной з/п по отраслям":
        st.title("📉 Сравнение номинальной и реальной зарплат (2000-2023 гг.)")
        
        sector = st.selectbox(
            "Выберите отрасль:",
            options=data_dict['salaries']['Economics_section'].unique(),
            index=1
        )
        
        if sector:
            austr = data_dict['salaries'].loc[data_dict['salaries']['Economics_section'].eq(sector)]
            austr_2 = data_dict['real_salaries'].loc[data_dict['real_salaries']['Economics_section'].eq(sector)]
            
            years = [int(col) for col in austr.columns if col.startswith('20')]
            nominal = austr.filter(regex=r'^20\d{2}$').values[0]
            real = austr_2.filter(regex=r'^20\d{2}$').values[0]
            nominal2 = nominal/1000
            real2 = real/1000

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(years, nominal2, linewidth=3, label='Номинальная зарплата')
            ax.plot(years, real2, linewidth=3, label='Реальная зарплата')
            
            ax.set_title(f'Сравнение зарплат: {sector.strip()}', fontsize=14)
            ax.set_ylabel('Зарплата, тыс. руб.', fontsize=12)
            ax.set_xlabel('Год', fontsize=12)
            ax.legend(fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xticks(np.arange(2000, 2024, 2))
            
            st.pyplot(fig, clear_figure=True)
            
            df_show = pd.DataFrame({
                'Год': years,
                'Номинальная (руб)': nominal,
                'Реальная (руб)': real
            })
            
            st.dataframe(
                df_show.style.format({
                    "Номинальная (руб)": "{:.0f}",
                    "Реальная (руб)": "{:.0f}"
                }),
                use_container_width=True
            )

    elif page == "Динамика индексов з\п по отраслям":
        st.title("📝 Индексы номинальной и реальной зарплат (2001-2023 гг.)")
        
        sector = st.selectbox(
            "Выберите отрасль:",
            options=data_dict['nominal_index']['Economics_section'].unique(),
            index=1
        )
        
        if sector:
            austr = data_dict['nominal_index'].loc[data_dict['nominal_index']['Economics_section'].eq(sector)]
            austr_2 = data_dict['real_index'].loc[data_dict['real_index']['Economics_section'].eq(sector)]

            years = [int(col) for col in austr.columns if col.startswith('20') and int(col) >= 2001]
            nominal = austr[[str(year) for year in years]].values[0]
            real = austr_2[[str(year) for year in years]].values[0]

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(years, nominal, 'b-', linewidth=2, label='Индекс номинальной зарплаты')
            ax.plot(years, real, 'r-', linewidth=2, label='Индекс реальной зарплаты')

            ax.set_title(f'Динамика индексов зарплат: {sector.strip()}', fontsize=14)
            ax.set_ylabel('Значение индекса', fontsize=12)
            ax.set_xlabel('Год', fontsize=12)
            ax.legend(fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_xticks(np.arange(2001, 2024, 2))

            st.pyplot(fig, clear_figure=True)
            
            df_show = pd.DataFrame({
                'Год': years,
                'Индекс номинальной зарплаты': nominal,
                'Индекс реальной зарплаты': real
            })
            
            st.dataframe(
                df_show.style.format({
                    'Индекс номинальной зарплаты': '{:.2f}',
                    'Индекс реальной зарплаты': '{:.2f}'
                }),
                use_container_width=True
            )

    elif page == "Прогнозирование з/п по отраслям":
        st.title("📈 Прогноз зарплат на 2024-2028 годы")
        st.markdown("""
        **Методология прогнозирования:**
        - Использованы модели ARIMA и Prophet
        - Прогнозы взвешены по точности моделей
        - Все значения округлены до целых чисел
        """)
    
        # Загрузка прогнозных данных
        forecasts = pd.read_csv("все_отрасли_прогноз_зарплат_2024_2028.csv")
        
        sector = st.selectbox(
            "Выберите отрасль:",
            options=forecasts['Отрасль'].unique(),
            index=0
        )
        
        if sector:
            # Загружаем исторические данные для контекста
            data_per = data_dict['salaries']
            data_rs = data_dict['real_salaries']
            hist_data_per = data_per.loc[data_per['Economics_section'] == sector]
            hist_data_rs = data_rs.loc[data_rs['Economics_section'] == sector]
            
            # Подготавливаем исторические данные
            hist_years = [int(col) for col in hist_data_per.columns if col.startswith('20')]
            nominal_hist = hist_data_per.filter(regex=r'^20\d{2}$').values[0]
            real_hist = hist_data_rs.filter(regex=r'^20\d{2}$').values[0]
            
            # Получаем прогнозные данные
            sector_forecasts = forecasts[forecasts['Отрасль'] == sector]
            forecast_years = sector_forecasts['Год']
            nominal_forecast = sector_forecasts['Прогноз_номинальной_зарплаты']
            real_forecast = sector_forecasts['Прогноз_реальной_зарплаты']
            
            # Создаем объединенный график
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Исторические данные
            ax.plot(hist_years, nominal_hist, 'b-', linewidth=2, label='Историческая номинальная')
            ax.plot(hist_years, real_hist, 'g-', linewidth=2, label='Историческая реальная')
            
            # Прогнозные данные
            ax.plot(forecast_years, nominal_forecast, 'b--', marker='o', markersize=6, 
                   linewidth=2, label='Прогноз номинальной')
            ax.plot(forecast_years, real_forecast, 'g--', marker='s', markersize=6, 
                   linewidth=2, label='Прогноз реальной')
            
            # Разделительная линия между историей и прогнозом
            ax.axvline(x=2023.5, color='gray', linestyle=':', linewidth=2)
            
            # Настройки графика
            ax.set_title(f'Прогноз зарплат: {sector}', fontsize=16)
            ax.set_ylabel('Зарплата, руб.', fontsize=12)
            ax.set_xlabel('Год', fontsize=12)
            ax.legend(fontsize=10, loc='upper left')
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax.set_axisbelow(True)
            
            # Добавляем аннотации с значениями
            for year, nom, real in zip(forecast_years, nominal_forecast, real_forecast):
                ax.text(year, nom, f"{int(nom):,}".replace(",", " "), 
                       ha='center', va='bottom', fontsize=9)
                ax.text(year, real, f"{int(real):,}".replace(",", " "), 
                       ha='center', va='top', fontsize=9)
            
            st.pyplot(fig, clear_figure=True)
            
            # Таблица с прогнозами
            st.subheader("Детали прогноза")
            
            display_df = sector_forecasts[[
                'Год', 
                'Прогноз_номинальной_зарплаты', 
                'Прогноз_реальной_зарплаты',
                'Ошибка_номинальной_зарплаты', 
                'Ошибка_реальной_зарплаты'
            ]].copy()
            
            display_df.columns = [
                'Год', 
                'Номинальная зарплата (руб)', 
                'Реальная зарплата (руб)',
                'Ошибка номинальной (%)', 
                'Ошибка реальной (%)'
            ]
            
            display_df['Номинальная зарплата (руб)'] = display_df['Номинальная зарплата (руб)'].apply(
                lambda x: f"{int(x):,}".replace(",", " "))
            display_df['Реальная зарплата (руб)'] = display_df['Реальная зарплата (руб)'].apply(
                lambda x: f"{int(x):,}".replace(",", " "))
            display_df['Ошибка номинальной (%)'] = display_df['Ошибка номинальной (%)'].apply(
                lambda x: f"{x:.2f}%")
            display_df['Ошибка реальной (%)'] = display_df['Ошибка реальной (%)'].apply(
                lambda x: f"{x:.2f}%")
            
            st.dataframe(
                display_df.set_index('Год'),
                use_container_width=True
            )

if __name__ == "__main__":
    main()
