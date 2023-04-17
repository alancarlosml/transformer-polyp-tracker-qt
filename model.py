import cv2
import time
import torch
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
import torchvision.transforms as T

from global_vars import GlobalVars
from general import rescale_bboxes

global_vars = GlobalVars.get_instance() 

CLASSES = [
    'N/A', 'polyp'
]

COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0)]

transform = T.Compose([
    T.Resize(800),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def load_model():
    if global_vars.weights_path:
        model = torch.hub.load('facebookresearch/detr', 'detr_resnet50', pretrained=False, num_classes=len(CLASSES))
        checkpoint = torch.load(global_vars.weights_path, map_location='cpu')
        model.load_state_dict(checkpoint['model'])
        model.eval()

        return model
    return None

def filter_bboxes_from_outputs(im, outputs, threshold=0.7):
  
    probas = outputs['pred_logits'].softmax(-1)[0, :, :-1]
    keep = probas.max(-1).values > threshold

    probas_to_keep = probas[keep]

    bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], im.size)

    return probas_to_keep, bboxes_scaled

def process_frame(model, frame):
            
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    input_tensor = transform(im).unsqueeze(0)
    
    start_time = time.time()
    outputs = model(input_tensor)
    end_time = time.time()
    frame_time = (end_time - start_time) * 1000  
    probas, bboxes = filter_bboxes_from_outputs(im, outputs, threshold=global_vars.threshold)

    im = draw_frame(im, probas, bboxes)

    return np.array(im), frame_time

def process_activation_map(model, frame):
    
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    input_tensor = transform(im).unsqueeze(0)
    
    original_h, original_w  = im.size[0], im.size[1]

    outputs = model(input_tensor)

    probas = outputs['pred_logits'].softmax(-1)[0, :, :-1]
    keep = probas.max(-1).values > global_vars.threshold

    bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], im.size)

    conv_features, enc_attn_weights, dec_attn_weights = [], [], []

    hooks = [
        model.backbone[-2].register_forward_hook(
            lambda self, input, output: conv_features.append(output)
        ),
        model.transformer.encoder.layers[-1].self_attn.register_forward_hook(
            lambda self, input, output: enc_attn_weights.append(output[1])
        ),
        model.transformer.decoder.layers[-1].multihead_attn.register_forward_hook(
            lambda self, input, output: dec_attn_weights.append(output[1])
        ),
    ]

    outputs = model(input_tensor)

    for hook in hooks:
        hook.remove()

    conv_features = conv_features[0]
    enc_attn_weights = enc_attn_weights[0]
    dec_attn_weights = dec_attn_weights[0]	

    h, w = conv_features['0'].tensors.shape[-2:]

    fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(original_h/100, original_w/100), squeeze=False)
    axs = axs.flatten()
    for idx, ax_i, (xmin, ymin, xmax, ymax) in zip(keep.nonzero(), axs.T, bboxes_scaled):
        ax = ax_i
        ax.imshow(dec_attn_weights[0, idx].view(h, w).detach().numpy())
        ax.axis('off')
        ax.set_title(None)
    plt.close()

    for ax in axs[len(bboxes_scaled):]:
        ax.axis('off')

    fig.tight_layout()
    
    fig.canvas.draw()
    plot_image = np.array(fig.canvas.renderer.buffer_rgba())

    opencv_image = cv2.cvtColor(plot_image, cv2.COLOR_RGBA2BGR)

    return opencv_image

def draw_frame(im, probas, bboxes):
    draw = ImageDraw.Draw(im)
    colors = COLORS[:len(probas)]
    if probas is not None and bboxes is not None:
        for p, (xmin, ymin, xmax, ymax), c in zip(probas, bboxes.tolist(), colors):
            draw.rectangle(((xmin, ymin), (xmax, ymax)), outline=c, width=2)
            cl = p.argmax()
            text = f'{CLASSES[cl]}: {p[cl]:0.2f}'
            font = ImageFont.truetype(r'/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', 20)
            draw.text((xmin, ymin-25), text=text, font=font, fill=c)
    return im