# MAE-ViT-on-diatom-classification


## Dataset

The dataset is arranged such that each class has a directory with the corresponding images placed in them. An example directory structure is shown below.

```bash
├── dataset
│   ├── train_data
│   │   ├── class1
│   │   ├── class2
...
│   │   ├── classN
│   ├── test_data
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
    --nb_classes 144
    --nodes 4 \
    --batch_size 16 \
    --model vit_large_patch16 \
    --finetune mae_pretrain_vit_large.pth \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR}
    --log_dir ${OUTPUT_DIR}
  
```

### ViT

```
python ViT-classification.py \
    --data_path ${DATA_DIR} \
    --nb_classes 144
    --nodes 4 \
    --batch_size 16 \
    --model vit_large_patch16_224 \
    --epochs 100 \
    --device cuda \
    --output_dir ${OUTPUT_DIR}
    --log_dir ${OUTPUT_DIR}
  
```
