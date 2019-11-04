import subprocess

models = ["comparing_model_128_drop", "comparing_model_128_all_avg_drop", "comparing_model_128_all_max", 
          "comparing_model_128_all_avg_drop_reg", "comparing_model_128_reg", "comparing_model_128_reg12",
          "comparing_model_256_reg12", "comparing_model_256_5x5_reg12"]
images = ["./pages/51d12da5-435f-11dd-b505-00145e5790ea.jpg", "./pages/55a93745-435f-11dd-b505-00145e5790ea.jpg", 
          "./pages/549b2282-435f-11dd-b505-00145e5790ea.jpg", "./pages/567623da-435f-11dd-b505-00145e5790ea.jpg"]

for i, item in enumerate(models):
    print(item)
    with open("./temp/folder_{}.txt" .format(item), "w+") as output:
        subprocess.call(["python", "rate_folder.py", 
            "--model_name", "{}" .format(item),
            "--model_weights", "./models/{}.h5" .format(item),
            "--folder", "./crops"], stdout=output)

    with open("./temp/folder_{}.txt" .format(item)) as f_input:
        data = f_input.read().rstrip('\n')
    with open("./temp/folder_{}.txt" .format(item), 'w') as f_output:    
        f_output.write(data)

    with open("./temp/correlation_{}.txt" .format(item), "w+") as output:
        subprocess.call(["python", "correlation.py",
            "--quality_network_file", "./temp/folder_{}.txt" .format(item),
            "--annotation_model_file", "./rankings/crops_48_annotation_model.txt"], stdout=output)

    with open("./temp/correlation_{}.txt" .format(item)) as f_input:
        data = f_input.read().rstrip('\n')
    with open("./temp/correlation_{}.txt" .format(item), 'w') as f_output:    
        f_output.write(data)

    with open("output.txt", "w+") as output:
        subprocess.call(["python", "network_end.py",
            "--model_name", "{}" .format(item),
            "--correlation_file", "./temp/correlation_{}.txt" .format(item)], stdout=output)
    
    for e, elem in enumerate(images):
        with open("output.txt", "w+") as output:
            subprocess.call(["python", "heatmap.py",
                "--model_name", "{}" .format(item),
                "--image_name", "{}" .format(elem), 
                "--model_weights", "./models/{}.h5" .format(item)], stdout=output)
