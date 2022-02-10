import numpy as np

for i in range(30):
    if i % 10 < 6:
        arr = np.load("problems/center_single/RAVEN_{}_train.npz".format(i))

        print((arr["image"].shape))
        print((arr["target"]))
        print((arr["predict"]))
        print((arr["meta_matrix"]))
        print((arr["meta_target"]))
        print((arr["structure"]))
        print((arr["meta_structure"]))
        print("------------------")

#print("shape:", arr.shape)
#print("first element", arr[0])
