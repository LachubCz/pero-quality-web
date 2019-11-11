import subprocess

models = ["comparing_model_128",                  "comparing_model_128_all_avg_drop", 
          "comparing_model_128_all_avg_drop_reg", "comparing_model_128_all_max", 
          "comparing_model_128_drop",             "comparing_model_128_reg",
          "comparing_model_128_reg12",            "comparing_model_128_reg12", 
          "comparing_model_256_5x5_reg12",
          "comparing_model_256_reg12",            "comparing_model_512", 
          "comparing_model_VGG_16",               "comparing_model_VGG_16",
          "comparing_model_VGG_16_small",         "comparing_model_VGG_16_small",
          "comparing_model_VGG_16_smaller",       "comparing_model_VGG_16_smaller"]

weights = ["./models/comparing_model_128.h5",                  "./models/comparing_model_128_all_avg_drop.h5", 
           "./models/comparing_model_128_all_avg_drop_reg.h5", "./models/comparing_model_128_all_max.h5", 
           "./models/comparing_model_128_drop.h5",             "./models/comparing_model_128_reg.h5",
           "./models/comparing_model_128_reg12_0.h5",          "./models/comparing_model_128_reg12_1.h5", 
           "./models/comparing_model_256_5x5_reg12.h5",
           "./models/comparing_model_256_reg12.h5",            "./models/comparing_model_512.h5", 
           "./models/comparing_model_VGG_16_0.h5",             "./models/comparing_model_VGG_16_1.h5",
           "./models/comparing_model_VGG_16_small_0.h5",       "./models/comparing_model_VGG_16_small_1.h5",
           "./models/comparing_model_VGG_16_smaller_0.h5",     "./models/comparing_model_VGG_16_smaller_1.h5"]

images = ["./pages/51d12da5-435f-11dd-b505-00145e5790ea.jpg", "./pages/55a93745-435f-11dd-b505-00145e5790ea.jpg", 
          "./pages/549b2282-435f-11dd-b505-00145e5790ea.jpg", "./pages/567623da-435f-11dd-b505-00145e5790ea.jpg"]

#print correlation of models
for i, item in enumerate(models):
    name = weights[i].split("/")[-1].split(".")[0]
    print(name)
    with open("./temp/folder_{}.txt" .format(name), "w+") as output:
        subprocess.call(["python", "rate_folder.py", 
            "--model_name", "{}" .format(item),
            "--model_weights", "{}" .format(weights[i]),
            "--folder", "./crops"], stdout=output)

    with open("./temp/folder_{}.txt" .format(name)) as f_input:
        data = f_input.read().rstrip('\n')
    with open("./temp/folder_{}.txt" .format(name), 'w') as f_output:    
        f_output.write(data)

    subprocess.call(["python", "correlation.py",
            "--quality_network_file", "./temp/folder_{}.txt" .format(name),
            "--annotation_model_file", "./rankings/crops_48_annotation_model.txt",
            "--mode", "result"])

#train end of the net and make heatmaps
for i, item in enumerate(models):
    name = weights[i].split("/")[-1].split(".")[0]
    print(name)
    with open("./temp/folder_{}.txt" .format(name), "w+") as output:
        subprocess.call(["python", "rate_folder.py", 
            "--model_name", "{}" .format(item),
            "--model_weights", "{}" .format(weights[i]),
            "--folder", "./crops"], stdout=output)

    with open("./temp/folder_{}.txt" .format(name)) as f_input:
        data = f_input.read().rstrip('\n')
    with open("./temp/folder_{}.txt" .format(name), 'w') as f_output:    
        f_output.write(data)

    with open("./temp/correlation_{}.txt" .format(name), "w+") as output:
        subprocess.call(["python", "correlation.py",
                "--quality_network_file", "./temp/folder_{}.txt" .format(name),
                "--annotation_model_file", "./rankings/crops_48_annotation_model.txt",
                "--mode", "compare"], stdout=output)

    with open("./temp/correlation_{}.txt" .format(name)) as f_input:
        data = f_input.read().rstrip('\n')
    with open("./temp/correlation_{}.txt" .format(name), 'w') as f_output:    
        f_output.write(data)

    with open("./temp/output.txt", "w+") as output:
        subprocess.call(["python", "network_end.py",
            "--model_name", "{}" .format(item),
            "--correlation_file", "./temp/correlation_{}.txt" .format(name)], stdout=output)
    
    for e, elem in enumerate(images):
        with open("./temp/output.txt", "w+") as output:
            subprocess.call(["python", "heatmap.py",
                "--model_name", "{}" .format(item),
                "--image_name", "{}" .format(elem), 
                "--model_weights", "{}" .format(weights[i]),
                "--mode", "use_end"], stdout=output)
