#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

"""Loss functions."""

import pandas as pd
import numpy as np
from functools import partial
import torch
import torch.nn as nn
import torch.nn.functional as F

from pytorchvideo.losses.soft_target_cross_entropy import (
    SoftTargetCrossEntropyLoss,
)

import os
from distutils.sysconfig import get_python_lib
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = f"{get_python_lib()}{os.sep}cv2{os.sep}qt{os.sep}plugins{os.sep}platforms"
class ContrastiveLoss(nn.Module):
    def __init__(self, reduction="mean"):
        super(ContrastiveLoss, self).__init__()
        self.reduction = reduction

    def forward(self, inputs, dummy_labels=None):
        targets = torch.zeros(inputs.shape[0], dtype=torch.long).cuda()
        loss = nn.CrossEntropyLoss(reduction=self.reduction).cuda()(
            inputs, targets
        )
        return loss


class MultipleMSELoss(nn.Module):
    """
    Compute multiple mse losses and return their average.
    """

    def __init__(self, reduction="mean"):
        """
        Args:
            reduction (str): specifies reduction to apply to the output. It can be
                "mean" (default) or "none".
        """
        super(MultipleMSELoss, self).__init__()
        self.mse_func = nn.MSELoss(reduction=reduction)

    def forward(self, x, y):
        loss_sum = 0.0
        multi_loss = []
        for xt, yt in zip(x, y):
            if isinstance(yt, (tuple,)):
                if len(yt) == 2:
                    yt, wt = yt
                    lt = "mse"
                elif len(yt) == 3:
                    yt, wt, lt = yt
                else:
                    raise NotImplementedError
            else:
                wt, lt = 1.0, "mse"
            if lt == "mse":
                loss = self.mse_func(xt, yt)
            else:
                raise NotImplementedError
            loss_sum += loss * wt
            multi_loss.append(loss)
        return loss_sum, multi_loss


# dir_action_count = "/mnt/HDD/Backup/Animal Action Recognition/Animal_Kingdom/annotation/df_action.xlsx"
# dir_action_count = "/mnt/HDD/Backup/Animal Action Recognition/baboons/tracks_ds/df_action.xlsx"
dir_action_count = "kabr/KABR/annotation/distribution.xlsx"


class BCELoss(nn.Module):
    '''
    Function: BCELoss
    Params:
        predictions: input->(batch_size, 1004)
        targets: target->(batch_size, 1004)
    Return:
        bceloss
    '''

    def __init__(self,logits=True, reduction="mean"):
        super(BCELoss, self).__init__()
        self.logits = logits
        self.reduction = reduction

    def forward(self, inputs, targets):
        if self.logits:
            BCE_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction=self.reduction)
        else:
            BCE_loss = F.binary_cross_entropy(inputs, targets, reduction=self.reduction)

        return BCE_loss

class FocalLoss(nn.Module):
    '''
    Function: FocalLoss
    Params:
        alpha: scale factor, default = 1
        gamma: exponential factor, default = 0
    Return:
        focalloss
    https://github.com/17Skye17/VideoLT/blob/master/ops/losses.py
    Original: https://github.com/facebookresearch/Detectron
    '''

    def __init__(self, logits=True, reduction="mean"):
        super(FocalLoss, self).__init__()
        self.alpha = 1 
        self.gamma = 0 
        self.logits = logits
        self.reduction = reduction

    def forward(self, inputs, targets):
        if self.logits:
            BCE_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction="none")
        else:
            BCE_loss = F.binary_cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-BCE_loss)
        F_loss = self.alpha * (1 - pt) ** self.gamma * BCE_loss

        if self.reduction == "mean":
            return torch.mean(F_loss)
        elif self.reduction == "sum":
            return torch.sum(F_loss)
        else:
            return F_loss


class LDAM(nn.Module):
    '''
    https://github.com/17Skye17/VideoLT/blob/master/ops/losses.py
    Original: https://github.com/kaidic/LDAM-DRW/blob/master/losses.py
    '''

    def __init__(self, logits=True, reduction='mean', max_m=0.5, s=30, step_epoch=80):
        super(LDAM, self).__init__()

        data = pd.read_excel(dir_action_count)
        self.num_class_list = list(map(float, data["count"].tolist()))  
        self.reduction = reduction
        self.logits = logits

        m_list = 1.0 / np.sqrt(np.sqrt(self.num_class_list))
        m_list = m_list * (max_m / np.max(m_list))
        m_list = torch.FloatTensor(m_list).cuda()
        self.m_list = m_list
        self.s = s
        self.step_epoch = step_epoch
        self.weight = None

    def reset_epoch(self, epoch):
        idx = epoch // self.step_epoch
        betas = [0, 0.9999]
        effective_num = 1.0 - np.power(betas[idx], self.num_class_list)
        per_cls_weights = (1.0 - betas[idx]) / np.array(effective_num)
        per_cls_weights = per_cls_weights / np.sum(per_cls_weights) * len(self.num_class_list)
        self.weight = torch.FloatTensor(per_cls_weights).cuda()

    def forward(self, inputs, targets):
        targets=targets.to(torch.float32)
        batch_m = torch.matmul(self.m_list[None, :], targets.transpose(0, 1))
        batch_m = batch_m.view((-1, 1))
        inputs_m = inputs - batch_m

        output = torch.where(targets.type(torch.uint8), inputs_m, inputs)
        if self.logits:
            loss = F.binary_cross_entropy_with_logits(self.s * output, targets, reduction=self.reduction,
                                                    weight=self.weight)
        else:
            loss = F.binary_cross_entropy(self.s * output, targets, reduction=self.reduction, weight=self.weight)
        return loss


class EQL(nn.Module):
    '''
    https://github.com/17Skye17/VideoLT/blob/master/ops/losses.py
    Original: https://github.com/tztztztztz/eql.detectron2
    '''

    def __init__(self, logits=True, reduction='mean', max_tail_num=100, gamma=1.76 * 1e-3):
        super(EQL, self).__init__()
        data = pd.read_excel(dir_action_count)
        num_class_list = list(map(float, data["count"].tolist())) 
        self.reduction = reduction
        self.logits = logits

        max_tail_num = max_tail_num
        self.gamma = gamma

        self.tail_flag = [False] * len(num_class_list)
        for i in range(len(self.tail_flag)):
            if num_class_list[i] <= max_tail_num:
                self.tail_flag[i] = True

    def threshold_func(self):
        weight = self.inputs.new_zeros(self.n_c)
        weight[self.tail_flag] = 1
        weight = weight.view(1, self.n_c).expand(self.n_i, self.n_c)
        return weight

    def beta_func(self):
        rand = torch.rand((self.n_i, self.n_c)).cuda()
        rand[rand < 1 - self.gamma] = 0
        rand[rand >= 1 - self.gamma] = 1
        return rand

    def forward(self, inputs, targets):
        self.inputs = inputs
        self.n_i, self.n_c = self.inputs.size()

        # CAHNGE BACK. FOR I3D ONLY
        # self.n_c = self.n_c // 4

        # targets = targets.type(torch.FloatTensor).cuda()
        eql_w = 1 - self.beta_func() * self.threshold_func() * (1 - targets)
        if self.logits:
            loss = F.binary_cross_entropy_with_logits(self.inputs, targets, reduction=self.reduction, weight=eql_w)
        else:
            loss = F.binary_cross_entropy(self.inputs, targets, reduction=self.reduction, weight=eql_w)
        return loss


_LOSSES = {
    "cross_entropy": nn.CrossEntropyLoss,
    "bce": nn.BCELoss,
    "bce_logit": nn.BCEWithLogitsLoss,
    "soft_cross_entropy": partial(
        SoftTargetCrossEntropyLoss, normalize_targets=False
    ),
    "contrastive_loss": ContrastiveLoss,
    "mse": nn.MSELoss,
    "multi_mse": MultipleMSELoss,

    # Extra.
    "bce_loss": BCELoss,
    "focal_loss": FocalLoss,
    "LDAM": LDAM,
    "EQL": EQL,
}


def get_loss_func(loss_name):
    """
    Retrieve the loss given the loss name.
    Args (int):
        loss_name: the name of the loss to use.
    """
    if loss_name not in _LOSSES.keys():
        raise NotImplementedError("Loss {} is not supported".format(loss_name))
    return _LOSSES[loss_name]
