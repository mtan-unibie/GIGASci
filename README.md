# MAE-ViT-on-diatom-classification

* This repo is a modification on the [MAE repo](https://github.com/facebookresearch/mae).
  
## Containerization
* Find the containerized notebook including installation and preparation details here: [demo](demo.ipynb).

## Dataset

The dataset is arranged such that each class has a directory with the corresponding images placed in them. An example directory structure is shown below.

```bash
├── dataset
│   ├── train
│   │   ├── class1
│   │   ├── class2
...
│   │   ├── classN
│   ├── val
│   │   ├── class1
│   │   ├── class2
...
│   │   ├── classN

```
## Fine-tuning
* Fine-tuning ImageNet pre-trained [model](https://dl.fbaipublicfiles.com/mae/pretrain/mae_pretrain_vit_large.pth) provided by MAE repo.
#### ResNet
```
python Convnet-classification.py \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model resnet50 \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR} \
    --log_dir ${OUTPUT_DIR} \
    --device cuda
```
#### ViT
```
python ViT-classification.py \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16_224 \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR} \
    --log_dir ${OUTPUT_DIR} \
    --device cuda
```
#### MAE
```
python main_finetune.py \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16 \
    --finetune mae_pretrain_vit_large.pth \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR} \
    --log_dir ${OUTPUT_DIR} \
    --device cuda
```

## Evaluation
* Run evaluation using fine-tuned checkpoints.
#### ResNet
```
python Convnet-classification.py \
    --eval \
    --model resnet50 \
    --resume ${CHECKPOINTS_DIR} \
    --data_path ${DATA_DIR} \ 
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16_224 \
    --device cuda 
```
#### ViT
```
python ViT-classification.py \
    --eval \
    --model vit_large_patch16_224 \
    --resume ${CHECKPOINTS_DIR} \
    --data_path ${DATA_DIR} \ 
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16_224 \
    --device cuda 
```
#### MAE

```
python main_finetune.py \
    --eval \
    --model vit_large_patch16 \
    --resume ${CHECKPOINTS_DIR} \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16 \
    --device cuda 
```

### License
This project is under the MIT license. See [LICENSE](LICENSE) for details.

