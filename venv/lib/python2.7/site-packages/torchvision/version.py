__version__ = '0.5.0'
git_version = '6d6fbdfe9e8d1521ea82efde970bbbd714366afb'
from torchvision.extension import _check_cuda_version
if _check_cuda_version() > 0:
    cuda = _check_cuda_version()
