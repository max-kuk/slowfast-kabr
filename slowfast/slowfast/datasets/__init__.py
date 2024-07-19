#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

from .ava_dataset import Ava  # noqa
from .build import DATASET_REGISTRY, build_dataset  # noqa
from .charades import Charades  # noqa
from .imagenet import Imagenet  # noqa
from .kinetics import Kinetics as Kinetics  # for Kinetics (dense sampling)
from .kinetics_sparse import (
    Kinetics_sparse as Kinetics_sparse,
)  # for Kinetics (sparse sampling)
from .ptv_datasets import Ptvcharades, Ptvkinetics, Ptvssv2  # noqa
from .sth import Sth as Sth  # shared for Something-Something V1 and V2
from .anet import Anet as Anet  # shared for ActivityNet and HACS
from .mit import Mit as Mit  # for Moments in Time
from .ssv2 import Ssv2  # noqa
from .mammalnet_animal import Mammalnet_animal as Mammalnet_animal
from .mammalnet_behavior import Mammalnet_behavior as Mammalnet_behavior
from .mammalnet_behavior_composition import (
    Mammalnet_behavior_composition as Mammalnet_behavior_composition,
)


try:
    from .ptv_datasets import Ptvcharades, Ptvkinetics, Ptvssv2  # noqa
except Exception:
    print("Please update your PyTorchVideo to latest master")
