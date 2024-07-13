from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import polars as pl
from shinywidgets import output_widget, render_widget  
import plotly.express as px

import pandas as pd
from great_tables import GT, exibble, loc, style
from ipyleaflet import Map 

daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]

data_poktan = pl.read_csv("data/profil_poktan.csv")

# Data tentang Kabupaten, Kecamatan, dan Desa

# Membuat aplikasi Shiny
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
                    output_widget("mapping")
                )
            ),
            ui.nav_panel(
                "Keluarga Berencana"
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
    #@reactive.event(input.action_button)
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

    @render_widget  
    def mapping():
        data = {
            'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'Country': ['USA', 'USA', 'USA', 'USA', 'USA'],
            'Latitude': [40.7128, 34.0522, 41.8781, 29.7604, 33.4484],
            'Longitude': [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740]
        }

        # Membuat DataFrame
        df = pd.DataFrame(data)

        # Membuat peta
        fig = px.scatter_geo(df, 
                            lat='Latitude', 
                            lon='Longitude', 
                            hover_name='City', 
                            hover_data=['Country'],
                            projection='natural earth')
        return fig 

app = App(app_ui, server, debug=True)
app.run()
# Untuk menjalankan aplikasi, gunakan:

