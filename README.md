# PERO - Anotátor kvality dokumentů

Spuštění aplikace:

`python3 run_app.py`

Skriptu na nahrání datasetu se dává soubor s cropy, ukázka takového souboru je `crop_files/crop_file_60_pages.txt`

Nahrání setu do databáze:  

`python3 fill_database.py -n nazev_datasetu -t typ_datasetu -d popis_datasetu -l example_crop_file.txt`

Vytvoření heatmapy:

`python heatmap.py --model_type done --model_name regression_model --mode use_end  --model_weights ./models/regression_model.h5 --colors first --image_name ./pages/51d12da5-435f-11dd-b505-00145e5790ea.jpg`

### Databáze:
- `databases/database_old.sqlite3` - 60 náhodných stránek, 1316 anotací
- `databases/database_new.sqlite3` - 200 náhodných stránek, 2834 anotací
- `databases/database_merged.sqlite3` - 200 náhodných stránek, 4150 anotací (spojená `database_old.sqlite3` a `database_new.sqlite3`)

