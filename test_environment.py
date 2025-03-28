import sys

print(sys.version)

import torch

# Check if GPU is available
if torch.cuda.is_available():
    print("GPU is available and will be used for training.")
else:
    print("GPU is not available. Training will be done on the CPU.")

# for path in sys.path:
#     print(path)
# import sionna
# print(sionna.__version__)

# import tensorflow as tf
# print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices("GPU")))
# print(tf.sysconfig.get_build_info())
# print(tf.__version__)

import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4])
plt.ylabel("some numbers")
plt.savefig("test2.svg", format="svg",dpi = 200)
plt.show()

plt.plot([1,4,9,16])
plt.ylabel("some numbers")
plt.savefig("test3.svg", format="svg",dpi = 200)
plt.show()