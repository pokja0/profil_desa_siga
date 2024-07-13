from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import polars as pl
from shinywidgets import output_widget, render_widget  
import plotly.express as px

import pandas as pd
from great_tables import GT, exibble, loc, style
from ipyleaflet import Map 
import folium
import ipyleaflet

import math

daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]

data_poktan = pl.read_csv("data/profil_poktan.csv")

#data_poktan = pl.read_csv("data/profil_poktan.csv")
    
piggy_bank = ui.HTML(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-piggy-bank " style="fill:currentColor;height:100%;" aria-hidden="true" role="img" ><path d="M5 6.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0zm1.138-1.496A6.613 6.613 0 0 1 7.964 4.5c.666 0 1.303.097 1.893.273a.5.5 0 0 0 .286-.958A7.602 7.602 0 0 0 7.964 3.5c-.734 0-1.441.103-2.102.292a.5.5 0 1 0 .276.962z"></path>\n<path fill-rule="evenodd" d="M7.964 1.527c-2.977 0-5.571 1.704-6.32 4.125h-.55A1 1 0 0 0 .11 6.824l.254 1.46a1.5 1.5 0 0 0 1.478 1.243h.263c.3.513.688.978 1.145 1.382l-.729 2.477a.5.5 0 0 0 .48.641h2a.5.5 0 0 0 .471-.332l.482-1.351c.635.173 1.31.267 2.011.267.707 0 1.388-.095 2.028-.272l.543 1.372a.5.5 0 0 0 .465.316h2a.5.5 0 0 0 .478-.645l-.761-2.506C13.81 9.895 14.5 8.559 14.5 7.069c0-.145-.007-.29-.02-.431.261-.11.508-.266.705-.444.315.306.815.306.815-.417 0 .223-.5.223-.461-.026a.95.95 0 0 0 .09-.255.7.7 0 0 0-.202-.645.58.58 0 0 0-.707-.098.735.735 0 0 0-.375.562c-.024.243.082.48.32.654a2.112 2.112 0 0 1-.259.153c-.534-2.664-3.284-4.595-6.442-4.595zM2.516 6.26c.455-2.066 2.667-3.733 5.448-3.733 3.146 0 5.536 2.114 5.536 4.542 0 1.254-.624 2.41-1.67 3.248a.5.5 0 0 0-.165.535l.66 2.175h-.985l-.59-1.487a.5.5 0 0 0-.629-.288c-.661.23-1.39.359-2.157.359a6.558 6.558 0 0 1-2.157-.359.5.5 0 0 0-.635.304l-.525 1.471h-.979l.633-2.15a.5.5 0 0 0-.17-.534 4.649 4.649 0 0 1-1.284-1.541.5.5 0 0 0-.446-.275h-.56a.5.5 0 0 1-.492-.414l-.254-1.46h.933a.5.5 0 0 0 .488-.393zm12.621-.857a.565.565 0 0 1-.098.21.704.704 0 0 1-.044-.025c-.146-.09-.157-.175-.152-.223a.236.236 0 0 1 .117-.173c.049-.027.08-.021.113.012a.202.202 0 0 1 .064.199z"></path></svg>'
)
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Dashboard", 
        ui.layout_column_wrap(
            ui.input_selectize("pilih_kab", "Pilih Kabupaten", choices=[], multiple=False),
            ui.input_selectize("pilih_kec", "Pilih Kecamatan", choices=[], multiple=False),
            ui.input_selectize("pilih_desa", "Pilih Desa/Kelurahan", choices=[], multiple=False),
            ui.input_selectize("pilih_bulan", "BULAN", 
                                  choices=daftar_bulan[:3])
        ),
        ui.input_action_button(
            "action_button", "Tampilkan Data"
        ),
        ui.br(),
        ui.h6(
            ui.output_text("judul_wilayah"),
            class_="text-lg-center text-left",
        ),
        ui.br(),
        ui.navset_card_pill(
            ui.nav_panel(
                "Profil",
                ui.layout_column_wrap(
                    ui.card(
                        output_widget("mapping")
                    ),
                    ui.card(
                        ui.layout_column_wrap(
                            ui.output_ui("kepemilikan_poktan"),
                            ui.output_ui("profil_wilayah")
                        )
                    )
                ),
                ui.layout_column_wrap(
                    ui.card(
                        output_widget("grafik_piramida")
                    ),
                    ui.card(
                        ui.output_data_frame("tabel_piramida")
                    )
                ),
                ui.layout_column_wrap(
                    ui.card(
                        ui.output_data_frame("df")
                    )
                )
            ),
            ui.nav_panel(
                "Keluarga Berencana",
                    ui.layout_column_wrap(
                        ui.output_ui("vb_unmet_need"),
                        ui.value_box(
                            "KPI Title",
                            "$1 Billion Dollars",
                            "Up 30% VS PREVIOUS 30 DAYS",
                            showcase=piggy_bank,
                            theme="text-green",
                            showcase_layout="top right",
                            full_screen=True,
                        ),
                        ui.value_box(
                            "KPI Title",
                            "$1 Billion Dollars",
                            "Up 30% VS PREVIOUS 30 DAYS",
                            showcase=piggy_bank,
                            theme="purple",
                            showcase_layout="bottom",
                            full_screen=True,
                        ),
                    )
            ),
            ui.nav_panel(
                "Stunting"
            ),
        )
        
    ),
    ui.nav_panel(
        "Download Data", "ini"
    ),
    title="Desa Profil"
)


def server(input, output, session):

    @reactive.effect
    def _():
        daftar_kab = data_poktan['KABUPATEN'].unique()
        daftar_kab = list(daftar_kab)
        daftar_kab.insert(0, "SEMUA KABUPATEN")
        ui.update_selectize(
            "pilih_kab",
            choices=daftar_kab
        )

    
    @reactive.effect
    def _():
        kondisi = input.pilih_kab()
        if kondisi == "SEMUA KABUPATEN":
            daftar_kec = ["SEMUA KECAMATAN"]
        else:
            daftar_kec = (data_poktan
                .select(["KABUPATEN","KECAMATAN"])
                .filter(data_poktan['KABUPATEN'] == input.pilih_kab())
                .select("KECAMATAN"))
            daftar_kec = daftar_kec["KECAMATAN"].unique()
            daftar_kec = list(daftar_kec)
            daftar_kec.insert(0, "SEMUA KECAMATAN")
        ui.update_selectize(
            "pilih_kec",
            choices=daftar_kec
        )

    @reactive.effect
    def _():
        if input.pilih_kec() == "SEMUA KECAMATAN":
            daftar_desa = ["SEMUA DESA/KELURAHAN"]
        else:
            daftar_desa = (data_poktan
                .select(["KECAMATAN","KELURAHAN"])
                .filter(data_poktan['KECAMATAN'] == input.pilih_kec())
                .select("KELURAHAN"))
            daftar_desa = list(daftar_desa["KELURAHAN"])
            daftar_desa.insert(0, "SEMUA DESA/KELURAHAN")
            
        ui.update_selectize(
            "pilih_desa",
            choices=daftar_desa
        )

    

    @render.text
    @reactive.event(input.action_button)
    def judul_wilayah():
        profil = "PROFIL"
        bulan = input.pilih_bulan()
        if input.pilih_kab() == "SEMUA KABUPATEN":
            teks = profil + " - PROVINSI SULAWESI BARAT - " + bulan
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() == "SEMUA KECAMATAN":
            teks = profil + " - KABUPATEN " + input.pilih_kab() + " - " + bulan
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            teks = profil + " - KECAMATAN " + input.pilih_kec() + " - " + bulan
        else:
            teks = profil + " - DESA/KELURAHAN " + input.pilih_desa() + " - " + bulan

        return "\n" + teks

    val_judul = reactive.value(0)
    @reactive.effect
    def _():
        if input.pilih_kab() == "SEMUA KABUPATEN":
            teks = " - PROVINSI SULAWESI BARAT"
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() == "SEMUA KECAMATAN":
            teks = " - KABUPATEN " + input.pilih_kab()
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            teks = " - KECAMATAN " + input.pilih_kec()
        else:
            teks = "DESA/KELURAHAN" + input.pilih_desa()

        val_judul.set(teks)

    val_kab = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        kondisi_input = input.pilih_kab()
        if kondisi_input == "SEMUA KABUPATEN":
            filter_kabupaten = data_poktan.select("KABUPATEN").unique().to_series().to_list()
        else:
            filter_kabupaten = [input.pilih_kab()]
        val_kab.set(filter_kabupaten)

    
    val_kec = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        filter_kabupaten = val_kab.get()
        kondisi_input = input.pilih_kec()
        if kondisi_input == "SEMUA KECAMATAN":
            filter_kecamatan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(data_poktan.select("KECAMATAN").unique().to_series().to_list()))
            filter_kecamatan = filter_kecamatan.select("KECAMATAN").unique().to_series().to_list()
        else:
            filter_kecamatan = [input.pilih_kec()]
        val_kec.set(filter_kecamatan)

    val_desa = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        kondisi_input = input.pilih_desa()
        if kondisi_input == "SEMUA DESA/KELURAHAN":
            filter_desa = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(data_poktan.select("KELURAHAN").unique().to_series().to_list()))
            filter_desa = filter_desa.select("KELURAHAN").unique().to_series().to_list()
        else:
            filter_desa = [input.pilih_desa()]

        val_desa.set(filter_desa)


    ### Profil

    @render.data_frame
    #@reactive.event(input.action_button)
    def df():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        data_poktan = pl.read_csv("data/profil_poktan.csv")
            
        data_poktan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(filter_desa))
        return render.DataGrid(data_poktan)  
    
    @render_widget  
    @reactive.event(input.action_button)
    def mapping():
        return ipyleaflet.Map(zoom=2)
    
    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_poktan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        data_poktan = pl.read_csv("data/profil_poktan.csv")
            
        data_poktan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(filter_desa))
        # List kolom yang akan dihitung
        columns_to_count = ["Kampung KB", "Rumah DataKU", "BKB", "BKR", "BKL", "UPPKA", "PIK-R"]

        # Menghitung jumlah "Ada" untuk setiap kolom
        counts = [data_poktan[col].str.count_matches("Ada").sum() for col in columns_to_count]

        # Menghitung jumlah desa unik berdasarkan kombinasi KECAMATAN dan KELURAHAN
        unique_desa = data_poktan.select(["KECAMATAN", "KELURAHAN"]).unique().shape[0]

        # Membuat DataFrame hasil
        results = pl.DataFrame({
            "Kategori": ["Desa/Kelurahan"] + columns_to_count,
            "Jumlah": [unique_desa] + counts
        })
        return GT(results)
    
    @render.ui
    @reactive.event(input.action_button)
    def profil_wilayah():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        data_sd = pl.read_csv("data/profil_sumber_daya.csv")
        
        data_sd = data_sd.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(filter_desa))

        # Menghitung jumlah total untuk LUAS_WILAYAH dan JUMLAH_PENDUDUK
        total_luas_wilayah = round(data_sd["LUAS_WILAYAH"].sum(),2)
        total_jumlah_penduduk = int(data_sd["JUMLAH_PENDUDUK"].sum())

        # Menghitung rata-rata untuk KEPADATAN_PENDUDUK
        avg_kepadatan_penduduk = round(total_jumlah_penduduk/total_luas_wilayah, 2)

        # Membuat DataFrame hasil
        results = pl.DataFrame({
            "Variable": ["Luas Wilayah", "Jumlah Penduduk", "Kepadatan Penduduk"],
            "Nilai": [total_luas_wilayah, total_jumlah_penduduk, avg_kepadatan_penduduk]
        })
        return GT(results)
    
    @render_widget
    @reactive.event(input.action_button)
    def grafik_piramida():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        
        kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
        kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                                    pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_lk = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Laki-laki"
        )

        kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
        kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_pr = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Perempuan"
        )

        df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

        # Daftar kategori usia
        ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
            "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
            "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
            "65 - 69", "70 - 74", "75+"]

        # Menghitung berapa kali daftar ku perlu diulang
        repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
        repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

        # Menambahkan kolom kategori umur
        df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])

        y_age = df_horizontal_join['Kategori_Umur'] 
        x_M = df_horizontal_join['Laki-laki'] 
        x_F = df_horizontal_join['Perempuan'] * -1

        if max(x_M) >= max(x_F):
            maks = max(x_M)
        else:
            maks = max(x_F)

        def round_up_to_nearest(number, base):
            return base * math.ceil(number / base)

        def auto_round_up(number):
            if number == 0:
                return 0
            base = 10 ** (len(str(number)) - 1)
            return round_up_to_nearest(number, base)

        maks1 = auto_round_up(maks)
        maks2 = auto_round_up(int(maks - (maks * 1 / 3)))
        maks3 = auto_round_up(int(maks - (maks * 2 / 3)))

        tick_vals = [-maks1, -maks2, -maks3, 0, maks1, maks2, maks3]
        tick_str = [str(abs(value)) for value in tick_vals]

        import plotly.graph_objects as gp
        # Creating instance of the figure 
        fig = gp.Figure() 
        

        # Adding Female data to the figure 
        fig.add_trace(gp.Bar(y = y_age, x = x_F, 
                            name = 'Perempuan', orientation = 'h',
                            marker=dict(color='#ffc107'),
                            hovertemplate='Perempuan Umur %{y}<br>Jumlah: %{customdata}<extra></extra>',
                            customdata=[abs(x) for x in x_F]
                            )) 

        # Adding Male data to the figure 
        fig.add_trace(gp.Bar(y= y_age, x = x_M,  
                            name = 'Laki-laki',  
                            orientation = 'h',
                            marker=dict(color='#0d6efd'),
                            hovertemplate='Laki-laki Umur %{y}<br> %{x}<extra></extra>')) 

        
        # Updating the layout for our graph 
        fig.update_layout(title={
                            'text': 'Piramida Penduduk ' + str(val_judul.get()),
                            'y': 0.98,  # Adjust this value to move the title up or down
                            'x': 0.5,  # Centered horizontally
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        title_font_size = 18, barmode = 'relative', 
                        bargap = 0.0, bargroupgap = 0, 
                        xaxis = dict(tickvals = tick_vals, 
                                    ticktext = tick_str, 
                                    title = 'Jumlah', 
                                    title_font_size = 14),
                        legend=dict(
                                orientation='h',
                                yanchor='bottom',
                                y=-0.3,  # Adjust this value to move the legend up or down
                                xanchor='center',
                                x=0.5
                        ),
                        plot_bgcolor='#f6f8fa',  # Set background color of the plot area to green
                        paper_bgcolor='#f6f8fa'  # Set background color of the entire canvas to green 
        )
        
        return fig

    @render.data_frame
    @reactive.event(input.action_button)
    def tabel_piramida():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        
        kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
        kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                                    pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_lk = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Laki-laki"
        )

        kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
        kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_pr = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Perempuan"
        )

        df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

        # Daftar kategori usia
        ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
            "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
            "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
            "65 - 69", "70 - 74", "75+"]

        # Menghitung berapa kali daftar ku perlu diulang
        repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
        repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

        # Menambahkan kolom kategori umur
        df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])
        df_horizontal_join = df_horizontal_join.select('Kategori_Umur', 'Perempuan', 'Laki-laki')


        df_horizontal_join = df_horizontal_join.with_columns(
            (pl.col("Perempuan") + pl.col("Laki-laki")).alias("Total")
        )
        return render.DataGrid(df_horizontal_join)
    ### akhir profil

    ### awal KB

    @render.ui
    #@reactive.event(input.action_button)
    def vb_unmet_need():
        vb = ui.value_box(
            "KPI Title",
            "$1 Billion Dollars",
            "Up 30% VS PREVIOUS 30 DAYS",
            showcase=piggy_bank,
            theme="bg-gradient-orange-red",
            full_screen=True,
        )
        return(vb)

    ### akhir KB
app = App(app_ui, server)