# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
# --------------------------------------------------------
# References:
# DeiT: https://github.com/facebookresearch/deit
# BEiT: https://github.com/microsoft/unilm/tree/master/beit
# --------------------------------------------------------

import math
import sys
from typing import Iterable, Optional

import torch

from timm.data import Mixup
from timm.utils import accuracy

import util.misc as misc
import util.lr_sched as lr_sched

def train_one_epoch(model: torch.nn.Module, criterion: torch.nn.Module,
                    data_loader: Iterable, optimizer: torch.optim.Optimizer,
                    device: torch.device, epoch: int, loss_scaler, max_norm: float = 0,
                    mixup_fn: Optional[Mixup] = None, log_writer=None,
                    args=None, focal_loss=False, prob_focal_loss = False, sqrt_loss = False, ep_loss = False, gamma=2):
    model.train(True)
    metric_logger = misc.MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', misc.SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = 'Epoch: [{}]'.format(epoch)
    print_freq = 20

    accum_iter = args.accum_iter

    optimizer.zero_grad()

    if log_writer is not None:
        print('log_dir: {}'.format(log_writer.log_dir))

    for data_iter_step, (samples, targets) in enumerate(metric_logger.log_every(data_loader, print_freq, header)):

        # we use a per iteration (instead of per epoch) lr scheduler
        if data_iter_step % accum_iter == 0:
            lr_sched.adjust_learning_rate(optimizer, data_iter_step / len(data_loader) + epoch, args)

        samples = samples.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        if mixup_fn is not None:
            samples, targets = mixup_fn(samples, targets)

        with torch.cuda.amp.autocast():
            outputs = model(samples)
            loss = criterion(outputs, targets)

            if focal_loss:
                pc = torch.exp(-loss)
                fl_loss = ((1 - pc) ** gamma * loss).mean()  # mean over the batch
                loss = fl_loss
            elif prob_focal_loss:
                pc = torch.exp(-loss)
                p_fl_loss = (loss/(pc+1e-14)).mean()
                loss = p_fl_loss
            elif sqrt_loss:
                pc = torch.exp(-loss)
                sqrt_loss = (torch.sqrt(1-pc) * loss).mean()
                loss = sqrt_loss
            elif ep_loss:
                pc = torch.exp(-loss)
                ep_loss = (torch.exp(-0.5 * pc) * loss).mean()
                loss = ep_loss
        loss_value = loss.item()

        if not math.isfinite(loss_value):
            print("Loss is {}, stopping training".format(loss_value))
            sys.exit(1)

        loss /= accum_iter
        loss_scaler(loss, optimizer, clip_grad=max_norm,
                    parameters=model.parameters(), create_graph=False,
                    update_grad=(data_iter_step + 1) % accum_iter == 0)
        if (data_iter_step + 1) % accum_iter == 0:
            optimizer.zero_grad()

        torch.cuda.synchronize()

        metric_logger.update(loss=loss_value)
        min_lr = 10.
        max_lr = 0.
        for group in optimizer.param_groups:
            min_lr = min(min_lr, group["lr"])
            max_lr = max(max_lr, group["lr"])

        metric_logger.update(lr=max_lr)

        loss_value_reduce = misc.all_reduce_mean(loss_value)
        if log_writer is not None and (data_iter_step + 1) % accum_iter == 0:
            """ We use epoch_1000x as the x-axis in tensorboard.
            This calibrates different curves when batch size changes.
            """
            epoch_1000x = int((data_iter_step / len(data_loader) + epoch) * 1000)
            log_writer.add_scalar('loss', loss_value_reduce, epoch_1000x)
            log_writer.add_scalar('lr', max_lr, epoch_1000x)

    # gather the stats from all processes
    metric_logger.synchronize_between_processes()
    print("Averaged stats:", metric_logger)
    return {k: meter.global_avg for k, meter in metric_logger.meters.items()}

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from torchmetrics.classification import MulticlassAUROC

from ignite.engine import *
from ignite.handlers import *
from ignite.metrics import *
from ignite.utils import *
from ignite.contrib.metrics.regression import *
from ignite.contrib.metrics import *


@torch.no_grad()
def evaluate(data_set, data_loader, model, device, args):
    criterion = torch.nn.CrossEntropyLoss()

    metric_logger = misc.MetricLogger(delimiter="  ")
    header = 'Test:'

    # switch to evaluation mode
    model.eval()

    y_pred = torch.zeros(0, dtype=torch.long, device='cpu')#[]
    y_Prob = torch.zeros(0, dtype=torch.long, device='cpu')
    y_true = torch.zeros(0, dtype=torch.long, device='cpu')
    misclassified_filenames = []

    for batch in metric_logger.log_every(data_loader, 10, header):
        images = batch[0]
        target = batch[-1]
        images = images.to(device, non_blocking=True)
        target = target.to(device, non_blocking=True)
        y_true = torch.cat([y_true, target.view(-1).cpu()])
        # compute output
        with torch.cuda.amp.autocast():
            output = model(images)
            predicted_probabilities = torch.softmax(output, dim=1)
            _, preds = torch.max(output, 1)
            y_pred = torch.cat([y_pred, preds.view(-1).cpu()])
            y_Prob = torch.cat([y_Prob, predicted_probabilities.cpu()])

            loss = criterion(output, target)

        acc1, acc5 = accuracy(output, target, topk=(1, 5))

        batch_size = images.shape[0]
        metric_logger.update(loss=loss.item())
        metric_logger.meters['acc1'].update(acc1.item(), n=batch_size)
        metric_logger.meters['acc5'].update(acc5.item(), n=batch_size)
    # gather the stats from all processes
    metric_logger.synchronize_between_processes()
    print('* Acc@1 {top1.global_avg:.3f} Acc@5 {top5.global_avg:.3f} loss {losses.global_avg:.3f}'
          .format(top1=metric_logger.acc1, top5=metric_logger.acc5, losses=metric_logger.loss))
    y_Prob_max, _ = torch.max(y_Prob, dim=1)

    num_cls = args.nb_classes
    # Confusion matrix
    target_names = ['Class-%d' % i for i in range(num_cls)]
    conf_matrix = confusion_matrix(y_true, y_pred)
    print('classification report')
    print(classification_report(y_true, y_pred, target_names=target_names))

    metric_macro = MulticlassAUROC(num_classes=num_cls, average="macro", thresholds=None)
    auc_macro = metric_macro(y_Prob, y_true)
    print('macro-avg auc', auc_macro)

    return {k: meter.global_avg for k, meter in metric_logger.meters.items()}, conf_matrix#, filtered_conf_matrix