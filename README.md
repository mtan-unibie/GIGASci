# MAE-ViT-on-diatom-classification

* This repo is a modification on the [MAE repo](https://github.com/facebookresearch/mae). Installation and preparation follow that repo.

# Containerization
* Find the containerized notebook here: [demo](demo).

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
## Fine-tuning Pre-trained MAE and ViT for Classification
### MAE

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
    --log_dir ${OUTPUT_DIR} 
  
```

### ViT

```
python ViT-classification.py \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16_224 \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR} \
    --log_dir ${OUTPUT_DIR}
  
```
## Evaluation checkpoints of MAE and ViT for Classification
### MAE

```
python main_finetune.py \
    --eval \
    --resume ${CHECKPOINTS_DIR} \
    --data_path ${DATA_DIR} \
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16 
```

### ViT

```
python ViT-classification.py \
    --eval \
    --resume ${CHECKPOINTS_DIR} \
    --data_path ${DATA_DIR} \ 
    --nb_classes 144 \
    --batch_size 16 \
    --model vit_large_patch16_224 
```
### License

This project is under the MIT license. See [LICENSE](LICENSE) for details.

