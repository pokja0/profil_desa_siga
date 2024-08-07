from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import shinyswatch
import polars as pl
from shinywidgets import output_widget, render_widget  
import plotly.express as px
import plotly.io as pio 
import faicons

import shiny as pyshiny

import pandas as pd
from great_tables import GT, exibble, loc, style
from ipyleaflet import Map 
import folium
import ipyleaflet

import math

import great_tables as gt
from itables.sample_dfs import get_countries
from itables.shiny import DT

from pathlib import Path

daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]

data_poktan = pl.read_csv("data/profil_poktan.csv")

#data_poktan = pl.read_csv("data/profil_poktan.csv")
    
icon_title_tes = "About tooltips"
icons_fa_tes = ui.HTML(
     f'<svg aria-hidden="true" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{icon_title_tes}</title><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'
    )
def fa_info_circle(icon_title: str, icons_fa):
    # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa(&quot;info-circle&quot;, a11y = &quot;sem&quot;, title = icon_title)`
    return ui.span(icon_title, " ", icons_fa)
# ui.tooltip(
#     fa_info_circle(icon_title),
#     "Text shown in the tooltip."
# )

piggy_bank = fa_info_circle(icon_title_tes, icons_fa_tes)

def filter_poktan(data, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan):
    hasil = data.filter(
        pl.col("KABUPATEN").is_in(filter_kabupaten),
        pl.col("KECAMATAN").is_in(filter_kecamatan),
        pl.col("KELURAHAN").is_in(filter_desa),
        pl.col("BULAN").is_in(filter_bulan)
    )
    hasil = hasil.drop("BATAS")

    return hasil

def nilai_bulan_sebelum(bulan_terpilih):
    daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    index = daftar_bulan.index(bulan_terpilih)
    if index == 0:
        return daftar_bulan[0]  # Jika bulan terpilih adalah JANUARI, nilai_bulan_sebelum juga JANUARI
    else:
        return daftar_bulan[index - 1]

def bulan_hingga(bulan_terpilih):
    daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    index = daftar_bulan.index(bulan_terpilih)
    return daftar_bulan[:index + 1]

def format_number(number):
    return f"{number:,}".replace(",", ".")

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Dashboard", 
        ui.layout_column_wrap(
            ui.input_selectize("pilih_kab", "Pilih Kabupaten", choices=[], multiple=False),
            ui.input_selectize("pilih_kec", "Pilih Kecamatan", choices=[], multiple=False),
            ui.input_selectize("pilih_desa", "Pilih Desa/Kelurahan", choices=[], multiple=False),
            ui.input_selectize("pilih_bulan", "BULAN", 
                                choices=daftar_bulan[:6], selected="JUNI")
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
                        ui.output_ui("vb_tenakes"),
                        ui.output_ui("vb_tp_kb"),
                        ui.output_ui("vb_mkjp")
                    ),
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Pasangan Usia Subur",
                            value=ui.output_ui("text_jumlah_pus"),
                            showcase=output_widget("line_vb_pus"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase_layout="bottom",
                        ),
                        ui.value_box(
                            "MCPR",
                            value=ui.output_ui("text_jumlah_mcpr"),
                            showcase=output_widget("line_vb_mcpr"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase_layout="bottom",
                        )
                    ),
                    ui.card(
                        ui.layout_column_wrap(
                            output_widget("bar_mix_kontrasepsi"),
                            output_widget("line_pa"),
                            output_widget("donut_status_pelatihan")
                        )
                    ),
                    ui.layout_column_wrap(
                        ui.tags.h1("Rekap dan Rincian Status Pelatihan", style="font-size: 24px; font-weight: bold; margin: 20px 0; text-align: center; color:black")

                    ),
                    ui.layout_column_wrap(
                        ui.output_ui("rekap_tabel_bidan"),
                        ui.output_ui("tabel_bidan")
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
    title="Profil Desa"
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
                                         pl.col("KELURAHAN").is_in(filter_desa)
                                        )
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
        filter_bulan = [input.pilih_bulan()]

        bkb = pl.read_excel("data/data_bkb.xlsx")
        bkr = pl.read_excel("data/data_bkr.xlsx")
        bkl = pl.read_excel("data/data_bkl.xlsx")
        uppka = pl.read_excel("data/data_uppka.xlsx")
        pikr = pl.read_excel("data/data_pikr.xlsx")
        kkb = pl.read_excel("data/data_kkb.xlsx")
        rdk = pl.read_excel("data/data_rdk.xlsx")
        daftar_desa = pl.read_csv("data/data_daftar_desa.csv")

        bkb = filter_poktan(bkb, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        bkr = filter_poktan(bkr, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        bkl = filter_poktan(bkl, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        uppka = filter_poktan(uppka, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        pikr = filter_poktan(pikr, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        kkb = filter_poktan(kkb, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        rdk = filter_poktan(rdk, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        daftar_desa = daftar_desa.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa)
            )
        
        data_poktan = pl.DataFrame({
            "Desa/Kel": daftar_desa.height,
            "Kampung KB": kkb["JUMLAH_KKB"].sum(),
            "Rumah DataKu": rdk["JUMLAH_RDK"].sum(),
            "BKB": bkr["JUMLAH_BKR"].sum(),
            "BKR": bkr["JUMLAH_BKR"].sum(),
            "BKL": bkl["JUMLAH_BKL"].sum(),
            "UPPKA": uppka["JUMLAH_UPPKA"].sum(),
            "PIK-R": pikr["JUMLAH_PIKR"].sum()
        })

        data_poktan = data_poktan.unpivot(["Desa/Kel", "Kampung KB", "Rumah DataKu",
                            "BKB", "BKR", "BKL", "UPPKA", "PIK-R"], 
                            variable_name="Poktan", value_name="Keterangan")
        # data_poktan = pl.read_csv("data/profil_poktan.csv")
            
        # data_poktan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
        #                                     pl.col("KECAMATAN").is_in(filter_kecamatan),
        #                                     pl.col("KELURAHAN").is_in(filter_desa))
        # # List kolom yang akan dihitung
        # columns_to_count = ["Kampung KB", "Rumah DataKU", "BKB", "BKR", "BKL", "UPPKA", "PIK-R"]

        # # Menghitung jumlah "Ada" untuk setiap kolom
        # counts = [data_poktan[col].str.count_matches("Ada").sum() for col in columns_to_count]

        # # Menghitung jumlah desa unik berdasarkan kombinasi KECAMATAN dan KELURAHAN
        # unique_desa = data_poktan.select(["KECAMATAN", "KELURAHAN"]).unique().shape[0]

        # # Membuat DataFrame hasil
        # results = pl.DataFrame({
        #     "Kategori": ["Desa/Kelurahan"] + columns_to_count,
        #     "Jumlah": [unique_desa] + counts
        # })
        return GT(data_poktan)
    
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
            "Indikator": ["Luas Wilayah", "Jumlah Penduduk", "Kepadatan Penduduk"],
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

        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        data_pus_unmet_need = pl.read_excel("data/data_pus.xlsx")

        def bulan_hingga(bulan_terpilih):
            daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
            index = daftar_bulan.index(bulan_terpilih)
            return daftar_bulan[:index + 1]

        hingga_bulan = bulan_hingga(filter_bulan)

        data_pus_unmet_need = data_pus_unmet_need.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(hingga_bulan)
        )
        data_pus_unmet_need = data_pus_unmet_need.group_by("Bulan").agg(
            [
                pl.sum("PUS").alias("PUS"),
                pl.sum("Unmet Need").alias("Unmet Need")
            ]
        )

        # Buat kolom baru yang merupakan hasil pembagian 'total_nilai1' dengan 'total_nilai2'
        data_pus_unmet_need = data_pus_unmet_need.with_columns(
            (pl.col("Unmet Need") / pl.col("PUS") *100 ).alias("Unmet Need(%)")
        )

        data_pus_unmet_need = data_pus_unmet_need.with_columns(
            pl.col("Unmet Need(%)").round(2)
        )

        #data_pus_unmet_need
        df_pandas = data_pus_unmet_need.to_pandas()

        # Peta urutan bulan
        bulan_urut = {
            "JANUARI": 1,
            "FEBRUARI": 2,
            "MARET": 3,
            "APRIL": 4,
            "MEI": 5,
            "JUNI": 6,
            "JULI": 7,
            "AGUSTUS": 8,
            "SEPTEMBER": 9,
            "OKTOBER": 10,
            "NOVEMBER": 11,
            "DESEMBER": 12
        }

        # Tambahkan kolom urutan bulan di pandas DataFrame
        df_pandas['Bulan_urut'] = df_pandas['Bulan'].map(bulan_urut)

        # Urutkan DataFrame berdasarkan urutan bulan
        df_pandas = df_pandas.sort_values(by='Bulan_urut')

        # Buang kolom urutan bulan setelah pengurutan
        df_pandas = df_pandas.drop(columns=['Bulan_urut'])


        # Buat line chart menggunakan Plotly
        fig = px.line(df_pandas, x="Bulan", y="Unmet Need(%)", markers=True)

        # Atur judul dan label sumbu
        fig.update_layout(
            title="Line Chart of PUS, Unmet Need, and Unmet Need(%)",
            xaxis_title="Bulan",
            yaxis_title="Values",
            legend_title="Metrics"
        )
        fig.update_traces(showlegend=False)

        fig.update_traces(
            line_color="#406EF1",
            line_width=1,
            fill="tozeroy",
            fillcolor="rgba(64,110,241,0.2)",
            hoverinfo="y",
        )

        fig.update_xaxes(visible=False, showgrid=False)
        fig.update_yaxes(visible=False, showgrid=False)
        fig.update_layout(
            height=100,
            hovermode="x",
            margin=dict(t=0, r=0, l=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    @render.ui
    #@reactive.event(input.action_button)
    def vb_unmet_need():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        data_pus = pl.read_excel("data/data_pus.xlsx")

        data_pus = data_pus.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([filter_bulan])
        )
        unmet_need_bulan_ini = round(data_pus["Unmet Need"].sum() / data_pus["PUS"].sum() *100, 2)
        #unmet_need_bulan_ini

        data_pus_bulan_lalu = pl.read_excel("data/data_pus.xlsx")

        data_pus_bulan_lalu = data_pus_bulan_lalu.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([nilai_bulan_sebelum(filter_bulan)])
        )
        unmet_need_bulan_lalu = round(data_pus_bulan_lalu["Unmet Need"].sum() / data_pus_bulan_lalu["PUS"].sum() *100, 2)
        #unmet_need_bulan_lalu


        if unmet_need_bulan_ini > unmet_need_bulan_lalu:
            icon_title = "Unmet Need"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 384 512" style="height:1em;width:0.75em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M214.6 41.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 141.2V448c0 17.7 14.3 32 32 32s32-14.3 32-32V141.2L329.4 246.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/></svg>'
                )
            kondisi = "Naik"
        elif unmet_need_bulan_ini < unmet_need_bulan_lalu:
            icon_title = "Unmet Need"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 384 512" style="height:1em;width:0.75em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M169.4 470.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 370.8 224 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 306.7L54.6 265.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/></svg>'
                )
            kondisi = "Turun"
        else:
            icon_title = "Unmet Need"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160H336c-17.7 0-32 14.3-32 32s14.3 32 32 32H463.5c0 0 0 0 0 0h.4c17.7 0 32-14.3 32-32V64c0-17.7-14.3-32-32-32s-32 14.3-32 32v51.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1V448c0 17.7 14.3 32 32 32s32-14.3 32-32V396.9l17.6 17.5 0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352H176c17.7 0 32-14.3 32-32s-14.3-32-32-32H48.4c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z"/></svg>'
            )
            kondisi = "Sama"

        icon_vb = ui.HTML(
                '<svg xmlns="http://www.w3.org/2000/svg" color="white" viewBox="0 0 384 512"><!--!Font Awesome Free 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M192 0a48 48 0 1 1 0 96 48 48 0 1 1 0-96zM120 383c-13.8-3.6-24-16.1-24-31V296.9l-4.6 7.6c-9.1 15.1-28.8 20-43.9 10.9s-20-28.8-10.9-43.9l58.3-97c15-24.9 40.3-41.5 68.7-45.6c4.1-.6 8.2-1 12.5-1h1.1 12.5H192c1.4 0 2.8 .1 4.1 .3c35.7 2.9 65.4 29.3 72.1 65l6.1 32.5c44.3 8.6 77.7 47.5 77.7 94.3v32c0 17.7-14.3 32-32 32H304 264v96c0 17.7-14.3 32-32 32s-32-14.3-32-32V384h-8-8v96c0 17.7-14.3 32-32 32s-32-14.3-32-32V383z"/></svg>'
            )
        
        #icon_title_tes = "About tooltips"
        # icons_fa = ui.HTML(
        #     f'<svg aria-hidden="true" color="blue" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{icon_title}</title><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'
        # )
        def fa_info_circle(icon_title: str, icons_fa):
            # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa(&quot;info-circle&quot;, a11y = &quot;sem&quot;, title = icon_title)`
            return ui.span(icon_title, " ", icons_fa)

        judul_vb = fa_info_circle(icon_title, icons_fa)

        if kondisi == "Naik":
            penjelasan_unmet_need = "Naik dari capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(unmet_need_bulan_lalu)  + ")"
        elif kondisi == "Turun":
             penjelasan_unmet_need ="Turun dari capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(unmet_need_bulan_lalu)  + ")"
        else:
            penjelasan_unmet_need = "Sama dengan capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(unmet_need_bulan_lalu)  + ")"

        vb = ui.value_box(  
            ui.span(judul_vb, style="font-size:20px; font-weight: bold;"),
            unmet_need_bulan_ini,
            penjelasan_unmet_need,
            showcase= faicons.icon_svg("person-pregnant"),
            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
            full_screen=True,
        )
        return(vb)

    @render.ui
    #@reactive.event(input.action_button)
    def vb_tenakes():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        data_tenakes = pl.read_excel("data/data_faskes_siga.xlsx")
        data_tenakes = data_tenakes.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        )
        jumlah_tenakes = data_tenakes.height

        if jumlah_tenakes <= 0:
            jumlah_tenakes = 0
        else:
            jumlah_tenakes = jumlah_tenakes

        vb = ui.value_box(  
            ui.span("Tenaga Kesehatan KB", style="font-size:20px; font-weight: bold;"),
            jumlah_tenakes,
            showcase= faicons.icon_svg("user-nurse"),
            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
            full_screen=True,
        )
        return(vb)
    
    @render.ui
    #@reactive.event(input.action_button)
    def vb_tp_kb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        data_tp_kb = pl.read_excel("data/data_faskes_siga.xlsx")
        data_tp_kb = data_tp_kb.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        )
        jumlah_tp_kb = len(data_tp_kb["No. Registrasi"].unique())

        if jumlah_tp_kb <= 0:
            jumlah_tp_kb = 0
        else:
            jumlah_tp_kb = jumlah_tp_kb

        vb = ui.value_box(  
            ui.span("Tempat Pelayanan KB", style="font-size:20px; font-weight: bold;"),
            jumlah_tp_kb,
            showcase= faicons.icon_svg("house-medical"),
            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
            full_screen=True,
        )
        return(vb)

    @render.ui
    #@reactive.event(input.action_button)
    def vb_mkjp():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        data_mkjp = pl.read_excel("data/data_mix_kontra.xlsx")

        data_mkjp = data_mkjp.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([filter_bulan])
        )
        mkjp_bulan_ini = data_mkjp["Implan"].sum() + data_mkjp["IUD"].sum() + data_mkjp["Vasektomi"].sum() + data_mkjp["Tubektomi"].sum()	
        #unmet_need_bulan_ini

        data_mkjp_bulan_lalu = pl.read_excel("data/data_mix_kontra.xlsx")

        data_mkjp_bulan_lalu = data_mkjp_bulan_lalu.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([nilai_bulan_sebelum(filter_bulan)])
        )
        mkjp_bulan_lalu = data_mkjp_bulan_lalu["Implan"].sum() + data_mkjp_bulan_lalu["IUD"].sum() + data_mkjp_bulan_lalu["Vasektomi"].sum() + data_mkjp_bulan_lalu["Tubektomi"].sum()
        mkjp_bulan_lalu


        if mkjp_bulan_ini > mkjp_bulan_lalu:
            icon_title = "MKJP"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 384 512" style="height:1em;width:0.75em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M214.6 41.4c-12.5-12.5-32.8-12.5-45.3 0l-160 160c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 141.2V448c0 17.7 14.3 32 32 32s32-14.3 32-32V141.2L329.4 246.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-160-160z"/></svg>'
                )
            kondisi = "Naik"
        elif mkjp_bulan_ini < mkjp_bulan_lalu:
            icon_title = "MKJP"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 384 512" style="height:1em;width:0.75em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M169.4 470.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 370.8 224 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 306.7L54.6 265.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"/></svg>'
                )
            kondisi = "Turun"
        else:
            icon_title = "MKJP"
            icons_fa = ui.HTML(
                f'<svg aria-hidden="true" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><path d="M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160H336c-17.7 0-32 14.3-32 32s14.3 32 32 32H463.5c0 0 0 0 0 0h.4c17.7 0 32-14.3 32-32V64c0-17.7-14.3-32-32-32s-32 14.3-32 32v51.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1V448c0 17.7 14.3 32 32 32s32-14.3 32-32V396.9l17.6 17.5 0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352H176c17.7 0 32-14.3 32-32s-14.3-32-32-32H48.4c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z"/></svg>'
            )
            kondisi = "Sama"

        icon_vb = ui.HTML(
                '<svg xmlns="http://www.w3.org/2000/svg" color="white" viewBox="0 0 384 512"><!--!Font Awesome Free 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M192 0a48 48 0 1 1 0 96 48 48 0 1 1 0-96zM120 383c-13.8-3.6-24-16.1-24-31V296.9l-4.6 7.6c-9.1 15.1-28.8 20-43.9 10.9s-20-28.8-10.9-43.9l58.3-97c15-24.9 40.3-41.5 68.7-45.6c4.1-.6 8.2-1 12.5-1h1.1 12.5H192c1.4 0 2.8 .1 4.1 .3c35.7 2.9 65.4 29.3 72.1 65l6.1 32.5c44.3 8.6 77.7 47.5 77.7 94.3v32c0 17.7-14.3 32-32 32H304 264v96c0 17.7-14.3 32-32 32s-32-14.3-32-32V384h-8-8v96c0 17.7-14.3 32-32 32s-32-14.3-32-32V383z"/></svg>'
            )

        #icon_title_tes = "About tooltips"
        # icons_fa = ui.HTML(
        #     f'<svg aria-hidden="true" color="blue" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{icon_title}</title><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'
        # )
        def fa_info_circle(icon_title: str, icons_fa):
            # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa(&quot;info-circle&quot;, a11y = &quot;sem&quot;, title = icon_title)`
            return ui.span(icon_title, " ", icons_fa)

        judul_vb = fa_info_circle(icon_title, icons_fa)

        if kondisi == "Naik":
            penjelasan_mkjp = "Naik dari capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(mkjp_bulan_lalu)  + ")"
        elif kondisi == "Turun":
                penjelasan_mkjp ="Turun dari capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(mkjp_bulan_lalu)  + ")"
        else:
            penjelasan_mkjp = "Sama dengan capaian " + nilai_bulan_sebelum(filter_bulan) + " (" + str(mkjp_bulan_lalu)  + ")"

        vb = ui.value_box(  
            ui.span(judul_vb, style="font-size:20px; font-weight: bold;"),
            mkjp_bulan_ini,
            penjelasan_mkjp,
            showcase= faicons.icon_svg("syringe"),
            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
            full_screen=True,
        )
        return vb

    @render_widget
    #@reactive.event(input.action_button)
    def bar_mix_kontrasepsi():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan =  bulan_hingga(input.pilih_bulan())
        data_mkjp = pl.read_excel("data/data_mix_kontra.xlsx")

        data_mkjp = data_mkjp.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(filter_bulan)
        )

        data_mkjp = data_mkjp.select(
            pl.col("Suntik").sum(),
            pl.col("Pil").sum(),
            pl.col("Kondom").sum(),
            pl.col("Implan").sum(),
            pl.col("IUD").sum(),
            pl.col("Vasektomi").sum(),
            pl.col("Tubektomi").sum(),
            pl.col("MAL").sum()
        )

        data_mkjp = data_mkjp.unpivot(on = ["Suntik", "Pil", "Kondom",
                "Implan",	"IUD",	"Vasektomi",
                "Tubektomi",	"MAL"], 
                variable_name="Alokon", value_name="Total")
        
        df = data_mkjp.to_pandas()

        # Mengurutkan data berdasarkan nilai terkecil ke terbesar
        df = df.sort_values(by="Total")

        # # Membuat bar chart dengan label
        # fig = px.bar(df, x="Variable", y="Value", title="Bar Chart", labels={"Variable": "Metode Kontrasepsi", "Value": "Jumlah"}, text="Value")

        grafik_kontrasepsi = px.bar(
            df,
            x="Total",
            y="Alokon",
            text="Total",
            title="Penggunaan Metode Kontrasepsi",
            orientation='h'
        )

        # Menambahkan pengaturan layout
        grafik_kontrasepsi.update_traces(marker_color='#0d6efd')
        grafik_kontrasepsi.update_layout(
            xaxis_title="Metode Kontrasepsi",
            yaxis_title="Jumlah Penggunaan",
            xaxis=dict(categoryorder="total ascending"),
            font=dict(family="Arial"),
            margin=dict(l=50, r=50, b=50, t=50),
            paper_bgcolor="#f6f8fa",
            plot_bgcolor="#f6f8fa",
            hoverlabel=dict(
                bgcolor="white",
                font=dict(family="Arial")
            ),
            legend=dict(font=dict(family="Arial")),
            hovermode="closest",
            hoverdistance=30,
            updatemenus=[dict(font=dict(family="Arial"))]
        )

        return grafik_kontrasepsi

    @render_widget
    #@reactive.event(input.action_button)
    def donut_status_pelatihan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        data_bidan = pl.read_excel("data/data_faskes_siga.xlsx")

        data_bidan = data_bidan.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        )

        data_bidan = data_bidan['Pelatihan']

        df = pl.DataFrame(data_bidan)

        # Konversi Polars DataFrame ke Pandas DataFrame
        df_pd = df.to_pandas()

        # Menambahkan kolom "Status Pelatihan" berdasarkan kondisi pada kolom "Pelatihan"
        df_pd["Status Pelatihan"] = df_pd["Pelatihan"].apply(
            lambda x: "Terlatih" if ("IUD" in x or "IMPLAN" in x) else "Tidak Terlatih"
        )

        # Plot donut chart menggunakan Plotly Express
        count = df_pd["Status Pelatihan"].value_counts()
        donut_status_pelatihan = px.pie(df_pd, names=count.index, values=count.values,
                    color=count.index, color_discrete_map={'Tidak Terlatih': '#ffc107', 'Terlatih': '#0d6efd'},
                    hole=0.5, title='Persentase Status Pelatihan Tenaga Kesehatan KB')

        donut_status_pelatihan.update_layout(
            xaxis_title="Metode Kontrasepsi",
            yaxis_title="Jumlah Penggunaan",
            xaxis=dict(categoryorder="total ascending"),
            font=dict(family="Arial"),
            margin=dict(l=50, r=50, b=50, t=50),
            paper_bgcolor="#f6f8fa",
            plot_bgcolor="#f6f8fa",
            hoverlabel=dict(
                bgcolor="white",
                font=dict(family="Arial")
            ),
            legend=dict(font=dict(family="Arial")),
            hovermode="closest",
            hoverdistance=30,
            updatemenus=[dict(font=dict(family="Arial"))]
        )
        return donut_status_pelatihan

    @render_widget
    #@reactive.event(input.action_button)
    def line_pa():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan =  bulan_hingga(input.pilih_bulan())
        data_pa = pl.read_excel("data/data_mix_kontra.xlsx")
        data_pa = data_pa.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(filter_bulan)
        )
        data_pa = data_pa.select(["PA", "Bulan"])
        data_pa = data_pa.group_by("Bulan").agg([
            pl.sum("PA")
        ])

        # Konversi kembali ke Pandas DataFrame untuk plotly
        data_pa = data_pa.to_pandas()

        # Menentukan urutan bulan
        bulan_order = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
        data_pa['Bulan'] = pd.Categorical(data_pa['Bulan'], categories=bulan_order, ordered=True)

        # Mengurutkan DataFrame berdasarkan urutan bulan
        data_pa = data_pa.sort_values('Bulan')

        line_pa = px.line(data_pa, x="Bulan", y="PA", title="Tren Peserta KB Aktif", markers=True)

        line_pa.update_layout(
            xaxis_title="Metode Kontrasepsi",
            yaxis_title="Jumlah Penggunaan",
            #xaxis=dict(categoryorder="total ascending"),
            font=dict(family="Arial"),
            margin=dict(l=50, r=50, b=50, t=50),
            paper_bgcolor="#f6f8fa",
            plot_bgcolor="#f6f8fa",
            hoverlabel=dict(
                bgcolor="white",
                font=dict(family="Arial")
            ),
            legend=dict(font=dict(family="Arial")),
            hovermode="closest",
            hoverdistance=30,
            updatemenus=[dict(font=dict(family="Arial"))]
        )
        return line_pa

    @render_widget
    #@reactive.event(input.action_button)
    def line_vb_pus():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        
        data_pus = pl.read_excel("data/data_pus.xlsx")

        hingga_bulan = bulan_hingga(filter_bulan)

        data_pus = data_pus.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(hingga_bulan)
        )
        data_pus = data_pus.select(["PUS", "Bulan"])
        data_pus = data_pus.group_by("Bulan").agg([
            pl.sum("PUS")
        ])

        data_pus = data_pus.to_pandas()

        # Menentukan urutan bulan
        bulan_order = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
        data_pus['Bulan'] = pd.Categorical(data_pus['Bulan'], categories=bulan_order, ordered=True)

        # Mengurutkan DataFrame berdasarkan urutan bulan
        data_pus = data_pus.sort_values('Bulan')


        line_pus = px.line(data_pus, x="Bulan", y="PUS",  markers=True)
        # line_pus.update_traces(
        #     line_color="#406EF1",
        #     line_width=1,
        #     fill="tozeroy",
        #     fillcolor="rgba(64,110,241,0.2)",
        #     hoverinfo="y",
        # )
        line_pus.update_xaxes(visible=False, showgrid=False)
        line_pus.update_yaxes(visible=False, showgrid=False)
        line_pus.update_layout(
            paper_bgcolor="#f6f8fa",
            plot_bgcolor="#f6f8fa"
        )
        return line_pus
        
    @render.text  
    #@reactive.event(input.action_button)
    def text_jumlah_pus():  
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        
        data_pus = pl.read_excel("data/data_pus.xlsx")

        data_pus = data_pus.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([filter_bulan])
        )
        data_pus = data_pus['PUS'].sum()
        data_pus = format_number(data_pus)
        return data_pus
    
    @render_widget
    #@reactive.event(input.action_button)
    def line_vb_mcpr():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        hingga_bulan = bulan_hingga(filter_bulan)

        #MCPR
        data_pus = pl.read_excel("data/data_pus.xlsx")

        data_pus = data_pus.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(hingga_bulan)
        )
        data_pus = data_pus.select(["PUS", "Bulan"])
        data_pus = data_pus.group_by("Bulan").agg([
            pl.sum("PUS")
        ])

        #MCPR
        data_mcpr = pl.read_excel("data/data_mix_kontra.xlsx")

        hingga_bulan = bulan_hingga("JUNI")

        data_mcpr = data_mcpr.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in(hingga_bulan)
        )
        data_mcpr = data_mcpr.select(["KB Modern", "Bulan"])
        data_mcpr = data_mcpr.group_by("Bulan").agg([
            pl.sum("KB Modern")
        ])

        data_mcpr = data_mcpr.join(data_pus, on="Bulan", how="inner")

        data_mcpr = data_mcpr.with_columns(
            (pl.col("KB Modern") / pl.col("PUS") * 100).round(2).alias("MCPR")
        )

        data_mcpr = data_mcpr.to_pandas()

        # Menentukan urutan bulan
        bulan_order = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
        data_mcpr['Bulan'] = pd.Categorical(data_mcpr['Bulan'], categories=bulan_order, ordered=True)

        # Mengurutkan DataFrame berdasarkan urutan bulan
        data_mcpr = data_mcpr.sort_values('Bulan')


        line_mcpr = px.line(data_mcpr, x="Bulan", y="MCPR",  markers=True)
        # line_pus.update_traces(
        #     line_color="#406EF1",
        #     line_width=1,
        #     fill="tozeroy",
        #     fillcolor="rgba(64,110,241,0.2)",
        #     hoverinfo="y",
        # )
        line_mcpr.update_xaxes(visible=False, showgrid=False)
        line_mcpr.update_yaxes(visible=False, showgrid=False)
        line_mcpr.update_layout(
            paper_bgcolor="#f6f8fa",
            plot_bgcolor="#f6f8fa"
        )
        return line_mcpr
        
    @render.text  
    #@reactive.event(input.action_button)
    def text_jumlah_mcpr():  
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        #MCPR
        data_pus = pl.read_excel("data/data_pus.xlsx")

        data_pus = data_pus.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan_Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([filter_bulan])
        )
        data_pus = data_pus.select(["PUS", "Bulan"])
        data_pus = data_pus.group_by("Bulan").agg([
            pl.sum("PUS")
        ])

        #MCPR
        data_mcpr = pl.read_excel("data/data_mix_kontra.xlsx")

        data_mcpr = data_mcpr.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("Bulan").is_in([filter_bulan])
        )
        data_mcpr = data_mcpr.select(["KB Modern", "Bulan"])
        data_mcpr = data_mcpr.group_by("Bulan").agg([
            pl.sum("KB Modern")
        ])

        data_mcpr = data_mcpr.join(data_pus, on="Bulan", how="inner")

        data_mcpr = data_mcpr.with_columns(
            (pl.col("KB Modern") / pl.col("PUS") * 100).round(2).alias("MCPR")
        )

        data_mcpr = data_mcpr["MCPR"].sum()

        data_mcpr = format_number(data_mcpr)
        return data_mcpr + "%"
    
    @reactive.calc
    #@reactive.event(input.action_button)  
    def data_bidan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        data_bidan = pl.read_excel("data/data_faskes_siga.xlsx")

        data_bidan = data_bidan.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        )			 		

        data_bidan = data_bidan.select(
            pl.col("Provinsi"), pl.col("Kabupaten"),
            pl.col("Kecamatan"), pl.col("Kelurahan/Desa"), pl.col("Nama Faskes"),
            pl.col("Nama Bidan"), pl.col("Pelatihan")
        )

        df = pl.DataFrame(data_bidan)

        # Konversi Polars DataFrame ke Pandas DataFrame
        df_pd = df.to_pandas()

        # Menambahkan kolom "Status Pelatihan" berdasarkan kondisi pada kolom "Pelatihan"
        df_pd["Pelatihan"] = df_pd["Pelatihan"].apply(
            lambda x: "Terlatih" if ("IUD" in x or "IMPLAN" in x) else "Belum Terlatih"
        )

        df_pd = pl.DataFrame(df_pd)
        return df_pd

    @render.ui
    def tabel_bidan():
        df = data_bidan()
        df = pl.DataFrame(df)
        df = df.with_columns(pl.arange(1, df.height + 1).alias("No")).select(["No", *df.columns])
        return ui.HTML(DT(df, scrollY="400px", scrollCollapse=True, paging=False,
                          search={"regex": True, "caseInsensitive": True},
                          buttons=["copyHtml5", "csvHtml5", "excelHtml5"]))


    @reactive.calc
    #@reactive.event(input.action_button)  
    def rekap_data_bidan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        data_bidan = pl.read_excel("data/data_faskes_siga.xlsx")

        data_bidan = data_bidan.filter(
            pl.col("Kabupaten").is_in(filter_kabupaten),
            pl.col("Kecamatan").is_in(filter_kecamatan),
            pl.col("Kelurahan/Desa").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        )			 		

        data_bidan = data_bidan.select(
            pl.col("Provinsi"), pl.col("Kabupaten"),
            pl.col("Kecamatan"), pl.col("Kelurahan/Desa"), pl.col("Nama Faskes"),
            pl.col("Nama Bidan"), pl.col("Pelatihan")
        )

        df = pl.DataFrame(data_bidan)

        # Konversi Polars DataFrame ke Pandas DataFrame
        df_pd = df.to_pandas()

        # Menambahkan kolom "Status Pelatihan" berdasarkan kondisi pada kolom "Pelatihan"
        df_pd["Pelatihan"] = df_pd["Pelatihan"].apply(
            lambda x: "Terlatih" if ("IUD" in x or "IMPLAN" in x) else "Belum Terlatih"
        )

        df_pd = pl.DataFrame(df_pd)
        
        if input.pilih_kab() == "SEMUA KABUPATEN":
            # Mengelompokkan data dan menghitung jumlahnya
            summary = df_pd.group_by(['Kabupaten', 'Pelatihan']).agg(
                pl.col('Nama Bidan').count().alias('count')
            )

            # Mengubah format agar serupa dengan unstack di pandas
            summary_pivot = summary.pivot(
                values='count',
                index=['Kabupaten'],
                on='Pelatihan'
            ).fill_null(0)

        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() == "SEMUA KECAMATAN":
            # Mengelompokkan data dan menghitung jumlahnya
            summary = df_pd.group_by(['Kabupaten', 'Kecamatan', 'Pelatihan']).agg(
                pl.col('Nama Bidan').count().alias('count')
            )

            summary_pivot = summary.pivot(
                values='count',
                index=['Kabupaten', 'Kecamatan'],
                on='Pelatihan'
            ).fill_null(0)
            summary_pivot = summary_pivot.sort(['Kabupaten', 'Kecamatan'])
            
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            # Mengelompokkan data dan menghitung jumlahnya
            summary = df_pd.group_by(['Kabupaten', 'Kecamatan', 'Kelurahan/Desa', 'Pelatihan']).agg(
                pl.col('Nama Bidan').count().alias('count')
            )

            summary_pivot = summary.pivot(
                values='count',
                index=['Kabupaten', 'Kecamatan', 'Kelurahan/Desa'],
                on='Pelatihan'
            ).fill_null(0)
            summary_pivot = summary_pivot.sort(['Kabupaten', 'Kecamatan', 'Kelurahan/Desa'])

        else:
            summary = df_pd.group_by(['Kabupaten', 'Kecamatan', 'Kelurahan/Desa', 'Nama Faskes', 'Pelatihan']).agg(
                pl.col('Nama Bidan').count().alias('count')
            )

            # Mengubah format agar serupa dengan unstack di pandas
            summary_pivot = summary.pivot(
                values='count',
                index=['Kabupaten', 'Kecamatan', 'Kelurahan/Desa', 'Nama Faskes'],
                on='Pelatihan'
            ).fill_null(0)

            # Menambah kolom 'Terlatih' jika belum ada
            if 'Terlatih' not in summary_pivot.columns:
                summary_pivot = summary_pivot.with_columns(pl.lit(0).alias('Terlatih'))
            elif 'Belum Terlatih' not in summary_pivot.columns:
                summary_pivot = summary_pivot.with_columns(pl.lit(0).alias('Belum Terlatih'))

            # Atur urutan kolom agar 'Terlatih' berada di urutan yang diinginkan
            columns_order = ['Kabupaten', 'Kecamatan', 'Kelurahan/Desa', 'Nama Faskes', 'Belum Terlatih', 'Terlatih']
            summary_pivot = summary_pivot.select(columns_order)
        # Menghitung total untuk kolom "Belum Terlatih" dan "Terlatih"
        summary_pivot = summary_pivot.to_pandas()
        # Menghitung total untuk kolom "Belum Terlatih" dan "Terlatih"
        total_belum_terlatih = summary_pivot['Belum Terlatih'].sum()
        total_terlatih = summary_pivot['Terlatih'].sum()

        # Menambahkan baris total ke DataFrame
        total_row = pd.DataFrame({
            'Kabupaten': ['TOTAL'],
            'Belum Terlatih': [total_belum_terlatih],
            'Terlatih': [total_terlatih]
        })

        summary_pivot = pd.concat([summary_pivot, total_row])
        summary_pivot['Jumlah Bidan'] = summary_pivot['Belum Terlatih'] + summary_pivot['Terlatih']
        return summary_pivot

    @render.ui
    def rekap_tabel_bidan():
        df = rekap_data_bidan()
        df = pl.DataFrame(df)
        df = df.with_columns(pl.arange(1, df.height + 1).alias("No")).select(["No", *df.columns])
        return ui.HTML(DT(df, scrollY="400px", scrollCollapse=True, paging=False,
                          search={"regex": True, "caseInsensitive": True},
                          buttons=["copyHtml5", "csvHtml5", "excelHtml5"]))
    ### akhir KB
www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)