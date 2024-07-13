
    @render.text
    def text1():
        kondisi_input = input.pilih_kab()
        if kondisi_input == "SEMUA KABUPATEN":
            filter_kabupaten = data_poktan.select("KABUPATEN").unique().to_series().to_list()
        else:
            filter_kabupaten = input.pilih_kab()
        return filter_kabupaten
    
    @render.text
    def text2():
        kondisi_input = input.pilih_kab()
        if kondisi_input == "SEMUA KABUPATEN":
            filter_kabupaten = data_poktan.select("KABUPATEN").unique().to_series().to_list()
        else:
            filter_kabupaten = [input.pilih_kab()]

        kondisi_input = input.pilih_kec()
        if kondisi_input == "SEMUA KECAMATAN":
            filter_kecamatan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                                pl.col("KECAMATAN").is_in(data_poktan.select("KECAMATAN").unique().to_series().to_list()))
            filter_kecamatan = filter_kecamatan.select("KECAMATAN").unique().to_series().to_list()
        else:
            filter_kecamatan = input.pilih_kec()
        return filter_kecamatan
    
    @render.text
    def text3():
        kondisi_input = input.pilih_kab()
        if kondisi_input == "SEMUA KABUPATEN":
            filter_kabupaten = data_poktan.select("KABUPATEN").unique().to_series().to_list()
        else:
            filter_kabupaten = [input.pilih_kab()]

        kondisi_input = input.pilih_kec()
        if kondisi_input == "SEMUA KECAMATAN":
            filter_kecamatan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                                pl.col("KECAMATAN").is_in(data_poktan.select("KECAMATAN").unique().to_series().to_list()))
            filter_kecamatan = filter_kecamatan.select("KECAMATAN").unique().to_series().to_list()
        else:
            filter_kecamatan = [input.pilih_kec()]
        
        kondisi_input = input.pilih_desa()
        if kondisi_input == "SEMUA DESA/KELURAHAN":
            filter_desa = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(data_poktan.select("KELURAHAN").unique().to_series().to_list()))
            filter_desa = filter_desa.select("KELURAHAN").unique().to_series().to_list()
        else:
            filter_desa = input.pilih_desa()
        return filter_desa

app = App(app_ui, server)