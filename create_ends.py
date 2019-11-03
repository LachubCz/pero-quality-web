import subprocess

with open("output.txt", "w+") as output:
    subprocess.call(["python", "rate_folder.py", 
        "--model_name", "comparing_model_128",
        "--model_weights", "./models/comparing_model_128.h5",
        "--folder", "./crops"], stdout=output)

with open("output.txt", "w+") as output:
    subprocess.call(["python", "correlation.py",
        "--quality_network_file", "./rankings/crops_48_quality_network.txt",
        "--annotation_model_file", "./rankings/crops_48_annotation_model.txt"], stdout=output)

with open("output.txt", "w+") as output:
    subprocess.call(["python", "network_end.py",
        "--model_name", "comparing_model_128",
        "--correlation_file", "./rankings/crops_48_annotation_model.txt"], stdout=output)

with open("output.txt", "w+") as output:
    subprocess.call(["python", "heatmap.py",
        "--model_name", "comparing_model_128",
        "--image_name", "./pages/55a93745-435f-11dd-b505-00145e5790ea.jpg", 
        "--model_weights", "./models/comparing_model_128.h5"], stdout=output)
