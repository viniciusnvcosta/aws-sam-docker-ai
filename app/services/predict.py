import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from core.config import settings
from core.errors import ModelLoadException
from fastapi import HTTPException
from loguru import logger


class MachineLearningModelHandlerScore(object):
    model = None
    image_transforms = torchvision.transforms.Compose(
        [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )

    @classmethod
    def predict(cls, input_image):
        # Ensure the model is loaded
        model = cls.get_model()
        if model is None:
            raise ValueError("Model is not loaded")

        # Perform prediction
        try:
            transformed_image = cls.image_transforms(np.array(input_image)).reshape(
                -1, 1, 28, 28
            )
            probabilities = model.forward(transformed_image)
            label = torch.argmax(probabilities).item()
            return label
        except Exception as e:
            raise RuntimeError(f"Error during prediction: {str(e)}")

    @classmethod
    def get_model(cls):
        if cls.model is None:
            try:
                path = f"{settings.MODEL_PATH}{settings.MODEL_NAME}"
                cls.model = Net()
                cls.model.load_state_dict(torch.load(path))
                cls.model.eval()
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {str(e)}")
        return cls.model


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, kernel_size=5)
        self.conv2 = nn.Conv2d(20, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()

        self.fc1 = nn.Linear(320, 100)
        self.bn1 = nn.BatchNorm1d(100)

        self.fc2 = nn.Linear(100, 100)
        self.bn2 = nn.BatchNorm1d(100)

        self.smax = nn.Linear(100, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))

        x = x.view(-1, 320)
        x = self.bn1(F.relu(self.fc1(x)))
        x = F.dropout(x, training=self.training)

        x = self.bn2(F.relu(self.fc2(x)))
        x = F.dropout(x, training=self.training)

        return F.softmax(self.smax(x), dim=-1)
