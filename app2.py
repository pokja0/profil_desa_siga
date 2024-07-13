from shiny import App, render, ui, reactive
import polars as pl

# Data input as a list of dictionaries
data = [
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "TOPOYO", "DESA": "SALULEKBO", "TOTAL": -2.009704},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "TOPOYO", "DESA": "PANGALLOANG", "TOTAL": -2.073505},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "TOPOYO", "DESA": "SINABATTA", "TOTAL": -1.984601},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "KAROSSA", "TOTAL": -1.810358},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "TASOKKO", "TOTAL": -1.925635},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "LARA", "TOTAL": -1.879259},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "KADAILA", "TOTAL": -1.767856},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "KAYU CALLA", "TOTAL": -1.791329},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "LEMBAH HOPO", "TOTAL": -1.853025},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "BENGGAULU", "TOTAL": -1.75638},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "SUKA MAJU", "TOTAL": -1.829642},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "KAMBUNONG", "TOTAL": -1.94825},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "SALUBIRO", "TOTAL": -1.908342},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "MAMUJU TENGAH", "KECAMATAN": "KAROSSA", "DESA": "SANJANGO", "TOTAL": -1.801845},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBAIRA", "DESA": "TAMPAURE", "TOTAL": -0.955359},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBAIRA", "DESA": "BAMBAIRA", "TOTAL": -0.981161},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBAIRA", "DESA": "KASOLOANG", "TOTAL": -1.013465},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBAIRA", "DESA": "KALUKU NANGKA", "TOTAL": -1.004631},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "RANDOMAYANG", "TOTAL": -1.055057},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "BAMBALAMOTU", "TOTAL": -1.086986},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "POLEWALI", "TOTAL": -1.138055},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "PANGIANG", "TOTAL": -1.132456},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "KALOLA", "TOTAL": -1.119735},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BAMBALAMOTU", "DESA": "WULAI", "TOTAL": -1.058962},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "BARAS", "TOTAL": -1.561229},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "BULU PARIGI", "TOTAL": -1.608294},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "BALANTI", "TOTAL": -1.581314},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "MOTU", "TOTAL": -1.528099},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "TOWONI", "TOTAL": -1.604194},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BARAS", "DESA": "KASANO", "TOTAL": -1.537815},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BULU TABA", "DESA": "SUMBER SARI", "TOTAL": -1.431718},
    {"PROVINSI": "SULAWESI BARAT", "KABUPATEN": "PASANGKAYU", "KECAMATAN": "BULU TABA", "DESA": "LELEJAE", "TOTAL": -1.430692}
]

# Convert list of dictionaries to a Polars DataFrame
df = pl.DataFrame(data)

# Function to filter the DataFrame based on given parameters
def filter_data(df, provinsi=None, kabupaten=None, kecamatan=None, desa=None):
    if provinsi:
        df = df.filter(pl.col("PROVINSI") == provinsi)
    if kabupaten:
        df = df.filter(pl.col("KABUPATEN") == kabupaten)
    if kecamatan:
        df = df.filter(pl.col("KECAMATAN") == kecamatan)
    if desa:
        df = df.filter(pl.col("DESA") == desa)
    return df

app_ui = ui.page_fluid(
    ui.panel_title("Data Filter"),
    ui.input_selectize("provinsi", "Pilih Provinsi:", choices=["SULAWESI BARAT"], selected="SULAWESI BARAT"),
    ui.input_selectize("kabupaten", "Pilih Kabupaten:", choices=[], selected=None, multiple=False),
    ui.input_selectize("kecamatan", "Pilih Kecamatan:", choices=[], selected=None, multiple=False),
    ui.input_selectize("desa", "Pilih Desa:", choices=[], selected=None, multiple=False),
    ui.output_table("filtered_table")
)

def server(input, output, session):
    @reactive.Effect
    def _update_kabupaten():
        if input.provinsi() == "SULAWESI BARAT":
            kabupaten_choices = df.filter(pl.col("PROVINSI") == "SULAWESI BARAT").select("KABUPATEN").unique().to_series().to_list()
            session.send_input_update("kabupaten", choices=kabupaten_choices, selected=None)
    
    @reactive.Effect
    def _update_kecamatan():
        if input.kabupaten():
            kecamatan_choices = df.filter(pl.col("KABUPATEN") == input.kabupaten()).select("KECAMATAN").unique().to_series().to_list()
            session.send_input_update("kecamatan", choices=kecamatan_choices, selected=None)
        else:
            session.send_input_update("kecamatan", choices=[], selected=None)

    @reactive.Effect
    def _update_desa():
        if input.kecamatan():
            desa_choices = df.filter(pl.col("KECAMATAN") == input.kecamatan()).select("DESA").unique().to_series().to_list()
            session.send_input_update("desa", choices=desa_choices, selected=None)
        elif input.kabupaten():
            desa_choices = df.filter(pl.col("KABUPATEN") == input.kabupaten()).select("DESA").unique().to_series().to_list()
            session.send_input_update("desa", choices=desa_choices, selected=None)
        else:
            session.send_input_update("desa", choices=[], selected=None)

    #@output
    @render.table
    def filtered_table():
        filtered_df = filter_data(df, provinsi=input.provinsi(), kabupaten=input.kabupaten(), kecamatan=input.kecamatan(), desa=input.desa())
        return filtered_df.to_pandas()

app = App(app_ui, server)
